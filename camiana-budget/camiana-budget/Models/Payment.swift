//
//  Payment.swift
//  camiana-budget
//
//  Created by Cameron Dudley on 3/21/26.
//

import Foundation

struct Payment: Codable, Identifiable {
    let id: Int
    let name: String
    let amount: Double
    let due_date: String
    let category: PaymentCategory?
    let account_id: Int?
    let split_method: SplitMethod
    let is_recurring: Int
    let due_day: Int?
    let created_at: String?
}

struct PaymentAllocation: Codable, Identifiable {
    let id: Int
    let payment_id: Int
    let person_id: Int
    let share_percentage: Double?
    let allocated_amount: Double
}

struct PaymentAllocationsResponse: Codable {
    let status: String
    let payment_id: Int
    let allocations: [PaymentAllocation]
}
