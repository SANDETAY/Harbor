import WidgetKit
import SwiftUI

/// Smart-stack face: Events — hero next event + later list. Small / Medium / Large.
struct HarborNextUpWidget: Widget {
    let kind = "HarborNextUpWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: HarborProvider()) { entry in
            NextUpWidgetView(entry: entry)
                .harborWidgetChrome(entry.snapshot.palette)
                .widgetURL(HarborWidgetLink.events)
        }
        .configurationDisplayName("Events")
        .description("Next event with countdown — tap to open Schedule in Harbor.")
        .supportedFamilies([.systemSmall, .systemMedium, .systemLarge])
        .contentMarginsDisabled()
    }
}

struct NextUpWidgetView: View {
    var entry: HarborEntry
    @Environment(\.widgetFamily) var family

    var body: some View {
        let snap = entry.snapshot
        let events = (snap.events ?? []).filter { $0.isStillRelevant(at: entry.date) }
        let ev: HarborWidgetEvent? = {
            if let n = snap.nextEvent, n.isStillRelevant(at: entry.date) { return n }
            return events.first
        }()
        let moreLimit = family == .systemLarge ? 4 : (family == .systemMedium ? 2 : 0)
        let more = Array(events.dropFirst().prefix(moreLimit))

        let pal = snap.palette
        VStack(alignment: .leading, spacing: family == .systemSmall ? 5 : 6) {
            HStack(alignment: .center, spacing: 8) {
                HarborMark(symbol: "◷", colors: [pal.accent, pal.accentDeep],
                           size: family == .systemSmall ? 20 : 22)
                VStack(alignment: .leading, spacing: 1) {
                    HarborCaption(text: "Events", color: pal.accent)
                    Text("Next up")
                        .font(.system(size: 10, weight: .medium))
                        .foregroundStyle(pal.muted)
                        .lineLimit(1)
                }
                Spacer(minLength: 4)
                HarborWidgetDateStamp(
                    date: entry.date,
                    palette: pal,
                    compact: family == .systemSmall
                )
            }

            if let ev = ev {
                HStack(alignment: .top, spacing: 9) {
                    RoundedRectangle(cornerRadius: 2, style: .continuous)
                        .fill(
                            LinearGradient(
                                colors: [pal.accent, pal.accentDeep],
                                startPoint: .top,
                                endPoint: .bottom
                            )
                        )
                        .frame(width: 4)
                        .frame(minHeight: family == .systemSmall ? 40 : 48)

                    VStack(alignment: .leading, spacing: 3) {
                        Text(ev.displayTitle)
                            .font(.system(
                                size: family == .systemSmall ? 18 : (family == .systemLarge ? 24 : 21),
                                weight: .bold
                            ))
                            .foregroundStyle(pal.text)
                            .lineLimit(family == .systemSmall ? 2 : 1)
                            .minimumScaleFactor(0.75)

                        HStack(spacing: 6) {
                            if let t = ev.time, !t.isEmpty {
                                Text(t)
                                    .font(.system(size: family == .systemSmall ? 12 : 13, weight: .bold, design: .rounded))
                                    .foregroundStyle(pal.accentDeep)
                                    .monospacedDigit()
                                    .lineLimit(1)
                            }
                            if let until = formatEventStatus(ev, at: entry.date) {
                                Text(until)
                                    .font(.system(size: 11, weight: .bold, design: .rounded))
                                    .foregroundStyle(pal.accentDeep)
                                    .padding(.horizontal, 8)
                                    .padding(.vertical, 3)
                                    .background(pal.accent.opacity(0.14), in: Capsule())
                                    .lineLimit(1)
                            }
                        }

                        if let who = ev.who, !who.isEmpty, family != .systemSmall {
                            Text(who)
                                .font(.system(size: 11, weight: .medium))
                                .foregroundStyle(pal.muted)
                                .lineLimit(1)
                                .minimumScaleFactor(0.85)
                        }
                    }
                    Spacer(minLength: 0)
                }

                if !more.isEmpty {
                    VStack(alignment: .leading, spacing: 4) {
                        Divider().opacity(0.35)
                        ForEach(Array(more.enumerated()), id: \.offset) { _, e in
                            HStack {
                                Text(e.displayTitle)
                                    .font(.system(size: family == .systemLarge ? 13 : 12, weight: .semibold))
                                    .foregroundStyle(pal.text)
                                    .lineLimit(1)
                                    .minimumScaleFactor(0.85)
                                Spacer(minLength: 4)
                                if let t = e.time, !t.isEmpty {
                                    Text(t)
                                        .font(.system(size: 11, weight: .medium, design: .rounded))
                                        .foregroundStyle(pal.muted)
                                        .monospacedDigit()
                                        .lineLimit(1)
                                }
                            }
                        }
                    }
                }
            } else {
                Spacer(minLength: 0)
                HarborEmptyLine(text: "No more events today", color: pal.muted)
                Spacer(minLength: 0)
            }

            Spacer(minLength: 0)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .harborWidgetPadding(family)
    }
}
