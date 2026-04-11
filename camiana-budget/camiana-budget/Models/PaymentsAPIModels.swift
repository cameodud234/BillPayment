//
//  PaymentsAPIModels.swift
//  camiana-budget
//
//  Created by Cameron Dudley on 3/29/26.
//

import Foundation

struct AddPaymentRequest: Codable {
    let name: String
    let amount: Double
    let due_date: String
    let category: String
    let account_id: Int?
    let is_recurring: Int
    let due_day: Int?
}

struct WeeklyBudgetRequest: Codable {
    let payday: String
}

struct WeeklyBudgetResponse: Codable {
    let total: Double
    let payments: [Payment]
}
