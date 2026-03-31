//
//  DashboardViewModel.swift
//  camiana-budget
//
//  Created by Cameron Dudley on 3/29/26.
//

import Foundation
import Combine

@MainActor
final class DashboardViewModel: ObservableObject {
    @Published var summary: NextPaydaySummaryResponse?
    @Published var isLoading = false
    @Published var errorMessage: String?

    func loadNextPaydaySummary() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        do {
            let result = try await SummariesAPIService.shared.fetchNextPaydaySummary()
            summary = result
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    var hasSummary: Bool {
        summary != nil
    }

    var todayText: String {
        "Today: \(summary?.today ?? "-")"
    }

    var nextPaydayText: String {
        "Next Friday Payday: \(summary?.next_payday ?? "-")"
    }

    var paycheckCountText: String {
        "Paychecks this Friday: \(summary?.paycheck_count ?? 0)"
    }

    var totalDueText: String {
        let total = summary?.total_due ?? 0
        return String(format: "Total due before payday: $%.2f", total)
    }

    var payments: [Payment] {
        summary?.payments ?? []
    }

    var wifePayday: Bool {
        summary?.wife_payday ?? false
    }
}
