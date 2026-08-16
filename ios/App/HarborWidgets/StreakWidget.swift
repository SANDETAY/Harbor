import WidgetKit
import SwiftUI

/// Grocery — items left + next meal. Small / Medium.
struct HarborListsWidget: Widget {
    let kind = "HarborStreakWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: HarborProvider()) { entry in
            GroceryWidgetView(entry: entry)
                .harborWidgetChrome(entry.snapshot.palette)
                .widgetURL(HarborWidgetLink.grocery)
        }
        .configurationDisplayName("Grocery")
        .description("Items left and tonight’s meal. Tap to open Grocery.")
        .supportedFamilies([.systemSmall, .systemMedium])
        .contentMarginsDisabled()
    }
}

struct GroceryWidgetView: View {
    var entry: HarborEntry
    @Environment(\.widgetFamily) var family

    var body: some View {
        let snap = entry.snapshot
        let pal = snap.palette
        let open = snap.groceryOpen ?? 0
        let items = Array((snap.groceryItems ?? []).prefix(3))
        let meal = snap.mealLine

        VStack(alignment: .leading, spacing: 6) {
            Text("GROCERY")
                .font(.system(size: 10, weight: .bold, design: .rounded))
                .foregroundStyle(pal.accent)
                .tracking(0.7)

            if family == .systemSmall {
                Text("\(open)")
                    .font(.system(size: 34, weight: .bold, design: .rounded))
                    .foregroundStyle(pal.accentDeep)
                    .monospacedDigit()
                Text(open == 0 ? "No items left" : "items left")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundStyle(pal.muted)
                Spacer(minLength: 0)
                if let meal, !meal.isEmpty {
                    Text(meal)
                        .font(.system(size: 11, weight: .semibold))
                        .foregroundStyle(pal.accentDeep)
                        .lineLimit(2)
                        .minimumScaleFactor(0.85)
                }
            } else {
                HStack(alignment: .firstTextBaseline) {
                    Text(open == 0 ? "List is clear" : "\(open) items left")
                        .font(.system(size: 13, weight: .medium))
                        .foregroundStyle(pal.muted)
                    Spacer()
                    Text("\(open)")
                        .font(.system(size: 28, weight: .bold, design: .rounded))
                        .foregroundStyle(pal.accentDeep)
                        .monospacedDigit()
                }
                if items.isEmpty {
                    Spacer(minLength: 0)
                    HarborEmptyLine(text: "No items left", color: pal.muted)
                    Spacer(minLength: 0)
                } else {
                    ForEach(Array(items.enumerated()), id: \.offset) { _, name in
                        HStack(spacing: 8) {
                            Circle()
                                .strokeBorder(pal.accent.opacity(0.65), lineWidth: 1.4)
                                .frame(width: 10, height: 10)
                            Text(name)
                                .font(.system(size: 13, weight: .medium))
                                .foregroundStyle(pal.text)
                                .lineLimit(1)
                        }
                    }
                    Spacer(minLength: 0)
                    if let meal, !meal.isEmpty {
                        Text(meal)
                            .font(.system(size: 11.5, weight: .semibold))
                            .foregroundStyle(pal.accentDeep)
                            .lineLimit(2)
                    }
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .harborWidgetPadding(family)
    }
}

typealias HarborStreakWidget = HarborListsWidget
