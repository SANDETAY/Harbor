import Foundation
import Capacitor
import AVFoundation
import Speech

/// Native speech-to-text for iOS Capacitor.
/// WKWebView does not reliably expose Web Speech / request mic permission, so Settings
/// never shows Harbor under Microphone unless we use AVAudioSession + SFSpeechRecognizer.
@objc(HarborSpeechPlugin)
public class HarborSpeechPlugin: CAPPlugin, CAPBridgedPlugin {
    public let identifier = "HarborSpeechPlugin"
    public let jsName = "HarborSpeech"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "isAvailable", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "requestPermission", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "start", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "stop", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "cancel", returnType: CAPPluginReturnPromise)
    ]

    private let speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
    private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    private var recognitionTask: SFSpeechRecognitionTask?
    private let audioEngine = AVAudioEngine()
    private var latestTranscript = ""
    private var isListening = false
    private let lock = NSLock()

    @objc func isAvailable(_ call: CAPPluginCall) {
        let speechAuth = SFSpeechRecognizer.authorizationStatus()
        let micGranted: Bool
        if #available(iOS 17.0, *) {
            micGranted = AVAudioApplication.shared.recordPermission == .granted
        } else {
            micGranted = AVAudioSession.sharedInstance().recordPermission == .granted
        }
        call.resolve([
            "available": speechRecognizer != nil && (speechRecognizer?.isAvailable ?? false),
            "speechAuthorized": speechAuth == .authorized,
            "microphoneAuthorized": micGranted,
            "platform": "ios"
        ])
    }

    @objc func requestPermission(_ call: CAPPluginCall) {
        requestSpeechAndMic { speechOk, micOk, err in
            if let err = err {
                call.reject(err)
                return
            }
            call.resolve([
                "speech": speechOk,
                "microphone": micOk,
                "granted": speechOk && micOk
            ])
        }
    }

    @objc func start(_ call: CAPPluginCall) {
        lock.lock()
        let already = isListening
        lock.unlock()
        if already {
            call.resolve(["started": true, "already": true])
            return
        }

        let go: () -> Void = { [weak self] in
            guard let self = self else { return }
            do {
                try self.beginListening()
                call.resolve(["started": true])
            } catch {
                call.reject("Could not start listening: \(error.localizedDescription)")
            }
        }

        if hasSpeechAndMicAuth() {
            go()
            return
        }

        requestSpeechAndMic { [weak self] speechOk, micOk, err in
            guard self != nil else { return }
            if let err = err {
                call.reject(err)
                return
            }
            guard speechOk, micOk else {
                call.reject("Microphone or speech recognition permission denied")
                return
            }
            go()
        }
    }

    @objc func stop(_ call: CAPPluginCall) {
        recognitionRequest?.endAudio()
        // Partials are already stored — don't wait a long flush
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.08) { [weak self] in
            let text = self?.endListening(cancel: false) ?? ""
            call.resolve(["transcript": text, "cancelled": false])
        }
    }

    @objc func cancel(_ call: CAPPluginCall) {
        _ = endListening(cancel: true)
        call.resolve(["transcript": "", "cancelled": true])
    }

    // MARK: - Permissions

    private func hasSpeechAndMicAuth() -> Bool {
        let speechOk = SFSpeechRecognizer.authorizationStatus() == .authorized
        let micOk: Bool
        if #available(iOS 17.0, *) {
            micOk = AVAudioApplication.shared.recordPermission == .granted
        } else {
            micOk = AVAudioSession.sharedInstance().recordPermission == .granted
        }
        return speechOk && micOk
    }

    private func requestSpeechAndMic(completion: @escaping (Bool, Bool, String?) -> Void) {
        SFSpeechRecognizer.requestAuthorization { status in
            let speechOk = (status == .authorized)
            guard speechOk else {
                let msg: String
                switch status {
                case .denied: msg = "Speech recognition denied — enable in Settings → Harbor"
                case .restricted: msg = "Speech recognition restricted on this device"
                case .notDetermined: msg = "Speech recognition not determined"
                default: msg = "Speech recognition unavailable"
                }
                DispatchQueue.main.async { completion(false, false, msg) }
                return
            }

            let finishMic: (Bool) -> Void = { micOk in
                DispatchQueue.main.async {
                    if !micOk {
                        completion(true, false, "Microphone denied — enable in Settings → Harbor → Microphone")
                    } else {
                        completion(true, true, nil)
                    }
                }
            }

            if #available(iOS 17.0, *) {
                AVAudioApplication.requestRecordPermission { granted in
                    finishMic(granted)
                }
            } else {
                AVAudioSession.sharedInstance().requestRecordPermission { granted in
                    finishMic(granted)
                }
            }
        }
    }

    // MARK: - Engine

    private func beginListening() throws {
        guard let speechRecognizer = speechRecognizer, speechRecognizer.isAvailable else {
            throw NSError(domain: "HarborSpeech", code: 1, userInfo: [
                NSLocalizedDescriptionKey: "Speech recognition not available right now"
            ])
        }

        // Tear down any prior task
        _ = endListening(cancel: true)

        let session = AVAudioSession.sharedInstance()
        try session.setCategory(.record, mode: .measurement, options: [.duckOthers, .allowBluetoothHFP])
        try session.setActive(true, options: .notifyOthersOnDeactivation)

        recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
        guard let recognitionRequest = recognitionRequest else {
            throw NSError(domain: "HarborSpeech", code: 2, userInfo: [
                NSLocalizedDescriptionKey: "Could not create speech request"
            ])
        }
        recognitionRequest.shouldReportPartialResults = true
        if #available(iOS 13, *) {
            recognitionRequest.requiresOnDeviceRecognition = false
        }

        latestTranscript = ""
        let inputNode = audioEngine.inputNode
        let format = inputNode.outputFormat(forBus: 0)
        // Some devices report 0 channels until active — fall back to standard format
        let recordingFormat: AVAudioFormat
        if format.sampleRate > 0 && format.channelCount > 0 {
            recordingFormat = format
        } else if let fallback = AVAudioFormat(standardFormatWithSampleRate: 44100, channels: 1) {
            recordingFormat = fallback
        } else {
            throw NSError(domain: "HarborSpeech", code: 3, userInfo: [
                NSLocalizedDescriptionKey: "No usable microphone format"
            ])
        }

        inputNode.removeTap(onBus: 0)
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { [weak self] buffer, _ in
            self?.recognitionRequest?.append(buffer)
        }

        audioEngine.prepare()
        try audioEngine.start()

        lock.lock()
        isListening = true
        lock.unlock()

        recognitionTask = speechRecognizer.recognitionTask(with: recognitionRequest) { [weak self] result, error in
            guard let self = self else { return }
            if let result = result {
                let text = result.bestTranscription.formattedString
                self.lock.lock()
                self.latestTranscript = text
                self.lock.unlock()
                self.notifyListeners("partial", data: [
                    "transcript": text,
                    "isFinal": result.isFinal
                ])
                if result.isFinal {
                    // Keep listening until JS calls stop (push-to-talk); ignore auto-final if continuous
                }
            }
            if let error = error {
                // Ignore cancellation noise
                let ns = error as NSError
                if ns.domain == "kAFAssistantErrorDomain" && (ns.code == 216 || ns.code == 203) {
                    return
                }
                self.notifyListeners("error", data: [
                    "message": error.localizedDescription
                ])
            }
        }
    }

    @discardableResult
    private func endListening(cancel: Bool) -> String {
        lock.lock()
        let text = latestTranscript
        isListening = false
        lock.unlock()

        if audioEngine.isRunning {
            audioEngine.stop()
        }
        audioEngine.inputNode.removeTap(onBus: 0)

        if cancel {
            recognitionRequest?.endAudio()
            recognitionTask?.cancel()
        } else {
            recognitionRequest?.endAudio()
            recognitionTask?.finish()
        }

        recognitionRequest = nil
        recognitionTask = nil

        try? AVAudioSession.sharedInstance().setActive(false, options: .notifyOthersOnDeactivation)

        return text.trimmingCharacters(in: .whitespacesAndNewlines)
    }
}
