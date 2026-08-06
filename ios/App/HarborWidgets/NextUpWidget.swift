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
        .description("Your next event with a live countdown.")
        .supportedFamilies([.systemSmall, .systemMedium])
        .contentMarginsDisabled()
    }
}

struct NextUpWidgetView: View {
    var entry: HarborEntry
    @Environment(\.widgetFamily) var family

    var body: some View {
        let snap = entry.snapshot
        // Prefer live-filtered next; never show a finished event
        let ev: HarborWidgetEvent? = {
            if let n = snap.nextEvent, n.isStillRelevant(at: entry.date) { return n }
            return (snap.events ?? []).first(where: { $0.isStillRelevant(at: entry.date) })
        }()

        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 6) {
                Image(systemName: "calendar")
                    .font(.system(size: 11, weight: .semibold))
                    .foregroundStyle(HarborWidgetTheme.accent)
                HarborCaption(text: "Next up")
                Spacer(minLength: 0)
            }

            if let ev = ev {
                Text(ev.displayTitle)
                    .font(.system(size: family == .systemSmall ? 17 : 20, weight: .semibold, design: .default))
                    .foregroundStyle(HarborWidgetTheme.primary)
                    .lineLimit(family == .systemSmall ? 2 : 2)
                    .minimumScaleFactor(0.8)
                    .fixedSize(horizontal: false, vertical: true)

                HStack(spacing: 8) {
                    if let t = ev.time, !t.isEmpty {
                        Text(t)
                            .font(.system(size: 13, weight: .semibold, design: .rounded))
                            .foregroundStyle(HarborWidgetTheme.accentDeep)
                            .monospacedDigit()
                            .lineLimit(1)
                    }
                    if let until = formatEventStatus(ev, at: entry.date) {
                        Text(until)
                            .font(.system(size: 12, weight: .semibold, design: .rounded))
                            .foregroundStyle(until == "now" ? HarborWidgetTheme.accent : HarborWidgetTheme.secondary)
                            .padding(.horizontal, 7)
                            .padding(.vertical, 3)
                            .background(
                                (until == "now" ? HarborWidgetTheme.accentSoft : Color.secondary.opacity(0.10)),
                                in: Capsule()
                            )
                            .lineLimit(1)
                    }
                }

                if let who = ev.who, !who.isEmpty, family != .systemSmall {
                    Text(who)
                        .font(.system(size: 12, weight: .medium))
                        .foregroundStyle(HarborWidgetTheme.secondary)
                        .lineLimit(1)
                }

                if family == .systemMedium, let free = snap.freeLabel, !free.isEmpty {
                    Spacer(minLength: 4)
                    HStack(spacing: 5) {
                        Image(systemName: "clock")
                            .font(.system(size: 10, weight: .semibold))
                            .foregroundStyle(HarborWidgetTheme.accent)
                        Text(free)
                            .font(.system(size: 12, weight: .medium))
                            .foregroundStyle(HarborWidgetTheme.secondary)
                            .lineLimit(1)
                            .minimumScaleFactor(0.85)
                    }
                }
            } else {
                Spacer(minLength: 0)
                Text("No more events today")
                    .font(.system(size: 15, weight: .medium))
                    .foregroundStyle(HarborWidgetTheme.secondary)
                    .lineLimit(2)
                    .minimumScaleFactor(0.9)
                if let free = snap.freeLabel, !free.isEmpty {
                    Text(free)
                        .font(.system(size: 12, weight: .medium))
                        .foregroundStyle(HarborWidgetTheme.accent)
                        .lineLimit(2)
                        .minimumScaleFactor(0.85)
                        .padding(.top, 2)
                }
                Spacer(minLength: 0)
            }

            Spacer(minLength: 0)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .harborWidgetPadding(family)
    }
}
