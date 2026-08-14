import WidgetKit
import SwiftUI

/// Smart-stack face: Budget — spent / left / bills always visible. Small / Medium / Large.
struct HarborDayWidget: Widget {
    let kind = "HarborGlanceWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: HarborProvider()) { entry in
            BudgetWidgetView(entry: entry)
                .harborWidgetChrome(entry.snapshot.palette)
                .widgetURL(HarborWidgetLink.budget)
        }
        .configurationDisplayName("Budget")
        .description("Month spend, left, and bills due — tap to open Budget in Harbor.")
        .supportedFamilies([.systemSmall, .systemMedium, .systemLarge])
        .contentMarginsDisabled()
    }
}

struct BudgetWidgetView: View {
    var entry: HarborEntry
    @Environment(\.widgetFamily) var family

    var body: some View {
        let snap = entry.snapshot
        let spent = snap.budgetSpent ?? 0
        let limit = snap.budgetLimit ?? 0
        let left = snap.budgetLeft ?? max(0, limit - spent)
        let pct = snap.resolvedBudgetPct
        let bills = snap.billsDue ?? 0
        let billsAmt = snap.billsDueAmount ?? 0
        let pal = snap.palette

        VStack(alignment: .leading, spacing: family == .systemSmall ? 6 : 8) {
            HStack(alignment: .center, spacing: 8) {
                HarborMark(symbol: "$", colors: [pal.accent, pal.accentDeep],
                           size: family == .systemSmall ? 20 : 22)
                VStack(alignment: .leading, spacing: 1) {
                    HarborCaption(text: "Budget", color: pal.accentDeep)
                    Text(limit > 0 ? "This month · \(pct)% used" : "This month")
                        .font(.system(size: 10, weight: .medium))
                        .foregroundStyle(pal.muted)
                        .lineLimit(1)
                        .minimumScaleFactor(0.8)
                }
                Spacer(minLength: 0)
            }

            // Spent hero
            HStack(alignment: .firstTextBaseline, spacing: 6) {
                Text(formatMoney(spent))
                    .font(.system(size: HarborWidgetTheme.heroSize(for: family), weight: .bold, design: .rounded))
                    .foregroundStyle(pal.text)
                    .monospacedDigit()
                    .minimumScaleFactor(0.7)
                    .lineLimit(1)
                if limit > 0 {
                    Text("of \(formatMoney(limit))")
                        .font(.system(size: family == .systemSmall ? 11 : 12, weight: .semibold))
                        .foregroundStyle(pal.muted)
                        .monospacedDigit()
                        .lineLimit(1)
                        .minimumScaleFactor(0.8)
                }
                Spacer(minLength: 0)
            }

            // Progress bar
            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    Capsule().fill(Color.secondary.opacity(0.12))
                    Capsule()
                        .fill(
                            LinearGradient(
                                colors: [pal.accentDeep, pal.accent],
                                startPoint: .leading,
                                endPoint: .trailing
                            )
                        )
                        .frame(width: max(6, geo.size.width * CGFloat(pct) / 100.0))
                }
            }
            .frame(height: family == .systemSmall ? 6 : 8)

            // Left + Bills — always visible
            if family == .systemSmall {
                HStack(spacing: 8) {
                    budgetPill(label: "Left", value: formatMoney(left), hot: false)
                    budgetPill(
                        label: "Bills",
                        value: bills > 0 ? "\(bills)" : "0",
                        hot: bills > 0
                    )
                }
            } else {
                HStack(spacing: 8) {
                    budgetTile(
                        label: "Left",
                        value: formatMoney(left),
                        hint: "room to spend",
                        hot: false
                    )
                    budgetTile(
                        label: "Bills due",
                        value: bills > 0 ? "\(bills)" : "0",
                        hint: billsAmt > 0 ? formatMoney(billsAmt) + " total" : "none soon",
                        hot: bills > 0
                    )
                }
            }

            if family == .systemLarge {
                Spacer(minLength: 4)
                Text("Tap to open Budget in Harbor")
                    .font(.system(size: 11, weight: .medium))
                    .foregroundStyle(pal.muted)
            }

            Spacer(minLength: 0)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .harborWidgetPadding(family)
    }

    @ViewBuilder
    private func budgetPill(label: String, value: String, hot: Bool) -> some View {
        let pal = entry.snapshot.palette
        VStack(alignment: .leading, spacing: 1) {
            Text(label.uppercased())
                .font(.system(size: 8, weight: .bold))
                .foregroundStyle(pal.muted)
                .tracking(0.4)
            Text(value)
                .font(.system(size: 14, weight: .bold, design: .rounded))
                .foregroundStyle(hot ? Color.orange : pal.text)
                .monospacedDigit()
                .lineLimit(1)
                .minimumScaleFactor(0.7)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal, 8)
        .padding(.vertical, 6)
        .background(Color.secondary.opacity(0.08), in: RoundedRectangle(cornerRadius: 10, style: .continuous))
    }

    @ViewBuilder
    private func budgetTile(label: String, value: String, hint: String, hot: Bool) -> some View {
        let pal = entry.snapshot.palette
        VStack(alignment: .leading, spacing: 2) {
            Text(label.uppercased())
                .font(.system(size: 10, weight: .bold))
                .foregroundStyle(pal.muted)
                .tracking(0.5)
                .lineLimit(1)
            Text(value)
                .font(.system(size: 16, weight: .bold, design: .rounded))
                .foregroundStyle(hot ? Color.orange : pal.text)
                .monospacedDigit()
                .lineLimit(1)
                .minimumScaleFactor(0.75)
            Text(hint)
                .font(.system(size: 10, weight: .medium))
                .foregroundStyle(pal.muted)
                .lineLimit(1)
                .minimumScaleFactor(0.8)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal, 10)
        .padding(.vertical, 8)
        .background(Color.secondary.opacity(0.08), in: RoundedRectangle(cornerRadius: 12, style: .continuous))
    }
}

typealias HarborGlanceWidget = HarborDayWidget
