import WidgetKit
import SwiftUI

@main
struct HarborWidgetsBundle: WidgetBundle {
    var body: some Widget {
        HarborTodayWidget()      // Tasks
        HarborNextUpWidget()     // Events
        HarborListsWidget()      // Grocery
        HarborDayWidget()        // Budget
    }
}

// MARK: - Harbor Pulse stack theme (mint or night only)

enum HarborWidgetTheme {
    /// Legacy aliases — all faces now use `HarborWidgetPalette` from the app theme.
    static let mint = Color(red: 0.184, green: 0.608, blue: 0.549)       // #2F9B8C
    static let mintDeep = Color(red: 0.110, green: 0.439, blue: 0.400)
    static let accent = mint
    static let accentSoft = mint.opacity(0.14)
    static let accentDeep = mintDeep
    static var primary: Color { Color.primary }
    static var secondary: Color { Color.secondary }

    static func padding(for family: WidgetFamily) -> CGFloat {
        switch family {
        case .systemSmall: return 12
        case .systemLarge: return 16
        default: return 14
        }
    }

    static func bodySize(for family: WidgetFamily) -> CGFloat {
        switch family {
        case .systemSmall: return 12.5
        case .systemLarge: return 14.5
        default: return 13.5
        }
    }

    static func heroSize(for family: WidgetFamily) -> CGFloat {
        switch family {
        case .systemSmall: return 26
        case .systemLarge: return 36
        default: return 30
        }
    }
}

enum HarborWidgetLink {
    static let tasks = URL(string: "com.sandetay.harbor://today")!
    static let events = URL(string: "com.sandetay.harbor://life/schedule")!
    static let grocery = URL(string: "com.sandetay.harbor://life/grocery")!
    static let budget = URL(string: "com.sandetay.harbor://life/budget")!
}

/// App-driven widget look: Harbor mint (default) or Harbor night. No per-face palettes.
struct HarborWidgetPalette {
    let isNight: Bool
    let accent: Color
    let accentDeep: Color
    let bg: Color
    let surface: Color
    let text: Color
    let muted: Color

    static func from(theme: String?) -> HarborWidgetPalette {
        let raw = (theme ?? "harbor").trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        let night = raw == "dark" || raw == "night"
        if night {
            return HarborWidgetPalette(
                isNight: true,
                accent: Color(red: 72 / 255, green: 178 / 255, blue: 162 / 255),
                accentDeep: Color(red: 154 / 255, green: 214 / 255, blue: 202 / 255),
                bg: Color(red: 8 / 255, green: 18 / 255, blue: 16 / 255),
                surface: Color(red: 16 / 255, green: 32 / 255, blue: 29 / 255),
                text: Color(red: 232 / 255, green: 242 / 255, blue: 238 / 255),
                muted: Color(red: 132 / 255, green: 158 / 255, blue: 150 / 255)
            )
        }
        return HarborWidgetPalette(
            isNight: false,
            accent: Color(red: 47 / 255, green: 155 / 255, blue: 140 / 255),
            accentDeep: Color(red: 28 / 255, green: 112 / 255, blue: 102 / 255),
            bg: Color(red: 214 / 255, green: 232 / 255, blue: 226 / 255),
            surface: Color(red: 236 / 255, green: 245 / 255, blue: 241 / 255),
            text: Color(red: 18 / 255, green: 40 / 255, blue: 37 / 255),
            muted: Color(red: 86 / 255, green: 110 / 255, blue: 104 / 255)
        )
    }
}

struct HarborWidgetChrome: ViewModifier {
    var palette: HarborWidgetPalette = .from(theme: "harbor")

