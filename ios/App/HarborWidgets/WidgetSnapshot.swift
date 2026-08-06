import Foundation
import WidgetKit
import EventKit

/// Shared App Group + decoded snapshot produced by the web app via HarborWidgetsPlugin.
enum HarborWidgetStore {
    static let appGroupId = "group.com.sandetay.harbor"
    static let snapshotKey = "harborWidgetSnapshot"
    static let snapshotFileName = "harbor-widget-snapshot.json"

    static func load() -> HarborWidgetSnapshot {
        if let dir = FileManager.default.containerURL(forSecurityApplicationGroupIdentifier: appGroupId) {
            let url = dir.appendingPathComponent(snapshotFileName)
            if let data = try? Data(contentsOf: url),
               let snap = decode(data) {
                return snap
            }
        }
        if let defaults = UserDefaults(suiteName: appGroupId),
           let json = defaults.string(forKey: snapshotKey),
           let data = json.data(using: .utf8),
           let snap = decode(data) {
            return snap
        }
        return .placeholder
    }

    private static func decode(_ data: Data) -> HarborWidgetSnapshot? {
        let decoder = JSONDecoder()
        if let snap = try? decoder.decode(HarborWidgetSnapshot.self, from: data) {
            return snap
        }
        guard let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            return nil
        }
        return HarborWidgetSnapshot(
            updatedAt: obj["updatedAt"] as? String,
            greeting: obj["greeting"] as? String,
            dayShape: obj["dayShape"] as? String,
            freeLabel: obj["freeLabel"] as? String,
            freeNowMins: intValue(obj["freeNowMins"]),
            tasksOpen: intValue(obj["tasksOpen"]),
            tasks: (obj["tasks"] as? [[String: Any]])?.map { t in
                HarborWidgetTask(
                    id: t["id"] as? String ?? (t["id"] as? NSNumber)?.stringValue,
                    title: t["title"] as? String,
                    mins: intValue(t["mins"])
                )
            },
            nextEvent: eventFrom(obj["nextEvent"] as Any?),
            events: (obj["events"] as? [[String: Any]])?.compactMap { eventFrom($0) },
            streakBest: intValue(obj["streakBest"]),
            streakActive: intValue(obj["streakActive"]),
            streakLabel: obj["streakLabel"] as? String,
            morningRitualDue: obj["morningRitualDue"] as? Bool,
            eveningRitualDue: obj["eveningRitualDue"] as? Bool,
            morningProgress: obj["morningProgress"] as? String,
            eveningProgress: obj["eveningProgress"] as? String,
            ritualHint: obj["ritualHint"] as? String,
            groceryOpen: intValue(obj["groceryOpen"]),
            billsDue: intValue(obj["billsDue"]),
            energy: obj["energy"] as? String
        )
    }

    private static func intValue(_ any: Any?) -> Int? {
        if let i = any as? Int { return i }
        if let n = any as? NSNumber { return n.intValue }
        if let d = any as? Double { return Int(d) }
        if let s = any as? String, let i = Int(s) { return i }
        return nil
    }

    private static func eventFrom(_ any: Any?) -> HarborWidgetEvent? {
        guard let e = any as? [String: Any] else { return nil }
        return HarborWidgetEvent(
            title: e["title"] as? String,
            time: e["time"] as? String,
            startMins: intValue(e["startMins"]),
            endMins: intValue(e["endMins"]),
            minsUntil: intValue(e["minsUntil"]),
            who: e["who"] as? String
        )
    }
}

struct HarborWidgetSnapshot: Codable {
    var updatedAt: String?
    var greeting: String?
    var dayShape: String?
    var freeLabel: String?
    var freeNowMins: Int?
    var tasksOpen: Int?
    var tasks: [HarborWidgetTask]?
    var nextEvent: HarborWidgetEvent?
    var events: [HarborWidgetEvent]?
    var streakBest: Int?
    var streakActive: Int?
    var streakLabel: String?
    var morningRitualDue: Bool?
    var eveningRitualDue: Bool?
    var morningProgress: String?
    var eveningProgress: String?
    var ritualHint: String?
    var groceryOpen: Int?
    var billsDue: Int?
    var energy: String?

    static let placeholder = HarborWidgetSnapshot(
        updatedAt: nil,
        greeting: "Harbor",
        dayShape: nil,
        freeLabel: nil,
        freeNowMins: nil,
        tasksOpen: 0,
        tasks: [],
        nextEvent: nil,
        events: [],
        streakBest: 0,
        streakActive: 0,
        streakLabel: nil,
        morningRitualDue: false,
        eveningRitualDue: false,
        morningProgress: nil,
        eveningProgress: nil,
        ritualHint: nil,
        groceryOpen: 0,
        billsDue: 0,
        energy: nil
    )

    var hasLiveData: Bool {
        if let u = updatedAt, !u.isEmpty { return true }
        if (tasksOpen ?? 0) > 0 { return true }
        if !(tasks ?? []).isEmpty { return true }
        if nextEvent?.title != nil { return true }
        if (groceryOpen ?? 0) > 0 { return true }
        if (billsDue ?? 0) > 0 { return true }
        if (streakActive ?? 0) > 0 { return true }
        return false
    }
}

struct HarborWidgetTask: Codable, Hashable {
    var id: String?
    var title: String?
    var mins: Int?

    var displayTitle: String {
        (title?.trimmingCharacters(in: .whitespacesAndNewlines))
            .flatMap { $0.isEmpty ? nil : $0 } ?? "Task"
    }
}

struct HarborWidgetEvent: Codable, Hashable {
    var title: String?
    var time: String?
    /// Minutes from midnight (local) when the event starts.
    var startMins: Int?
    /// Minutes from midnight when the event ends (optional; defaults to start + 45).
    var endMins: Int?
    var minsUntil: Int?
    var who: String?

