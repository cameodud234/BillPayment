//
//  BudgetToolsView.swift
//  camiana-budget
//
//  Created by Cameron Dudley on 4/1/26.
//

import SwiftUI

struct BudgetToolsView: View {
    @EnvironmentObject var paymentsStore: PaymentsStore
    @State private var payday: Date = Date()

    var body: some View {
        GroupBox("Budget Tools") {
            VStack(alignment: .leading, spacing: 12) {
                DatePicker("Payday", selection: $payday, displayedComponents: .date)

                Button {
                    Task {
                        await paymentsStore.calculateWeeklyBudget(payday: payday)
                    }
                } label: {
                    if paymentsStore.isCalculatingWeekly {
                        ProgressView()
                            .controlSize(.small)
                    } else {
                        Text("Calculate Weekly Budget")
                    }
                }
                .buttonStyle(.bordered)
                .disabled(paymentsStore.isCalculatingWeekly)

                if !paymentsStore.weeklyPayments.isEmpty || paymentsStore.weeklyTotal > 0 {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Weekly Total: $\(paymentsStore.weeklyTotal, specifier: "%.2f")")
                            .font(.headline)

                        LazyVStack(alignment: .leading, spacing: 8) {
                            ForEach(paymentsStore.weeklyPayments) { payment in
                                PaymentRowView(payment: payment)
                            }
                        }
                        .frame(minHeight: 140, maxHeight: 220)
                    }
                    .padding(.top, 4)
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }
}
