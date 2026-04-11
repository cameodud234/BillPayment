//
//  SavedPaymentsView.swift
//  camiana-budget
//
//  Created by Cameron Dudley on 4/1/26.
//

import SwiftUI

struct SavedPaymentsView: View {
    @EnvironmentObject var paymentsStore: PaymentsStore

    var body: some View {
        GroupBox("Saved Payments") {
            VStack(alignment: .leading, spacing: 10) {
                HStack {
                    Button("Refresh") {
                        Task {
                            await paymentsStore.loadPayments()
                        }
                    }
                    .buttonStyle(.bordered)

                    Spacer()
                }

                if paymentsStore.isLoadingPayments {
                    ProgressView("Loading payments...")
                        .frame(maxWidth: .infinity, alignment: .leading)
                } else if paymentsStore.payments.isEmpty {
                    Text("No payments found.")
                        .foregroundStyle(.secondary)
                } else {
                    LazyVStack(alignment: .leading, spacing: 8) {
                        ForEach(paymentsStore.payments) { payment in
                            PaymentRowView(payment: payment)
                        }
                    }
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .task {
            if paymentsStore.payments.isEmpty {
                await paymentsStore.loadPayments()
            }
        }
    }
}
