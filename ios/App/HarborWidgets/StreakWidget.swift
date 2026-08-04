import WidgetKit
import SwiftUI

/// Lists pulse — grocery, bills, streak.
struct HarborListsWidget: Widget {
    let kind = "HarborStreakWidget" // keep kind for existing placements

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: HarborProvider()) { entry in
            ListsWidgetView(entry: entry)
                .harborWidgetChrome()
        }
        .configurationDisplayName("Lists")
        .description("Grocery, bills, and streak at a glance.")
        .supportedFamilies([.systemSmall, .systemMedium])
        .contentMarginsDisabled()
    }
}

struct ListsWidgetView: View {
    var entry: HarborEntry
    @Environment(\.widgetFamily) var family

    var body: some View {
        let snap = entry.snapshot
        let grocery = snap.groceryOpen ?? 0
        let bills = snap.billsDue ?? 0
        let tasks = snap.tasksOpen ?? 0
        let streak = snap.streakActive ?? snap.streakBest ?? 0

        VStack(alignment: .leading, spacing: 8) {
            HarborCaption(text: "Harbor")

            if family == .systemSmall {
                VStack(alignment: .leading, spacing: 7) {
                    row(icon: "cart", title: "Grocery", value: "\(grocery)")
                    row(icon: "list.bullet", title: "Tasks", value: "\(tasks)")
                    if bills > 0 {
                        row(icon: "creditcard", title: "Bills", value: "\(bills)", hot: true)
                    } else if streak > 0 {
                        row(icon: "flame.fill", title: "Streak", value: "\(streak)d")
                    }
                }
            } else {
                HStack(alignment: .top, spacing: 8) {
                    bigStat(icon: "cart", value: "\(grocery)", label: "Grocery")
                    bigStat(icon: "checklist", value: "\(tasks)", label: "Tasks")
                    bigStat(icon: "creditcard", value: "\(bills)", label: "Bills", hot: bills > 0)
                    if streak > 0 {
                        bigStat(icon: "flame.fill", value: "\(streak)", label: "Streak")
                    }
                }
                Spacer(minLength: 0)
                if let label = snap.streakLabel, !label.isEmpty, streak > 0 {
                    Text(label)
                        .font(.system(size: 12, weight: .medium))
                        .foregroundStyle(HarborWidgetTheme.secondary)
                        .lineLimit(1)
                        .minimumScaleFactor(0.85)
                }
            }

            Spacer(minLength: 0)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .harborWidgetPadding(family)
    }

    @ViewBuilder
    private func row(icon: String, title: String, value: String, hot: Bool = false) -> some View {
        HStack(spacing: 7) {
            Image(systemName: icon)
                .font(.system(size: 12, weight: .semibold))
                .foregroundStyle(hot ? Color.orange : HarborWidgetTheme.accent)
                .frame(width: 16)
            Text(title)
                .font(.system(size: 13, weight: .medium))
                .foregroundStyle(HarborWidgetTheme.primary)
                .lineLimit(1)
                .minimumScaleFactor(0.85)
            Spacer(minLength: 0)
            Text(value)
                .font(.system(size: 15, weight: .semibold, design: .rounded))
                .foregroundStyle(hot ? Color.orange : HarborWidgetTheme.primary)
                .monospacedDigit()
                .lineLimit(1)
                .minimumScaleFactor(0.8)
        }
    }

    @ViewBuilder
    private func bigStat(icon: String, value: String, label: String, hot: Bool = false) -> some View {
        VStack(alignment: .leading, spacing: 3) {
            Image(systemName: icon)
                .font(.system(size: 11, weight: .semibold))
                .foregroundStyle(hot ? Color.orange : HarborWidgetTheme.accent)
            Text(value)
                .font(.system(size: 20, weight: .semibold, design: .rounded))
                .foregroundStyle(hot ? Color.orange : HarborWidgetTheme.primary)
                .monospacedDigit()
                .lineLimit(1)
                .minimumScaleFactor(0.7)
            Text(label)
                .font(.system(size: 10, weight: .medium))
                .foregroundStyle(HarborWidgetTheme.secondary)
                .lineLimit(1)
                .minimumScaleFactor(0.8)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

typealias HarborStreakWidget = HarborListsWidget
