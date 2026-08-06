import WidgetKit
import SwiftUI

/// Hero widget — day at a glance (calendar + free time + tasks + lists).
struct HarborDayWidget: Widget {
    let kind = "HarborGlanceWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: HarborProvider()) { entry in
            DayWidgetView(entry: entry)
                .harborWidgetChrome()
        }
        .configurationDisplayName("Day")
        .description("Next event, free time, and top tasks.")
        .supportedFamilies([.systemMedium, .systemLarge])
        .contentMarginsDisabled()
    }
}

struct DayWidgetView: View {
    var entry: HarborEntry
    @Environment(\.widgetFamily) var family

    var body: some View {
        let snap = entry.snapshot
        let open = snap.tasksOpen ?? 0
        let grocery = snap.groceryOpen ?? 0
        let bills = snap.billsDue ?? 0
        let taskLimit = family == .systemLarge ? 4 : 2
        let tasks = Array((snap.tasks ?? []).prefix(taskLimit))
        let events = (snap.events ?? []).filter { $0.isStillRelevant(at: entry.date) }
        let nextEv = snap.nextEvent.flatMap { $0.isStillRelevant(at: entry.date) ? $0 : nil }
            ?? events.first

        VStack(alignment: .leading, spacing: 10) {
            // Header
            HStack(alignment: .top, spacing: 8) {
                VStack(alignment: .leading, spacing: 2) {
                    Text(snap.greeting ?? "Harbor")
                        .font(.system(size: 11, weight: .semibold, design: .rounded))
                        .foregroundStyle(HarborWidgetTheme.accent)
                        .lineLimit(1)
                        .minimumScaleFactor(0.85)
                    if let shape = snap.dayShape, !shape.isEmpty {
                        Text(shape)
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundStyle(HarborWidgetTheme.primary)
                            .lineLimit(1)
                            .minimumScaleFactor(0.85)
                    } else {
                        Text(weekdayLabel())
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundStyle(HarborWidgetTheme.primary)
                            .lineLimit(1)
                    }
                }
                Spacer(minLength: 6)
                HStack(spacing: 10) {
                    metric(value: open, label: "tasks")
                    if grocery > 0 { metric(value: grocery, label: "list") }
                    if bills > 0 { metric(value: bills, label: "bills", hot: true) }
                }
            }

            if let free = snap.freeLabel, !free.isEmpty {
                HStack(spacing: 6) {
                    Image(systemName: "clock.fill")
                        .font(.system(size: 10, weight: .semibold))
                        .foregroundStyle(HarborWidgetTheme.accent)
                    Text(free)
                        .font(.system(size: 12, weight: .medium))
                        .foregroundStyle(HarborWidgetTheme.primary)
                        .lineLimit(1)
                        .minimumScaleFactor(0.85)
                }
                .padding(.horizontal, 10)
                .padding(.vertical, 6)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(HarborWidgetTheme.accentSoft, in: RoundedRectangle(cornerRadius: 10, style: .continuous))
            }

            if let ev = nextEv {
                eventRow(ev, emphasize: true)
                if family == .systemLarge {
                    ForEach(Array(events.dropFirst().prefix(2).enumerated()), id: \.offset) { _, e in
                        eventRow(e, emphasize: false)
                    }
                }
            } else {
                Text("No events left today")
                    .font(.system(size: 13, weight: .medium))
                    .foregroundStyle(HarborWidgetTheme.secondary)
                    .lineLimit(1)
            }

            if !tasks.isEmpty {
                Divider().opacity(0.25)
                ForEach(Array(tasks.enumerated()), id: \.offset) { _, t in
                    HStack(spacing: 8) {
                        Circle()
                            .strokeBorder(HarborWidgetTheme.accent.opacity(0.7), lineWidth: 1.5)
                            .frame(width: 12, height: 12)
                        Text(t.displayTitle)
                            .font(.system(size: 13.5, weight: .medium))
                            .foregroundStyle(HarborWidgetTheme.primary)
                            .lineLimit(1)
                            .minimumScaleFactor(0.85)
                        Spacer(minLength: 0)
                        if let m = t.mins, m > 0 {
                            Text("\(m)m")
                                .font(.system(size: 11, weight: .regular, design: .rounded))
                                .foregroundStyle(HarborWidgetTheme.secondary)
                                .monospacedDigit()
                        }
                    }
                }
            } else if open == 0 {
                Text("Tasks clear")
                    .font(.system(size: 13, weight: .medium))
                    .foregroundStyle(HarborWidgetTheme.secondary)
            }

            Spacer(minLength: 0)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .harborWidgetPadding(family)
    }

    @ViewBuilder
    private func metric(value: Int, label: String, hot: Bool = false) -> some View {
        VStack(alignment: .trailing, spacing: 0) {
            Text("\(value)")
                .font(.system(size: 17, weight: .semibold, design: .rounded))
                .foregroundStyle(hot ? Color.orange : HarborWidgetTheme.primary)
                .monospacedDigit()
                .lineLimit(1)
                .minimumScaleFactor(0.8)
            Text(label)
                .font(.system(size: 9, weight: .medium))
                .foregroundStyle(HarborWidgetTheme.secondary)
                .lineLimit(1)
        }
    }

    @ViewBuilder
    private func eventRow(_ ev: HarborWidgetEvent, emphasize: Bool) -> some View {
        HStack(alignment: .center, spacing: 8) {
            RoundedRectangle(cornerRadius: 2, style: .continuous)
                .fill(HarborWidgetTheme.accent)
                .frame(width: 3, height: emphasize ? 28 : 24)
            VStack(alignment: .leading, spacing: 2) {
                Text(ev.displayTitle)
                    .font(.system(size: emphasize ? 14 : 13, weight: .semibold))
                    .foregroundStyle(HarborWidgetTheme.primary)
                    .lineLimit(1)
                    .minimumScaleFactor(0.85)
                HStack(spacing: 5) {
                    if let t = ev.time, !t.isEmpty {
                        Text(t)
                            .font(.system(size: 11, weight: .medium, design: .rounded))
                            .foregroundStyle(HarborWidgetTheme.secondary)
                            .monospacedDigit()
                    }
                    if let until = formatEventStatus(ev, at: entry.date) {
                        Text(until)
                            .font(.system(size: 11, weight: .semibold, design: .rounded))
                            .foregroundStyle(until == "now" ? HarborWidgetTheme.accent : HarborWidgetTheme.secondary)
                    }
                }
            }
            Spacer(minLength: 0)
        }
    }

    private func weekdayLabel() -> String {
        let f = DateFormatter()
        f.dateFormat = "EEEE"
        return f.string(from: Date())
    }
}

typealias HarborGlanceWidget = HarborDayWidget
