import WidgetKit
import SwiftUI

/// Today tasks — clean list like Apple Reminders.
struct HarborTodayWidget: Widget {
    let kind = "HarborTodayWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: HarborProvider()) { entry in
            TodayWidgetView(entry: entry)
                .harborWidgetChrome()
        }
        .configurationDisplayName("Tasks")
        .description("Open items on Today.")
        .supportedFamilies([.systemSmall, .systemMedium, .systemLarge])
        .contentMarginsDisabled()
    }
}

struct TodayWidgetView: View {
    var entry: HarborEntry
    @Environment(\.widgetFamily) var family

    var body: some View {
        let snap = entry.snapshot
        let limit = family == .systemLarge ? 7 : (family == .systemMedium ? 4 : 3)
        let tasks = Array((snap.tasks ?? []).prefix(limit))
        let open = snap.tasksOpen ?? tasks.count

        VStack(alignment: .leading, spacing: family == .systemSmall ? 6 : 8) {
            HStack(alignment: .firstTextBaseline, spacing: 6) {
                HarborCaption(text: "Today")
                Spacer(minLength: 4)
                Text("\(open)")
                    .font(.system(size: family == .systemSmall ? 18 : 22, weight: .semibold, design: .rounded))
                    .foregroundStyle(HarborWidgetTheme.primary)
                    .monospacedDigit()
                    .minimumScaleFactor(0.8)
                    .lineLimit(1)
            }

            if tasks.isEmpty {
                Spacer(minLength: 0)
                HarborEmptyLine(text: open == 0 ? "All clear" : "Open Harbor")
                Spacer(minLength: 0)
            } else {
                VStack(alignment: .leading, spacing: family == .systemSmall ? 5 : 7) {
                    ForEach(Array(tasks.enumerated()), id: \.offset) { _, t in
                        HStack(alignment: .center, spacing: 8) {
                            Circle()
                                .strokeBorder(HarborWidgetTheme.accent.opacity(0.65), lineWidth: 1.5)
                                .frame(width: 11, height: 11)
                            Text(t.displayTitle)
                                .font(.system(size: HarborWidgetTheme.bodySize(for: family), weight: .medium))
                                .foregroundStyle(HarborWidgetTheme.primary)
                                .lineLimit(1)
                                .minimumScaleFactor(0.85)
                            Spacer(minLength: 0)
                            if let m = t.mins, m > 0, family != .systemSmall {
                                Text("\(m)m")
                                    .font(.system(size: 12, weight: .regular, design: .rounded))
                                    .foregroundStyle(HarborWidgetTheme.secondary)
                                    .monospacedDigit()
                            }
                        }
                    }
                }
                Spacer(minLength: 0)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .harborWidgetPadding(family)
    }
}
