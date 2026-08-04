import Foundation
import Capacitor
import WidgetKit

/// Writes a JSON snapshot into the App Group so WidgetKit can render Harbor at a glance.
/// Dual-write: UserDefaults suite + shared container file (file survives App Group edge cases).
@objc(HarborWidgetsPlugin)
public class HarborWidgetsPlugin: CAPPlugin, CAPBridgedPlugin {
    public let identifier = "HarborWidgetsPlugin"
    public let jsName = "HarborWidgets"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "updateSnapshot", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "reload", returnType: CAPPluginReturnPromise)
    ]

    static let appGroupId = "group.com.sandetay.harbor"
    static let snapshotKey = "harborWidgetSnapshot"
    static let snapshotFileName = "harbor-widget-snapshot.json"

    @objc func updateSnapshot(_ call: CAPPluginCall) {
        // Accept string or object — Capacitor sometimes deserializes JSON
        var json: String?
        if let s = call.getString("json"), !s.isEmpty {
            json = s
        } else if let obj = call.getObject("json") {
            if let data = try? JSONSerialization.data(withJSONObject: obj, options: []),
               let s = String(data: data, encoding: .utf8) {
                json = s
            }
        } else if let raw = call.options["json"] as? String, !raw.isEmpty {
            json = raw
        } else if let nested = call.getObject("snapshot") {
            // Alternate key some bridges use
            if let data = try? JSONSerialization.data(withJSONObject: nested, options: []),
               let s = String(data: data, encoding: .utf8) {
                json = s
            }
        }

        guard let json = json, !json.isEmpty else {
            call.reject("Missing json")
            return
        }

        // Validate JSON so we never store garbage that breaks WidgetKit decode
        guard let data = json.data(using: .utf8),
              (try? JSONSerialization.jsonObject(with: data)) != nil else {
            call.reject("Invalid json")
            return
        }

        var wroteDefaults = false
        var wroteFile = false
        var groupURL: String?

        // 1) App Group UserDefaults
        if let defaults = UserDefaults(suiteName: Self.appGroupId) {
            defaults.set(json, forKey: Self.snapshotKey)
            defaults.set(Date().timeIntervalSince1970, forKey: "harborWidgetUpdatedAt")
            defaults.synchronize()
            wroteDefaults = true
        }

        // 2) Shared container file (more reliable for some WidgetKit configs)
        if let dir = FileManager.default.containerURL(forSecurityApplicationGroupIdentifier: Self.appGroupId) {
            groupURL = dir.path
            let url = dir.appendingPathComponent(Self.snapshotFileName)
            do {
                try data.write(to: url, options: .atomic)
                wroteFile = true
            } catch {
                // keep going if defaults worked
            }
        }

        guard wroteDefaults || wroteFile else {
            call.reject("App Group unavailable — enable group.com.sandetay.harbor in Apple Developer for both App and Widgets")
            return
        }

        Self.reloadTimelines()
        call.resolve([
            "ok": true,
            "bytes": json.utf8.count,
            "defaults": wroteDefaults,
            "file": wroteFile,
            "groupPath": groupURL as Any
        ])
    }

    @objc func reload(_ call: CAPPluginCall) {
        Self.reloadTimelines()
        call.resolve(["ok": true])
    }

    static func reloadTimelines() {
        if #available(iOS 14.0, *) {
            WidgetCenter.shared.reloadAllTimelines()
        }
    }
}