    var displayTitle: String {
        (title?.trimmingCharacters(in: .whitespacesAndNewlines))
            .flatMap { $0.isEmpty ? nil : $0 } ?? "Event"
    }

    var resolvedEndMins: Int {
        if let e = endMins, e > 0 { return e }
        if let s = startMins { return s + 45 }
        return 0
    }

    /// Minutes until start. Negative means already started (or past).
    func liveMinsUntil(at date: Date = Date()) -> Int? {
        if let start = startMins, start >= 0, start < 24 * 60 + 180 {
            let cal = Calendar.current
            let nowMins = cal.component(.hour, from: date) * 60 + cal.component(.minute, from: date)
            return start - nowMins
        }
        if let parsed = Self.parseClockToMins(time) {
            let cal = Calendar.current
            let nowMins = cal.component(.hour, from: date) * 60 + cal.component(.minute, from: date)
            return parsed - nowMins
        }
        return minsUntil
    }

    /// True while the event is still relevant (not finished).
    func isStillRelevant(at date: Date = Date()) -> Bool {
        let cal = Calendar.current
        let nowMins = cal.component(.hour, from: date) * 60 + cal.component(.minute, from: date)
        if let start = startMins {
            let end = resolvedEndMins > start ? resolvedEndMins : start + 45
            return end > nowMins
        }
        if let until = liveMinsUntil(at: date) {
            // Keep showing from 30 min before start through ~45 min after start if no end
            return until > -45
        }
        return true
    }

    func isUpcoming(at date: Date = Date()) -> Bool {
        guard let until = liveMinsUntil(at: date) else { return isStillRelevant(at: date) }
        return until >= 0
    }

    private static func parseClockToMins(_ s: String?) -> Int? {
        guard var t = s?.trimmingCharacters(in: .whitespacesAndNewlines), !t.isEmpty else { return nil }
        let upper = t.uppercased()
        let isPM = upper.contains("PM")
        let isAM = upper.contains("AM")
        t = t.replacingOccurrences(of: #"[AaPp]\.?[Mm]\.?"#, with: "", options: .regularExpression)
            .trimmingCharacters(in: .whitespacesAndNewlines)

        // "0900" / "1430" military compact
        if t.count == 3 || t.count == 4, t.allSatisfy(\.isNumber), !t.contains(":") {
            let padded = t.count == 3 ? "0" + t : t
            if let h = Int(padded.prefix(2)), let m = Int(padded.suffix(2)),
               h >= 0, h < 24, m >= 0, m < 60 {
                return h * 60 + m
            }
        }

        let parts = t.split(separator: ":")
        guard let hPart = parts.first, let h = Int(hPart) else { return nil }
        let m = parts.count > 1 ? Int(parts[1].filter(\.isNumber)) ?? 0 : 0
        var hour = h
        if isPM && hour < 12 { hour += 12 }
        if isAM && hour == 12 { hour = 0 }
        guard hour >= 0, hour < 24, m >= 0, m < 60 else { return nil }
        return hour * 60 + m
    }
}

struct HarborEntry: TimelineEntry {
    let date: Date
    let snapshot: HarborWidgetSnapshot
}

// MARK: - Live EventKit (refresh calendars without opening the app)

/// Reads remaining today events from device calendars when permission was granted in Harbor.
enum HarborWidgetCalendar {
    private static let store = EKEventStore()

    static func remainingEventsToday(limit: Int = 4) -> [HarborWidgetEvent] {
        let status = EKEventStore.authorizationStatus(for: .event)
        let allowed: Bool
        if #available(iOS 17.0, *) {
            allowed = (status == .fullAccess || status == .authorized)
        } else {
            allowed = (status == .authorized)
        }
        guard allowed else { return [] }

        let cal = Calendar.current
        let now = Date()
        guard let dayStart = cal.date(bySettingHour: 0, minute: 0, second: 0, of: now),
              let dayEnd = cal.date(byAdding: .day, value: 1, to: dayStart) else {
            return []
        }

        let predicate = store.predicateForEvents(withStart: dayStart, end: dayEnd, calendars: nil)
        let events = store.events(matching: predicate)
            .filter { !$0.isAllDay }
            .sorted { $0.startDate < $1.startDate }

        var out: [HarborWidgetEvent] = []
        for e in events {
            if e.endDate <= now { continue }
            let startMins = cal.component(.hour, from: e.startDate) * 60
                + cal.component(.minute, from: e.startDate)
            var endMins = cal.component(.hour, from: e.endDate) * 60
                + cal.component(.minute, from: e.endDate)
            if e.endDate >= dayEnd { endMins = 24 * 60 }
            let nowMins = cal.component(.hour, from: now) * 60 + cal.component(.minute, from: now)
            let title = (e.title ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
            out.append(HarborWidgetEvent(
                title: title.isEmpty ? "Event" : title,
                time: formatTime(e.startDate),
                startMins: startMins,
                endMins: endMins,
                minsUntil: startMins - nowMins,
                who: e.location
            ))
            if out.count >= limit { break }
        }
        return out
    }

    private static func formatTime(_ date: Date) -> String {
        let f = DateFormatter()
        f.locale = .current
        f.timeStyle = .short
        f.dateStyle = .none
        return f.string(from: date)
    }

    /// Prefer live EventKit when available; always drop finished events via wall clock.
    static func enrich(_ snap: HarborWidgetSnapshot) -> HarborWidgetSnapshot {
        let live = remainingEventsToday(limit: 4)
        guard !live.isEmpty else {
            return snap.withLiveCountdowns(at: Date())
        }
        var copy = snap
        copy.events = live
        copy.nextEvent = live.first
        return copy.withLiveCountdowns(at: Date())
    }
}
