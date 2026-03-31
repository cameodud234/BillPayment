import SwiftUI

struct NextPaydaySummaryView: View {
    @StateObject private var viewModel = DashboardViewModel()

    var body: some View {
        GroupBox("Next Payday Summary") {
            VStack(alignment: .leading, spacing: 14) {
                content

                HStack {
                    Button("Refresh Summary") {
                        Task {
                            await viewModel.loadNextPaydaySummary()
                        }
                    }
                    .buttonStyle(.borderedProminent)

                    if viewModel.hasSummary {
                        Text("Updated from local backend")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .task {
            await viewModel.loadNextPaydaySummary()
        }
    }

    @ViewBuilder
    private var content: some View {
        if viewModel.isLoading {
            ProgressView("Loading summary...")
        } else if let summary = viewModel.summary {
            summaryHeader(summary)

            Divider()

            Text("Bills due by payday")
                .font(.headline)

            if viewModel.payments.isEmpty {
                Text("No bills due before the next Friday payday.")
                    .foregroundStyle(.secondary)
            } else {
                List(viewModel.payments) { payment in
                    PaymentRowView(payment: payment)
                }
                .frame(minHeight: 120, maxHeight: 260)
            }
        } else if let errorMessage = viewModel.errorMessage {
            Text(errorMessage)
                .foregroundStyle(.red)
        } else {
            Text("No summary loaded.")
                .foregroundStyle(.secondary)
        }
    }

    @ViewBuilder
    private func summaryHeader(_ summary: NextPaydaySummaryResponse) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(viewModel.todayText)

            Text(viewModel.nextPaydayText)
                .font(.headline)

            HStack(spacing: 12) {
                Label("Your paycheck", systemImage: "checkmark.circle.fill")
                    .foregroundStyle(.green)

                if viewModel.wifePayday {
                    Label("Wife paycheck too", systemImage: "person.2.fill")
                        .foregroundStyle(.blue)
                } else {
                    Label("Wife off-week", systemImage: "person.fill.xmark")
                        .foregroundStyle(.orange)
                }
            }

            Text(viewModel.paycheckCountText)
                .font(.subheadline)

            Text(viewModel.totalDueText)
                .font(.title3)
                .bold()
        }
    }
}
