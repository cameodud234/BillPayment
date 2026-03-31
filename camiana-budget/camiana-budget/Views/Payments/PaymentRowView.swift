//
//  PaymentRowView.swift
//  camiana-budget
//
//  Created by Cameron Dudley on 3/29/26.
//

import SwiftUI

struct PaymentRowView: View {
    let payment: Payment

    var body: some View {
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
}
