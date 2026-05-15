//
//  BankAccount.swift
//  camiana-budget
//
//  Created by Cameron Dudley on 3/23/26.
//

import Foundation

enum AccountType: String, Codable, CaseIterable, Identifiable {
    case checking
    case savings
    case credit
    case cash
    case other

    var id: String { rawValue }
}

struct BankAccount: Codable, Identifiable {
    let id: Int
    let person_id: Int
    let name: String
    let account_type: AccountType
    let balance: Double
    let updated_at: String?
}

struct AddAccountRequest: Codable {
    let person_id: Int
    let name: String
    let account_type: AccountType
    let balance: Double
    let updated_at: String?
}

struct UpdateAccountRequest: Codable {
    let person_id: Int
    let name: String
    let account_type: AccountType
    let balance: Double
    let updated_at: String?
}

struct AccountsForPersonResponse: Codable {
    let status: String
    let accounts: [BankAccount]
}

struct TotalBalanceResponse: Codable {
    let status: String
    let person_id: Int
    let total_balance: Double
}
