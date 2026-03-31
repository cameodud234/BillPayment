//
//  ContentView.swift
//  camiana-budget
//
//  Created by Cameron Dudley on 3/21/26.
//

import SwiftUI

struct ContentView: View {
    @State private var payments: [Payment] = []
    @State private var weeklyPayments: [Payment] = []
    @State private var weeklyTotal: Double = 0

    @State private var name: String = ""
    @State private var amount: String = ""
    @State private var category: String = ""
    @State private var dueDate: Date = Date()
    @State private var payday: Date = Date()

    @State private var isLoading = false
    @State private var isSaving = false
    @State private var isCalculating = false

    @State private var errorMessage: String?
    @State private var showAlert = false

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    NextPaydaySummaryView()
                    addPaymentSection
                    budgetToolsSection
                    savedPaymentsSection
                }
                .padding(20)
            }
            .navigationTitle("Bills")
            .frame(minWidth: 850, minHeight: 650)
            .task {
                await loadPayments()
            }
            .alert("Error", isPresented: $showAlert) {
                Button("OK", role: .cancel) {}
            } message: {
                Text(errorMessage ?? "Unknown error")
            }
        }
    }

    private var addPaymentSection: some View {
        GroupBox("Add Payment") {
            VStack(alignment: .leading, spacing: 12) {
                TextField("Payment name", text: $name)

                TextField("Amount", text: $amount)
                    .textFieldStyle(.roundedBorder)

                TextField("Category", text: $category)

                DatePicker("Due Date", selection: $dueDate, displayedComponents: .date)

                HStack {
                    Button {
                        Task {
                            await savePayment()
                        }
                    } label: {
                        if isSaving {
                            ProgressView()
                                .controlSize(.small)
                        } else {
                            Text("Save Payment")
                        }
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(isSaving)

                    Button("Refresh") {
                        Task {
                            await loadPayments()
                        }
                    }
                    .buttonStyle(.bordered)
                    .disabled(isLoading)
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    private var budgetToolsSection: some View {
        GroupBox("Budget Tools") {
            VStack(alignment: .leading, spacing: 12) {
                DatePicker("Payday", selection: $payday, displayedComponents: .date)

                Button {
                    Task {
                        await calculateWeeklyBudget()
                    }
                } label: {
                    if isCalculating {
                        ProgressView()
                            .controlSize(.small)
                    } else {
                        Text("Calculate Weekly Budget")
                    }
                }
                .buttonStyle(.bordered)
                .disabled(isCalculating)

                if !weeklyPayments.isEmpty || weeklyTotal > 0 {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Weekly Total: $\(weeklyTotal, specifier: "%.2f")")
                            .font(.headline)

                        List(weeklyPayments) { payment in
                            PaymentRowView(payment: payment)
                        }
                        .frame(minHeight: 140, maxHeight: 220)
                    }
                    .padding(.top, 4)
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    private var savedPaymentsSection: some View {
        GroupBox("Saved Payments") {
            VStack(alignment: .leading, spacing: 10) {
                if isLoading {
                    ProgressView("Loading payments...")
                        .frame(maxWidth: .infinity, alignment: .leading)
                } else if payments.isEmpty {
                    Text("No payments found.")
                        .foregroundStyle(.secondary)
                } else {
                    List(payments) { payment in
                        PaymentRowView(payment: payment)
                    }
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
    }

    private func loadPayments() async {
        isLoading = true
        defer { isLoading = false }

        do {
            let fetched = try await PaymentsAPIService.shared.fetchPayments()
            payments = fetched
        } catch {
            showError(error.localizedDescription)
        }
    }

    private func savePayment() async {
        guard !name.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            showError("Please enter a payment name.")
            return
        }

        guard let amountValue = Double(amount.trimmingCharacters(in: .whitespacesAndNewlines)) else {
            showError("Please enter a valid amount.")
            return
        }

        isSaving = true
        defer { isSaving = false }

        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        let dueDateString = formatter.string(from: dueDate)

        let request = AddPaymentRequest(
            name: name.trimmingCharacters(in: .whitespacesAndNewlines),
            amount: amountValue,
            due_date: dueDateString,
            category: category.trimmingCharacters(in: .whitespacesAndNewlines)
        )

        do {
            try await PaymentsAPIService.shared.addPayment(request)

            name = ""
            amount = ""
            category = ""

            await loadPayments()
        } catch {
            showError(error.localizedDescription)
        }
    }

    private func calculateWeeklyBudget() async {
        isCalculating = true
        defer { isCalculating = false }

        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        let paydayString = formatter.string(from: payday)

        do {
            let result = try await PaymentsAPIService.shared.calculateWeeklyBudget(payday: paydayString)
            weeklyTotal = result.total
            weeklyPayments = result.payments
        } catch {
            showError(error.localizedDescription)
        }
    }

    private func showError(_ message: String) {
        errorMessage = message
        showAlert = true
    }
}