    func body(content: Content) -> some View {
        let painted = content.environment(\.colorScheme, palette.isNight ? .dark : .light)
        if #available(iOS 17.0, *) {
            painted
                .containerBackground(for: .widget) {
                    widgetFill
                }
        } else {
            painted.background(widgetFill)
        }
    }

    private var widgetFill: some View {
        ZStack {
            palette.bg
            LinearGradient(
                colors: [
                    palette.surface.opacity(0.95),
                    palette.accent.opacity(palette.isNight ? 0.10 : 0.14),
                    palette.bg
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        }
    }
}

extension View {
    func harborWidgetChrome(_ palette: HarborWidgetPalette) -> some View {
        modifier(HarborWidgetChrome(palette: palette))
    }

    func harborWidgetPadding(_ family: WidgetFamily) -> some View {
        padding(HarborWidgetTheme.padding(for: family))
    }
}

// MARK: - Shared graphic bits

struct HarborMark: View {
    let symbol: String
    let colors: [Color]
    var size: CGFloat = 22

    var body: some View {
        Text(symbol)
            .font(.system(size: size * 0.42, weight: .bold))
            .foregroundStyle(.white)
            .frame(width: size, height: size)
            .background(
                LinearGradient(colors: colors, startPoint: .topLeading, endPoint: .bottomTrailing),
                in: RoundedRectangle(cornerRadius: size * 0.32, style: .continuous)
            )
    }
}

struct HarborCaption: View {
    let text: String
    var color: Color = HarborWidgetTheme.mint

    var body: some View {
        Text(text.uppercased())
            .font(.system(size: 10, weight: .bold, design: .rounded))
            .foregroundStyle(color)
            .tracking(0.7)
            .lineLimit(1)
            .minimumScaleFactor(0.8)
    }
}

struct HarborProgressRing: View {
    var progress: Double
    var color: Color
    var trackOpacity: Double = 0.18
    var lineWidth: CGFloat = 5
    var centerText: String

    var body: some View {
        ZStack {
            Circle()
                .stroke(color.opacity(trackOpacity), lineWidth: lineWidth)
            Circle()
                .trim(from: 0, to: CGFloat(min(1, max(0, progress))))
                .stroke(color, style: StrokeStyle(lineWidth: lineWidth, lineCap: .round))
                .rotationEffect(.degrees(-90))
            Text(centerText)
                .font(.system(size: 12, weight: .bold, design: .rounded))
                .foregroundStyle(HarborWidgetTheme.primary)
                .monospacedDigit()
                .minimumScaleFactor(0.7)
                .lineLimit(1)
        }
    }
}

struct HarborEmptyLine: View {
    let text: String
    var color: Color = HarborWidgetTheme.secondary
    var body: some View {
        Text(text)
            .font(.system(size: 14, weight: .medium))
            .foregroundStyle(color)
            .lineLimit(2)
            .minimumScaleFactor(0.9)
    }
}

/// Upper-right date: bold weekday + complementary month/day.
struct HarborWidgetDateStamp: View {
    var date: Date
    var palette: HarborWidgetPalette
    var compact: Bool = false

    var body: some View {
        let day = Self.weekday.string(from: date).uppercased()
        let md = Self.monthDay.string(from: date)
        if compact {
            VStack(alignment: .trailing, spacing: 0) {
                Text(day)
                    .font(.system(size: 12, weight: .heavy, design: .rounded))
                    .foregroundStyle(palette.text)
                    .lineLimit(1)
                    .minimumScaleFactor(0.7)
                Text(md)
                    .font(.system(size: 10, weight: .semibold, design: .rounded))
                    .foregroundStyle(palette.muted)
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
            }
        } else {
            HStack(alignment: .firstTextBaseline, spacing: 6) {
                Text(day)
                    .font(.system(size: 16, weight: .heavy, design: .rounded))
                    .foregroundStyle(palette.text)
                    .lineLimit(1)
                    .minimumScaleFactor(0.75)
                Text(md)
                    .font(.system(size: 12, weight: .semibold, design: .rounded))
                    .foregroundStyle(palette.muted)
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
            }
        }
    }

    private static let weekday: DateFormatter = {
        let f = DateFormatter()
        f.locale = .current
        f.dateFormat = "EEEE"
        return f
    }()

    private static let monthDay: DateFormatter = {
        let f = DateFormatter()
        f.locale = .current
        f.setLocalizedDateFormatFromTemplate("MMMd")
        return f
    }()
}

/// Relative time for upcoming events.
func formatMinsUntil(_ m: Int?) -> String? {
    guard let m = m else { return nil }
    if m < -1 { return "now" }
    if m <= 0 { return "now" }
    if m < 60 { return "in \(m)m" }
    let h = m / 60
    let r = m % 60
    return r == 0 ? "in \(h)h" : "in \(h)h \(r)m"
}

func formatEventStatus(_ ev: HarborWidgetEvent, at date: Date) -> String? {
    guard let until = ev.liveMinsUntil(at: date) else { return nil }
    if until > 0 { return formatMinsUntil(until) }
    if ev.isStillRelevant(at: date) { return "now" }
    return nil
}

func formatMoney(_ amount: Int) -> String {
    let f = NumberFormatter()
    f.numberStyle = .decimal
    f.maximumFractionDigits = 0
    return "$" + (f.string(from: NSNumber(value: amount)) ?? "\(amount)")
}

// MARK: - Timeline provider

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
        var offsets: [Int] = []
        for m in 0...20 { offsets.append(m) }
        for m in stride(from: 25, through: 90, by: 5) { offsets.append(m) }
        for m in stride(from: 120, through: 12 * 60, by: 30) { offsets.append(m) }

        for offset in offsets {
            guard let date = Calendar.current.date(byAdding: .minute, value: offset, to: now) else { continue }
            entries.append(HarborEntry(date: date, snapshot: snap.withLiveCountdowns(at: date)))
        }

        let reload = Calendar.current.date(byAdding: .minute, value: 15, to: now) ?? now.addingTimeInterval(900)
        completion(Timeline(entries: entries, policy: .after(reload)))
    }

    private func loadEnriched() -> HarborWidgetSnapshot {
        HarborWidgetCalendar.enrich(HarborWidgetStore.load())
    }

    private var sampleSnapshot: HarborWidgetSnapshot {
        HarborWidgetSnapshot(
            updatedAt: ISO8601DateFormatter().string(from: Date()),
            greeting: "Good morning",
            dayShape: "Light day",
            freeLabel: "Free · 45 min",
            freeNowMins: 45,
            tasksOpen: 4,
            tasksDone: 3,
            tasksTotal: 7,
            tasks: [
                HarborWidgetTask(id: "1", title: "Unload dishwasher", mins: 10),
                HarborWidgetTask(id: "2", title: "Walk the dog", mins: 20),
                HarborWidgetTask(id: "3", title: "Pay electric bill", mins: 5),
                HarborWidgetTask(id: "4", title: "Prep dinner", mins: 25)
            ],
            nextEvent: HarborWidgetEvent(title: "Dentist", time: "2:30 PM", startMins: 14 * 60 + 30, endMins: 15 * 60, minsUntil: 95, who: "Oak Dental"),
            events: [
                HarborWidgetEvent(title: "Dentist", time: "2:30 PM", startMins: 14 * 60 + 30, endMins: 15 * 60, minsUntil: 95, who: "Oak Dental"),
                HarborWidgetEvent(title: "School pickup", time: "4:00 PM", startMins: 16 * 60, endMins: 16 * 60 + 20, minsUntil: 185, who: nil),
                HarborWidgetEvent(title: "Team standup", time: "5:15 PM", startMins: 17 * 60 + 15, endMins: 17 * 60 + 45, minsUntil: 260, who: nil)
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
            groceryChecked: 2,
            groceryItems: ["Oat milk", "Spinach", "Chicken", "Coffee", "Eggs", "Bread"],
            billsDue: 1,
            billsDueAmount: 142,
            budgetSpent: 1840,
            budgetLimit: 2800,
            budgetLeft: 960,
            budgetPct: 66,
            energy: "medium",
            theme: "harbor"
        )
    }
}

extension HarborWidgetSnapshot {
    func withLiveCountdowns(at date: Date) -> HarborWidgetSnapshot {
        var copy = self
        var pool = copy.events ?? []
        if let ne = copy.nextEvent, !pool.contains(where: { $0.title == ne.title && $0.startMins == ne.startMins }) {
            pool.insert(ne, at: 0)
        }

        let remaining = pool
            .filter { $0.isStillRelevant(at: date) }
            .sorted { ($0.startMins ?? Int.max) < ($1.startMins ?? Int.max) }
            .map { e -> HarborWidgetEvent in
                var e2 = e
                e2.minsUntil = e2.liveMinsUntil(at: date)
                return e2
            }

        copy.events = remaining
        copy.nextEvent = remaining.first(where: { ($0.minsUntil ?? 0) >= 0 }) ?? remaining.first
        if var ne = copy.nextEvent {
            ne.minsUntil = ne.liveMinsUntil(at: date)
            copy.nextEvent = ne
        }
        return copy
    }
}
