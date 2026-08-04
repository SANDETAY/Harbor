import WidgetKit
import SwiftUI

/// Next calendar event — Calendar-app style.
struct HarborNextUpWidget: Widget {
    let kind = "HarborNextUpWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: HarborProvider()) { entry in
            NextUpWidgetView(entry: entry)
                .harborWidgetChrome()
        }
        .configurationDisplayName("Next up")
        .description("Your next event and free window.")
        .supportedFamilies([.systemSmall, .systemMedium])
        .contentMarginsDisabled()
    }
}

struct NextUpWidgetView: View {
    var entry: HarborEntry
    @Environment(\.widgetFamily) var family

    var body: some View {
        let snap = entry.snapshot
        let ev = snap.nextEvent

        VStack(alignment: .leading, spacing: 6) {
            HarborCaption(text: "Next up")

            if let ev = ev, !(ev.title ?? "").isEmpty {
                Text(ev.displayTitle)
                    .font(.system(size: family == .systemSmall ? 16 : 20, weight: .semibold))
                    .foregroundStyle(HarborWidgetTheme.primary)
                    .lineLimit(family == .systemSmall ? 2 : 2)
                    .minimumScaleFactor(0.8)
                    .fixedSize(horizontal: false, vertical: true)

                HStack(spacing: 6) {
                    if let t = ev.time, !t.isEmpty {
                        Text(t)
                            .font(.system(size: 13, weight: .semibold, design: .rounded))
                            .foregroundStyle(HarborWidgetTheme.accent)
                            .monospacedDigit()
                            .lineLimit(1)
                    }
                    if let until = formatMinsUntil(ev.liveMinsUntil(at: entry.date) ?? ev.minsUntil) {
                        Text(until)
                            .font(.system(size: 12, weight: .medium))
                            .foregroundStyle(HarborWidgetTheme.secondary)
                            .lineLimit(1)
                            .minimumScaleFactor(0.85)
                    }
                }

                if let who = ev.who, !who.isEmpty, family != .systemSmall {
                    Text(who)
                        .font(.system(size: 12, weight: .medium))
                        .foregroundStyle(HarborWidgetTheme.secondary)
                        .lineLimit(1)
                }

                if family == .systemMedium, let free = snap.freeLabel, !free.isEmpty {
                    Spacer(minLength: 2)
                    Text(free)
                        .font(.system(size: 12, weight: .medium))
                        .foregroundStyle(HarborWidgetTheme.secondary)
                        .lineLimit(1)
                        .minimumScaleFactor(0.85)
                }
            } else {
                Spacer(minLength: 0)
                Text("No upcoming events")
                    .font(.system(size: 14, weight: .medium))
                    .foregroundStyle(HarborWidgetTheme.secondary)
                    .lineLimit(2)
                    .minimumScaleFactor(0.9)
                if let free = snap.freeLabel, !free.isEmpty {
                    Text(free)
                        .font(.system(size: 12, weight: .medium))
                        .foregroundStyle(HarborWidgetTheme.accent)
                        .lineLimit(2)
                        .minimumScaleFactor(0.85)
                }
                Spacer(minLength: 0)
            }

            Spacer(minLength: 0)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .harborWidgetPadding(family)
    }
}
