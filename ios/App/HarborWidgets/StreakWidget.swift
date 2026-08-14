import WidgetKit
import SwiftUI

/// Smart-stack face: Grocery — open count + item chips. Small / Medium / Large.
struct HarborListsWidget: Widget {
    let kind = "HarborStreakWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: HarborProvider()) { entry in
            GroceryWidgetView(entry: entry)
                .harborWidgetChrome(entry.snapshot.palette)
                .widgetURL(HarborWidgetLink.grocery)
        }
        .configurationDisplayName("Grocery")
        .description("Open grocery items — tap to open Grocery in Harbor.")
        .supportedFamilies([.systemSmall, .systemMedium, .systemLarge])
        .contentMarginsDisabled()
    }
}

struct GroceryWidgetView: View {
    var entry: HarborEntry
    @Environment(\.widgetFamily) var family

    var body: some View {
        let snap = entry.snapshot
        let open = snap.groceryOpen ?? 0
        let checked = snap.groceryChecked ?? 0
        let items = Array((snap.groceryItems ?? []).prefix(family == .systemLarge ? 12 : (family == .systemMedium ? 6 : 4)))
        let pal = snap.palette

        VStack(alignment: .leading, spacing: family == .systemSmall ? 6 : 8) {
            HStack(alignment: .center, spacing: 8) {
                HarborMark(symbol: "▣", colors: [pal.accent, pal.accentDeep],
                           size: family == .systemSmall ? 20 : 22)
                VStack(alignment: .leading, spacing: 1) {
                    HarborCaption(text: "Grocery", color: pal.accent)
                    Text(checked > 0 ? "\(checked) checked · list open" : "Shopping list")
                        .font(.system(size: 10, weight: .medium))
                        .foregroundStyle(pal.muted)
                        .lineLimit(1)
                        .minimumScaleFactor(0.8)
                }
                Spacer(minLength: 4)
                VStack(alignment: .trailing, spacing: 1) {
                    Text("\(open)")
                        .font(.system(size: HarborWidgetTheme.heroSize(for: family), weight: .bold, design: .rounded))
                        .foregroundStyle(pal.accentDeep)
                        .monospacedDigit()
                        .minimumScaleFactor(0.7)
                        .lineLimit(1)
                    Text("left")
                        .font(.system(size: 10, weight: .semibold))
                        .foregroundStyle(HarborWidgetTheme.secondary)
                }
            }

            if items.isEmpty {
                Spacer(minLength: 0)
                HarborEmptyLine(text: open == 0 ? "List is clear" : "Open Harbor for items", color: pal.muted)
                Spacer(minLength: 0)
            } else if family == .systemSmall {
                VStack(alignment: .leading, spacing: 4) {
                    ForEach(Array(items.prefix(3).enumerated()), id: \.offset) { _, name in
                        HStack(spacing: 6) {
                            Circle()
                                .strokeBorder(pal.accent.opacity(0.65), lineWidth: 1.4)
                                .frame(width: 10, height: 10)
                            Text(name)
                                .font(.system(size: 12, weight: .medium))
                                .foregroundStyle(pal.text)
                                .lineLimit(1)
                                .minimumScaleFactor(0.85)
                        }
                    }
                }
                Spacer(minLength: 0)
            } else {
                FlowishChips(items: items, accent: pal.accent, deep: pal.accentDeep)
                Spacer(minLength: 0)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .harborWidgetPadding(family)
    }
}

/// Simple chip grid without UIKit — rows of wrapped-looking chips via LazyVGrid.
struct FlowishChips: View {
    let items: [String]
    let accent: Color
    let deep: Color

    var body: some View {
        let columns = [GridItem(.adaptive(minimum: 72, maximum: 140), spacing: 5, alignment: .leading)]
        LazyVGrid(columns: columns, alignment: .leading, spacing: 5) {
            ForEach(Array(items.enumerated()), id: \.offset) { _, name in
                Text(name)
                    .font(.system(size: 11, weight: .semibold))
                    .foregroundStyle(deep)
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
                    .padding(.horizontal, 9)
                    .padding(.vertical, 4)
                    .background(accent.opacity(0.16), in: Capsule())
            }
        }
    }
}

typealias HarborStreakWidget = HarborListsWidget
