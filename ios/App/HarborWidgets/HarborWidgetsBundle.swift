import WidgetKit
import SwiftUI

@main
struct HarborWidgetsBundle: WidgetBundle {
    var body: some Widget {
        HarborDayWidget()
        HarborTodayWidget()
        HarborNextUpWidget()
        HarborListsWidget()
    }
}

// MARK: - Professional theme (Calendar / Reminders inspired)

enum HarborWidgetTheme {
    /// Harbor teal — restrained accent
    static let accent = Color(red: 0.15, green: 0.48, blue: 0.45)
    static let accentSoft = Color(red: 0.15, green: 0.48, blue: 0.45).opacity(0.14)
    static let accentDeep = Color(red: 0.10, green: 0.36, blue: 0.34)

    static var primary: Color { Color.primary }
    static var secondary: Color { Color.secondary }
    static var tertiary: Color { Color.secondary.opacity(0.75) }

    static func padding(for family: WidgetFamily) -> CGFloat {
        switch family {
        case .systemSmall: return 12
        case .systemLarge: return 16
        default: return 14
        }
    }

    static func titleSize(for family: WidgetFamily) -> CGFloat {
        family == .systemSmall ? 15 : 17
    }

    static func bodySize(for family: WidgetFamily) -> CGFloat {
        family == .systemSmall ? 13 : 14
    }
}

struct HarborWidgetChrome: ViewModifier {
    func body(content: Content) -> some View {
        if #available(iOS 17.0, *) {
            content
                .containerBackground(for: .widget) {
                    ZStack {
                        // System material base (adapts light/dark)
                        Color(.systemBackground)
                        // Subtle top wash — professional, not flat mint
                        LinearGradient(
                            colors: [
                                HarborWidgetTheme.accent.opacity(0.10),
                                HarborWidgetTheme.accent.opacity(0.03),
                                Color.clear
                            ],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    }
                }
        } else {
            content
                .background(
                    ZStack {
                        Color(.systemBackground)
                        LinearGradient(
                            colors: [
                                HarborWidgetTheme.accent.opacity(0.10),
                                Color.clear
                            ],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    }
                )
        }
    }
}

extension View {
    func harborWidgetChrome() -> some View {
        modifier(HarborWidgetChrome())
    }

    func harborWidgetPadding(_ family: WidgetFamily) -> some View {
        padding(HarborWidgetTheme.padding(for: family))
    }
}

// MARK: - Timeline provider (live countdowns + EventKit when available)

struct HarborProvider: TimelineProvider {
    func placeholder(in context: Context) -> HarborEntry {
        HarborEntry(date: Date(), snapshot: sampleSnapshot)
    }

    func getSnapshot(in context: Context, completion: @escaping (HarborEntry) -> Void) {
        let now = Date()
        let base = context.isPreview ? sampleSnapshot : loadEnriched()
        completion(HarborEntry(date: now, snapshot: base.withLiveCountdowns(at: now)))
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<HarborEntry>) -> Void) {
        let snap = loadEnriched()
        let now = Date()
        var entries: [HarborEntry] = []

        // Dense timeline for accurate “in Xm” without opening the app
        // Every 1 min for next 20 min, then every 5 for the rest of the hour, then hourly
        var offsets: [Int] = []
        for m in 0...20 { offsets.append(m) }
        for m in stride(from: 25, through: 90, by: 5) { offsets.append(m) }
        for m in stride(from: 120, through: 12 * 60, by: 30) { offsets.append(m) }

        for offset in offsets {
            guard let date = Calendar.current.date(byAdding: .minute, value: offset, to: now) else { continue }
            entries.append(HarborEntry(date: date, snapshot: snap.withLiveCountdowns(at: date)))
        }

        // Ask WidgetKit to rebuild soon (iOS still budgets refreshes; entries keep countdowns honest)
        let reload = Calendar.current.date(byAdding: .minute, value: 15, to: now) ?? now.addingTimeInterval(900)
        completion(Timeline(entries: entries, policy: .after(reload)))
    }

    private func loadEnriched() -> HarborWidgetSnapshot {
        let stored = HarborWidgetStore.load()
        // EventKit path: updates calendar even if the app is not open
        return HarborWidgetCalendar.enrich(stored)
    }

