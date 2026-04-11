//
//  PaymentsStore.swift
//  camiana-budget
//
//  Created by Cameron Dudley on 4/1/26.
//

import Foundation
import Combine

@MainActor
final class PaymentsStore: ObservableObject {
    @Published var payments: [Payment] = []
    @Published var weeklyPayments: [Payment] = []
    @Published var weeklyTotal: Double = 0

    @Published var isLoadingPayments = false
    @Published var isSavingPayment = false
    @Published var isCalculatingWeekly = false

    @Published var errorMessage: String?

    func loadPayments() async {
        isLoadingPayments = true
        errorMessage = nil
        defer { isLoadingPayments = false }

        do {
            payments = try await PaymentsAPIService.shared.fetchPayments()
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func addPayment(
        name: String,
        amount: Double,
        dueDate: Date,
        category: PaymentCategory,
        isRecurring: Bool,
        dueDay: Int?
    ) async {
        isSavingPayment = true
        errorMessage = nil
        defer { isSavingPayment = false }

        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"

        let request = AddPaymentRequest(
            name: name.trimmingCharacters(in: .whitespacesAndNewlines),
            amount: amount,
            due_date: formatter.string(from: dueDate),
            category: category.rawValue,
            account_id: nil,
            is_recurring: isRecurring ? 1 : 0,
            due_day: dueDay
        )

        do {
            try await PaymentsAPIService.shared.addPayment(request)
            await loadPayments()
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func calculateWeeklyBudget(payday: Date) async {
        isCalculatingWeekly = true
        errorMessage = nil
        defer { isCalculatingWeekly = false }

        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        let paydayString = formatter.string(from: payday)

        do {
            let result = try await PaymentsAPIService.shared.calculateWeeklyBudget(payday: paydayString)
            weeklyTotal = result.total
            weeklyPayments = result.payments
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func clearWeeklyResults() {
        weeklyPayments = []
        weeklyTotal = 0
    }
}
