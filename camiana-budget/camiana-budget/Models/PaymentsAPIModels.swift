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
    let participant_ids: [Int]
    let split_method: SplitMethod
    let is_recurring: Bool
    let due_day: Int?
}

struct UpdatePaymentRequest: Codable {
    let name: String
    let amount: Double
    let due_date: String
    let category: String
    let account_id: Int?
    let participant_ids: [Int]
    let split_method: SplitMethod
    let is_recurring: Bool
    let due_day: Int?
}

struct WriteResponse: Codable {
    let status: String
    let id: Int?
    let updated_id: Int?
    let deleted_id: Int?
}

struct WeeklyBudgetRequest: Codable {
    let payday: String
}

struct WeeklyBudgetResponse: Codable {
    let status: String
    let total: Double
    let payments: [Payment]
}
