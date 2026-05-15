//
//  Person.swift
//  camiana-budget
//
//  Created by Cameron Dudley on 3/23/26.
//

import Foundation

struct Person: Codable, Identifiable {
    let id: Int
    let name: String
    let payday: String
    let pay_schedule: String
    let anchor_date: String?
    let average_income: Double?
    let created_at: String?
}

struct AddPersonRequest: Codable {
    let name: String
    let payday: String
    let pay_schedule: String
    let anchor_date: String?
    let average_income: Double?
}

struct UpdatePersonRequest: Codable {
    let name: String
    let payday: String
    let pay_schedule: String
    let anchor_date: String?
    let average_income: Double?
}
