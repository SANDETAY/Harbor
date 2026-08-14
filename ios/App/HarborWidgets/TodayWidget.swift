import WidgetKit
import SwiftUI

/// Smart-stack face: Tasks — mint ring + open list. Small / Medium / Large.
struct HarborTodayWidget: Widget {
    let kind = "HarborTodayWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: HarborProvider()) { entry in
            TodayWidgetView(entry: entry)
                .harborWidgetChrome(entry.snapshot.palette)
                .widgetURL(HarborWidgetLink.tasks)
        }
        .configurationDisplayName("Tasks")
        .description("Open tasks with progress — tap to open Task in Harbor.")
        .supportedFamilies([.systemSmall, .systemMedium, .systemLarge])
        .contentMarginsDisabled()
    }
}

struct TodayWidgetView: View {
    var entry: HarborEntry
    @Environment(\.widgetFamily) var family

    var body: some View {
        let snap = entry.snapshot
        let open = snap.tasksOpen ?? (snap.tasks ?? []).count
        let done = snap.resolvedTasksDone
        let total = max(snap.resolvedTasksTotal, open)
        let limit: Int = {
            switch family {
            case .systemSmall: return 3
            case .systemLarge: return 8
            default: return 4
            }
        }()
        let tasks = Array((snap.tasks ?? []).prefix(limit))
        let ringSize: CGFloat = family == .systemSmall ? 44 : (family == .systemLarge ? 62 : 54)
        let pal = snap.palette

        VStack(alignment: .leading, spacing: family == .systemSmall ? 6 : 8) {
            HStack(alignment: .center, spacing: 8) {
                HarborMark(symbol: "✓", colors: [pal.accent, pal.accentDeep],
                           size: family == .systemSmall ? 20 : 22)
                VStack(alignment: .leading, spacing: 1) {
                    HarborCaption(text: "Tasks", color: pal.accent)
                    Text(total > 0 ? "\(done) of \(total) today" : "Today")
                        .font(.system(size: family == .systemSmall ? 10 : 11, weight: .medium))
                        .foregroundStyle(pal.muted)
                        .lineLimit(1)
                        .minimumScaleFactor(0.8)
                }
                Spacer(minLength: 4)
                HarborProgressRing(
                    progress: snap.taskProgress,
                    color: pal.accent,
                    lineWidth: family == .systemSmall ? 4 : 5,
                    centerText: "\(open)"
                )
                .frame(width: ringSize, height: ringSize)
            }

            if tasks.isEmpty {
                Spacer(minLength: 0)
                HarborEmptyLine(text: open == 0 ? "All clear for now" : "Open Harbor", color: pal.muted)
                Spacer(minLength: 0)
            } else {
                VStack(alignment: .leading, spacing: family == .systemSmall ? 5 : 7) {
                    ForEach(Array(tasks.enumerated()), id: \.offset) { _, t in
                        HStack(spacing: 8) {
                            Circle()
                                .strokeBorder(pal.accent.opacity(0.7), lineWidth: 1.6)
                                .frame(width: family == .systemSmall ? 11 : 13,
                                       height: family == .systemSmall ? 11 : 13)
                            Text(t.displayTitle)
                                .font(.system(size: HarborWidgetTheme.bodySize(for: family), weight: .medium))
                                .foregroundStyle(pal.text)
                                .lineLimit(1)
                                .minimumScaleFactor(0.85)
                            Spacer(minLength: 0)
                            if let m = t.mins, m > 0, family != .systemSmall {
                                Text("\(m)m")
                                    .font(.system(size: 11, weight: .semibold, design: .rounded))
                                    .foregroundStyle(pal.muted)
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
