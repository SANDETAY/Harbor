import WidgetKit
import SwiftUI

/// Quick wins — low-effort due / overdue work. Small / Medium.
struct HarborNextUpWidget: Widget {
    let kind = "HarborNextUpWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: HarborProvider()) { entry in
            QuickWinsWidgetView(entry: entry)
                .harborWidgetChrome(entry.snapshot.palette)
                .widgetURL(HarborWidgetLink.today)
        }
        .configurationDisplayName("Quick Wins")
        .description("Easy tasks when energy is low. Tap to open Today.")
        .supportedFamilies([.systemSmall, .systemMedium])
        .contentMarginsDisabled()
    }
}

struct QuickWinsWidgetView: View {
    var entry: HarborEntry
    @Environment(\.widgetFamily) var family

    var body: some View {
        let snap = entry.snapshot
        let pal = snap.palette
        let wins = Array((snap.easyTasks ?? snap.tasks ?? []).prefix(3))

        VStack(alignment: .leading, spacing: 7) {
            Text("QUICK WINS")
                .font(.system(size: 10, weight: .bold, design: .rounded))
                .foregroundStyle(pal.accent)
                .tracking(0.7)

            if wins.isEmpty {
                Spacer(minLength: 0)
                HarborEmptyLine(text: "Nothing easy left", color: pal.muted)
                Spacer(minLength: 0)
            } else if family == .systemSmall {
                Text(wins[0].displayTitle)
                    .font(.system(size: 16, weight: .bold))
                    .foregroundStyle(pal.text)
                    .lineLimit(3)
                    .minimumScaleFactor(0.8)
                Text("Low effort · due today")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundStyle(pal.muted)
                Spacer(minLength: 0)
            } else {
                Text("Easy tasks for a low-energy stretch")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundStyle(pal.muted)
                    .lineLimit(1)
                ForEach(Array(wins.enumerated()), id: \.offset) { _, t in
                    HStack(spacing: 8) {
                        Circle()
                            .strokeBorder(pal.accent.opacity(0.7), lineWidth: 1.5)
                            .frame(width: 11, height: 11)
                        Text(t.displayTitle)
                            .font(.system(size: 13.5, weight: .medium))
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
                Spacer(minLength: 0)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .harborWidgetPadding(family)
    }
}
