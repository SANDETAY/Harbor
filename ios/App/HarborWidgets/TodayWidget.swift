import WidgetKit
import SwiftUI

/// Daily Brief — main Harbor widget. Small / Medium / Large.
struct HarborTodayWidget: Widget {
    let kind = "HarborTodayWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: HarborProvider()) { entry in
            TodayWidgetView(entry: entry)
                .harborWidgetChrome(entry.snapshot.palette)
                .widgetURL(HarborWidgetLink.today)
        }
        .configurationDisplayName("Today")
        .description("Greeting, next tasks for your energy, and one smart line. Tap to open Today.")
        .supportedFamilies([.systemSmall, .systemMedium, .systemLarge])
        .contentMarginsDisabled()
    }
}

struct TodayWidgetView: View {
    var entry: HarborEntry
    @Environment(\.widgetFamily) var family

    var body: some View {
        let snap = entry.snapshot
        let pal = snap.palette
        let status = (snap.statusLine?.isEmpty == false)
            ? snap.statusLine!
            : defaultStatus(snap)
        let next = (snap.nextAction?.isEmpty == false)
            ? snap.nextAction!
            : (snap.tasks?.first?.displayTitle ?? "All clear")
        let greet = (snap.greeting?.isEmpty == false) ? snap.greeting! : "Today"
        let limit = family == .systemLarge ? 5 : 3
        let tasks = Array((snap.tasks ?? []).prefix(limit))
        let smart = firstSmartLine(snap)

        VStack(alignment: .leading, spacing: family == .systemSmall ? 6 : 7) {
            Text("TODAY")
                .font(.system(size: 10, weight: .bold, design: .rounded))
                .foregroundStyle(pal.accent)
                .tracking(0.7)

            if family == .systemSmall {
                Text(next)
                    .font(.system(size: 16, weight: .bold))
                    .foregroundStyle(pal.text)
                    .lineLimit(2)
                    .minimumScaleFactor(0.8)
                Text(status)
                    .font(.system(size: 12, weight: .medium))
                    .foregroundStyle(pal.muted)
                    .lineLimit(2)
                Spacer(minLength: 0)
            } else {
                Text(greet)
                    .font(.system(size: family == .systemLarge ? 20 : 17, weight: .bold))
                    .foregroundStyle(pal.text)
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
                Text(status)
                    .font(.system(size: 12, weight: .medium))
                    .foregroundStyle(pal.muted)
                    .lineLimit(1)

                if tasks.isEmpty {
                    Spacer(minLength: 4)
                    HarborEmptyLine(text: "All clear", color: pal.muted)
                    Spacer(minLength: 0)
                } else {
                    VStack(alignment: .leading, spacing: family == .systemLarge ? 7 : 6) {
                        ForEach(Array(tasks.enumerated()), id: \.offset) { _, t in
                            HStack(spacing: 8) {
                                Circle()
                                    .strokeBorder(pal.accent.opacity(0.7), lineWidth: 1.5)
                                    .frame(width: 11, height: 11)
                                Text(t.displayTitle)
                                    .font(.system(size: HarborWidgetTheme.bodySize(for: family), weight: .medium))
                                    .foregroundStyle(pal.text)
                                    .lineLimit(1)
                                    .minimumScaleFactor(0.85)
                                Spacer(minLength: 0)
                                if let m = t.mins, m > 0 {
                                    Text("\(m)m")
                                        .font(.system(size: 11, weight: .semibold, design: .rounded))
                                        .foregroundStyle(pal.muted)
                                        .monospacedDigit()
                                }
                            }
                        }
                    }
                    Spacer(minLength: 0)
                    if let smart {
                        Text(smart)
                            .font(.system(size: 11.5, weight: .semibold))
                            .foregroundStyle(pal.accentDeep)
                            .lineLimit(2)
                            .minimumScaleFactor(0.85)
                    }
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .harborWidgetPadding(family)
    }

    private func defaultStatus(_ snap: HarborWidgetSnapshot) -> String {
        let open = snap.tasksOpen ?? (snap.tasks ?? []).count
        let done = snap.resolvedTasksDone
        if open == 0 { return done > 0 ? "\(done) done · Clear on must-dos" : "All clear" }
        return "\(open) open · \(done) done"
    }

    private func firstSmartLine(_ snap: HarborWidgetSnapshot) -> String? {
        if let m = snap.mealLine, !m.isEmpty { return m }
        if let b = snap.budgetLine, !b.isEmpty { return b }
        return nil
    }
}
