import WidgetKit
import SwiftUI

/// Next bill due. Small.
struct HarborDayWidget: Widget {
    let kind = "HarborGlanceWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: HarborProvider()) { entry in
            BillsWidgetView(entry: entry)
                .harborWidgetChrome(entry.snapshot.palette)
                .widgetURL(HarborWidgetLink.bills)
        }
        .configurationDisplayName("Bills")
        .description("Next bill due. Tap to open Bills.")
        .supportedFamilies([.systemSmall])
        .contentMarginsDisabled()
    }
}

struct BillsWidgetView: View {
    var entry: HarborEntry

    var body: some View {
        let snap = entry.snapshot
        let pal = snap.palette
        let title = (snap.nextBillTitle?.isEmpty == false) ? snap.nextBillTitle! : nil
        let when = snap.nextBillWhen ?? ""
        let amt = snap.billsDueAmount ?? 0
        let dueCount = snap.billsDue ?? 0

        VStack(alignment: .leading, spacing: 6) {
            Text("BILLS")
                .font(.system(size: 10, weight: .bold, design: .rounded))
                .foregroundStyle(pal.accent)
                .tracking(0.7)

            if title != nil || dueCount > 0 {
                Text(title ?? "Bill due")
                    .font(.system(size: 16, weight: .bold))
                    .foregroundStyle(pal.text)
                    .lineLimit(2)
                    .minimumScaleFactor(0.85)
                if amt > 0 {
                    Text(formatMoney(amt))
                        .font(.system(size: 26, weight: .bold, design: .rounded))
                        .foregroundStyle(pal.text)
                        .monospacedDigit()
                }
                Text(when.isEmpty ? "Due soon" : when)
                    .font(.system(size: 12, weight: .medium))
                    .foregroundStyle(pal.muted)
                Spacer(minLength: 0)
            } else {
                Spacer(minLength: 0)
                Text("No bills due this week")
                    .font(.system(size: 16, weight: .semibold))
                    .foregroundStyle(pal.muted)
                    .lineLimit(3)
                Spacer(minLength: 0)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .harborWidgetPadding(.systemSmall)
    }
}

typealias HarborGlanceWidget = HarborDayWidget
