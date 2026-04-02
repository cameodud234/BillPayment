//
//  PaymentCategory.swift
//  camiana-budget
//
//  Created by Cameron Dudley on 4/1/26.
//

import Foundation

enum PaymentCategory: String, Codable, CaseIterable, Identifiable {
    case housing = "Housing"
    case utilities = "Utilities"
    case groceries = "Groceries"
    case transportation = "Transportation"
    case entertainment = "Entertainment"
    case technology = "Technology"
    case education = "Education"
    case business = "Business"
    case other = "Other"

    var id: String { rawValue }
}