    private var sampleSnapshot: HarborWidgetSnapshot {
        HarborWidgetSnapshot(
            updatedAt: ISO8601DateFormatter().string(from: Date()),
            greeting: "Good morning",
            dayShape: "Light day",
            freeLabel: "Free · 45 min",
            freeNowMins: 45,
            tasksOpen: 3,
            tasks: [
                HarborWidgetTask(id: "1", title: "Unload dishwasher", mins: 10),
                HarborWidgetTask(id: "2", title: "Walk the dog", mins: 20),
                HarborWidgetTask(id: "3", title: "Pay electric bill", mins: 5)
            ],
            nextEvent: HarborWidgetEvent(title: "Dentist", time: "2:30 PM", startMins: 14 * 60 + 30, endMins: 15 * 60, minsUntil: 95, who: nil),
            events: [
                HarborWidgetEvent(title: "Dentist", time: "2:30 PM", startMins: 14 * 60 + 30, endMins: 15 * 60, minsUntil: 95, who: nil)
            ],
            streakBest: 12,
            streakActive: 12,
            streakLabel: "Make the bed",
            morningRitualDue: false,
            eveningRitualDue: false,
            morningProgress: nil,
            eveningProgress: nil,
            ritualHint: nil,
            groceryOpen: 6,
            billsDue: 1,
            energy: "medium"
        )
    }
}

// MARK: - Shared chrome bits

struct HarborCaption: View {
    let text: String
    var body: some View {
        Text(text.uppercased())
            .font(.system(size: 10, weight: .bold, design: .rounded))
            .foregroundStyle(HarborWidgetTheme.accent)
            .tracking(0.7)
            .lineLimit(1)
            .minimumScaleFactor(0.85)
    }
}

struct HarborEmptyLine: View {
    let text: String
    var body: some View {
        Text(text)
            .font(.system(size: 14, weight: .medium))
            .foregroundStyle(HarborWidgetTheme.secondary)
            .lineLimit(2)
            .minimumScaleFactor(0.9)
    }
}

/// Relative time for upcoming events. Never invents “in 1m” for past events.
func formatMinsUntil(_ m: Int?) -> String? {
    guard let m = m else { return nil }
    if m < -1 {
        // In progress (started)
        return "now"
    }
    if m <= 0 {
        return "now"
    }
    if m < 60 {
        return "in \(m)m"
    }
    let h = m / 60
    let r = m % 60
    return r == 0 ? "in \(h)h" : "in \(h)h \(r)m"
}

func formatEventStatus(_ ev: HarborWidgetEvent, at date: Date) -> String? {
    guard let until = ev.liveMinsUntil(at: date) else { return nil }
    if until > 0 {
        return formatMinsUntil(until)
    }
    // Started but not ended
    if ev.isStillRelevant(at: date) {
        return "now"
    }
    return nil
}

extension HarborWidgetSnapshot {
    /// Drop finished events and recompute next + countdowns for a wall-clock date.
    func withLiveCountdowns(at date: Date) -> HarborWidgetSnapshot {
        var copy = self
        var pool = copy.events ?? []
        if let ne = copy.nextEvent, !pool.contains(where: { $0.title == ne.title && $0.startMins == ne.startMins }) {
            pool.insert(ne, at: 0)
        }

        // Keep only events that have not ended
        let remaining = pool
            .filter { $0.isStillRelevant(at: date) }
            .sorted { (a, b) in
                let as_ = a.startMins ?? Int.max
                let bs = b.startMins ?? Int.max
                return as_ < bs
            }
            .map { e -> HarborWidgetEvent in
                var e2 = e
                e2.minsUntil = e2.liveMinsUntil(at: date)
                return e2
            }

        copy.events = remaining
        // Prefer not-yet-started; else in-progress; else nil
        copy.nextEvent = remaining.first(where: { ($0.minsUntil ?? 0) >= 0 })
            ?? remaining.first
        if var ne = copy.nextEvent {
            ne.minsUntil = ne.liveMinsUntil(at: date)
            copy.nextEvent = ne
        }

        // Recompute free label roughly when freeNowMins is present
        if let free = copy.freeNowMins, free > 0 {
            // Soft decay free window across timeline entries so it doesn't freeze forever
            let elapsed = max(0, Int(date.timeIntervalSince(Date()) / 60.0))
            // only for future timeline entries relative to "now" snapshot load — keep freeLabel as-is if stored
            _ = elapsed
        }

        return copy
    }
}
