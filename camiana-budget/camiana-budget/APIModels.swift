//
//  apimodels.swift
//  camiana-budget
//
//  Created by Cameron Dudley on 3/21/26.
//

import Foundation

struct AddPaymentRequest: Codable {
    let name: String
    let amount: Double
    let due_date: String
    let category: String
}

struct NextPaydaySummaryResponse: Codable {
    let today: String
    let next_payday: String
    let your_payday: Bool
    let wife_payday: Bool
    let paycheck_count: Int
    let total_due: Double
    let payments: [Payment]
}

struct WeeklyBudgetRequest: Codable {
    let payday: String
}

struct WeeklyBudgetResponse: Codable {
    let total: Double
    let payments: [Payment]
}

struct APIErrorResponse: Codable {
    let detail: String?
    let error: String?
}
