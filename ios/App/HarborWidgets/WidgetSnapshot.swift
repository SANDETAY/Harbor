import Foundation
import WidgetKit

/// Shared App Group + decoded snapshot produced by the web app via HarborWidgetsPlugin.
enum HarborWidgetStore {
    static let appGroupId = "group.com.sandetay.harbor"
    static let snapshotKey = "harborWidgetSnapshot"
    static let snapshotFileName = "harbor-widget-snapshot.json"

    static func load() -> HarborWidgetSnapshot {
        // Prefer file (atomic write), fall back to UserDefaults
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

    /// Lenient decode: ignore unknown keys, tolerate minor type drift from JS.
    private static func decode(_ data: Data) -> HarborWidgetSnapshot? {
        let decoder = JSONDecoder()
        if let snap = try? decoder.decode(HarborWidgetSnapshot.self, from: data) {
            return snap
        }
        // Fallback: rebuild from NSDictionary (numbers sometimes arrive as Double)
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

    /// True when we have real app data (not the never-opened placeholder).
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

    var displayTitle: String { (title?.trimmingCharacters(in: .whitespacesAndNewlines)).flatMap { $0.isEmpty ? nil : $0 } ?? "Task" }
}

struct HarborWidgetEvent: Codable, Hashable {
    var title: String?
    var time: String?
    /// Minutes from midnight (local) when the event starts — used to recompute live countdowns.
    var startMins: Int?
    var minsUntil: Int?
    var who: String?

    var displayTitle: String { (title?.trimmingCharacters(in: .whitespacesAndNewlines)).flatMap { $0.isEmpty ? nil : $0 } ?? "Event" }

    /// Fresh “minutes until start” based on wall clock (falls back to stored minsUntil).
    func liveMinsUntil(at date: Date = Date()) -> Int? {
        if let start = startMins, start >= 0, start < 24 * 60 {
            let cal = Calendar.current
            let nowMins = cal.component(.hour, from: date) * 60 + cal.component(.minute, from: date)
            return max(0, start - nowMins)
        }
        // Parse display time strings like "2:30 PM" if startMins missing
        if let parsed = Self.parseClockToMins(time) {
            let cal = Calendar.current
            let nowMins = cal.component(.hour, from: date) * 60 + cal.component(.minute, from: date)
            return max(0, parsed - nowMins)
        }
        return minsUntil
    }

    private static func parseClockToMins(_ s: String?) -> Int? {
        guard var t = s?.trimmingCharacters(in: .whitespacesAndNewlines), !t.isEmpty else { return nil }
        let upper = t.uppercased()
        let isPM = upper.contains("PM")
        let isAM = upper.contains("AM")
        t = t.replacingOccurrences(of: #"[AaPp]\.?[Mm]\.?"#, with: "", options: .regularExpression)
            .trimmingCharacters(in: .whitespacesAndNewlines)
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
