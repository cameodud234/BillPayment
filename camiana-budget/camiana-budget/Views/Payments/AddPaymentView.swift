//
//  AddPaymentView.swift
//  camiana-budget
//
//  Created by Cameron Dudley on 4/1/26.
//

import SwiftUI

struct AddPaymentView: View {
    @EnvironmentObject var paymentsStore: PaymentsStore

    @State private var name: String = ""
    @State private var amount: String = ""
    @State private var dueDate: Date = Date()
    @State private var isRecurring = false
    @State private var dueDay = 1
    @State private var selectedCategory: PaymentCategory = .other

    var body: some View {
        GroupBox("Add Payment") {
            VStack(alignment: .leading, spacing: 12) {
                TextField("Payment name", text: $name)
                    .textFieldStyle(.roundedBorder)

                TextField("Amount", text: $amount)
                    .textFieldStyle(.roundedBorder)

                Picker("Category", selection: $selectedCategory) {
                    ForEach(PaymentCategory.allCases) { category in
                        Text(category.rawValue).tag(category)
                    }
                }
                .pickerStyle(.menu)
                
                Toggle("Recurring Payment", isOn: $isRecurring)
                
                if isRecurring {
                    Picker("Due Day", selection: $dueDay) {
                        ForEach(1...31, id: \.self) { day in
                            Text("\(day)").tag(day)
                        }
                    }
                    .pickerStyle(.menu)

                    Text("This payment will repeat monthly on day \(dueDay).")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                } else {
                    DatePicker("Due Date", selection: $dueDate, displayedComponents: .date)
                }

                Button {
                    Task {
                        await savePayment()
                    }
                } label: {
                    if paymentsStore.isSavingPayment {
                        ProgressView()
                            .controlSize(.small)
                    } else {
                        Text("Save Payment")
                    }
                }
                .buttonStyle(.borderedProminent)
                .disabled(paymentsStore.isSavingPayment)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .alert("Error", isPresented: Binding(
            get: { paymentsStore.errorMessage != nil },
            set: { if !$0 { paymentsStore.errorMessage = nil } }
        )) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(paymentsStore.errorMessage ?? "Unknown error")
        }
    }

    private func savePayment() async {
        guard !name.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            paymentsStore.errorMessage = "Please enter a payment name."
            return
        }

        guard let amountValue = Double(amount.trimmingCharacters(in: .whitespacesAndNewlines)) else {
            paymentsStore.errorMessage = "Please enter a valid amount."
            return
        }

        await paymentsStore.addPayment(
            name: name,
            amount: amountValue,
            dueDate: dueDate,
            category: selectedCategory,
            isRecurring: isRecurring,
            dueDay: isRecurring ? dueDay : nil
        )

        if paymentsStore.errorMessage == nil {
            name = ""
            amount = ""
            selectedCategory = .other
            isRecurring = false
            dueDay = 1
        }
    }
}
