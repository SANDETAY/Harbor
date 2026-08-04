import WidgetKit
import SwiftUI

@main
struct HarborWidgetsBundle: WidgetBundle {
    var body: some Widget {
        HarborDayWidget()       // hero — calendar + tasks + free time
        HarborTodayWidget()     // task list
        HarborNextUpWidget()    // next calendar event
        HarborListsWidget()     // grocery + bills + streaks counts
    }
}

// MARK: - Apple-quality theme (system materials + restrained accent)

enum HarborWidgetTheme {
    /// Harbor brand accent — used sparingly like Calendar teal
    static let accent = Color(red: 0.18, green: 0.55, blue: 0.50)
    static let accentSoft = Color(red: 0.18, green: 0.55, blue: 0.50).opacity(0.12)

    static var primary: Color { Color.primary }
    static var secondary: Color { Color.secondary }
    static var tertiary: Color { Color.secondary.opacity(0.8) }

    /// Adaptive outer padding — tight so iOS 17 system margins don’t clip on mini/SE
    static func padding(for family: WidgetFamily) -> CGFloat {
        switch family {
        case .systemSmall: return 10
        case .systemLarge: return 14
        default: return 12
        }
    }

    static func titleSize(for family: WidgetFamily) -> CGFloat {
        family == .systemSmall ? 15 : 17
    }

    static func bodySize(for family: WidgetFamily) -> CGFloat {
        family == .systemSmall ? 12.5 : 13.5
    }
}

struct HarborWidgetChrome: ViewModifier {
    func body(content: Content) -> some View {
        if #available(iOS 17.0, *) {
            content
                .containerBackground(for: .widget) {
                    // Apple-style: system surface + restrained Harbor wash (not a flat mint fill)
                    ZStack {
                        Color(.systemBackground)
                        LinearGradient(
                            colors: [
                                HarborWidgetTheme.accent.opacity(0.08),
                                Color.clear,
                                HarborWidgetTheme.accent.opacity(0.03)
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
                                HarborWidgetTheme.accent.opacity(0.08),
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

    /// Safe outer inset — system content margins are disabled on each widget config
    func harborWidgetPadding(_ family: WidgetFamily) -> some View {
        padding(HarborWidgetTheme.padding(for: family))
    }
}





struct HarborProvider: TimelineProvider {
    func placeholder(in context: Context) -> HarborEntry {
        HarborEntry(date: Date(), snapshot: sampleSnapshot)
    }

    func getSnapshot(in context: Context, completion: @escaping (HarborEntry) -> Void) {
        let now = Date()
        let base = context.isPreview ? sampleSnapshot : HarborWidgetStore.load()
        completion(HarborEntry(date: now, snapshot: base.withLiveCountdowns(at: now)))
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<HarborEntry>) -> Void) {
        let snap = HarborWidgetStore.load()
        let now = Date()
        var entries: [HarborEntry] = []
        for offset in stride(from: 0, through: 60, by: 5) {
            let date = Calendar.current.date(byAdding: .minute, value: offset, to: now) ?? now.addingTimeInterval(Double(offset) * 60)
            entries.append(HarborEntry(date: date, snapshot: snap.withLiveCountdowns(at: date)))
        }
        let next = Calendar.current.date(byAdding: .minute, value: 15, to: now) ?? now.addingTimeInterval(900)
        completion(Timeline(entries: entries, policy: .after(next)))
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
            nextEvent: HarborWidgetEvent(title: "Dentist", time: "2:30 PM", startMins: 14 * 60 + 30, minsUntil: 95, who: nil),
            events: [
                HarborWidgetEvent(title: "Dentist", time: "2:30 PM", startMins: 14 * 60 + 30, minsUntil: 95, who: nil)
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

// Shared small bits

struct HarborCaption: View {
    let text: String
    var body: some View {
        Text(text.uppercased())
            .font(.system(size: 11, weight: .semibold, design: .rounded))
            .foregroundStyle(HarborWidgetTheme.accent)
            .tracking(0.5)
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

func formatMinsUntil(_ m: Int?) -> String? {
    guard let m = m, m >= 0, m < 24 * 60 else { return nil }
    if m < 60 { return "in \(max(1, m))m" }
    let h = m / 60
    let r = m % 60
    return r == 0 ? "in \(h)h" : "in \(h)h \(r)m"
}

extension HarborWidgetSnapshot {
    /// Recompute event countdowns for a timeline entry’s wall-clock date.
    func withLiveCountdowns(at date: Date) -> HarborWidgetSnapshot {
        var copy = self
        if var ev = copy.nextEvent {
            ev.minsUntil = ev.liveMinsUntil(at: date)
            copy.nextEvent = ev
        }
        if let events = copy.events {
            copy.events = events.map { e in
                var e2 = e
                e2.minsUntil = e2.liveMinsUntil(at: date)
                return e2
            }
        }
        return copy
    }
}
