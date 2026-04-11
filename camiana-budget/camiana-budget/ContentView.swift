//
//  ContentView.swift
//  camiana-budget
//
//  Created by Cameron Dudley on 3/21/26.
//

import SwiftUI

struct ContentView: View {
    @StateObject private var paymentsStore = PaymentsStore()
    
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    NextPaydaySummaryView()
                    AddPaymentView()
                    BudgetToolsView()
                    SavedPaymentsView()
                }
                .padding(20)
            }
            .navigationTitle("Bills")
            .frame(minWidth: 850, minHeight: 650)
        }
        .environmentObject(paymentsStore)
    }
}
