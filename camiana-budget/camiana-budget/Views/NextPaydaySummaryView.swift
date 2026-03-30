//
//  NextPaydaySummaryView.swift
//  camiana-budget
//
//  Created by Cameron Dudley on 3/22/26.
//

import SwiftUI

struct NextPaydaySummaryView: View {
    @State private var summary: NextPaydaySummaryResponse?
    @State private var isLoading = false
    @State private var errorMessage: String?

    var body: some View {
        GroupBox("Next Payday Summary") {
            VStack(alignment: .leading, spacing: 14) {
                if isLoading {
                    ProgressView("Loading summary...")
                } else if let summary = summary {
                    summaryHeader(summary)

                    Divider()

                    Text("Bills due by payday")
                        .font(.headline)

                    if summary.payments.isEmpty {
                        Text("No bills due before the next Friday payday.")
                            .foregroundStyle(.secondary)
                    } else {
                        List(summary.payments) { payment in
                            HStack {
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(payment.name)
                                        .font(.headline)

                                    if let category = payment.category, !category.isEmpty {
                                        Text(category)
                                            .font(.subheadline)
                                            .foregroundStyle(.secondary)
                                    }
                                }

                                Spacer()

                                VStack(alignment: .trailing, spacing: 4) {
                                    Text("$\(payment.amount, specifier: "%.2f")")
                                        .font(.headline)

                                    Text(payment.due_date)
                                        .font(.subheadline)
                                        .foregroundStyle(.secondary)
                                }
                            }
                            .padding(.vertical, 4)
                        }
                        .frame(minHeight: 120, maxHeight: 260)
                    }
                } else if let errorMessage = errorMessage {
                    Text(errorMessage)
                        .foregroundStyle(.red)
                } else {
                    Text("No summary loaded.")
                        .foregroundStyle(.secondary)
                }

                HStack {
                    Button("Refresh Summary") {
                        Task {
                            await loadSummary()
                        }
                    }
                    .buttonStyle(.borderedProminent)

                    if summary != nil {
                        Text("Updated from local backend")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .task {
            await loadSummary()
        }
    }

    @ViewBuilder
    private func summaryHeader(_ summary: NextPaydaySummaryResponse) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Today: \(summary.today)")
            Text("Next Friday Payday: \(summary.next_payday)")
                .font(.headline)

            HStack(spacing: 12) {
                Label("Your paycheck", systemImage: "checkmark.circle.fill")
                    .foregroundStyle(.green)

                if summary.wife_payday {
                    Label("Wife paycheck too", systemImage: "person.2.fill")
                        .foregroundStyle(.blue)
                } else {
                    Label("Wife off-week", systemImage: "person.fill.xmark")
                        .foregroundStyle(.orange)
                }
            }

            Text("Paychecks this Friday: \(summary.paycheck_count)")
                .font(.subheadline)

            Text("Total due by payday: $\(summary.total_due, specifier: "%.2f")")
                .font(.title3)
                .bold()
        }
    }

    private func loadSummary() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        do {
            let result = try await APIService.shared.fetchNextPaydaySummary()
            summary = result
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
