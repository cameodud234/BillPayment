//
//  SummariesAPIModels.swift
//  camiana-budget
//
//  Created by Cameron Dudley on 3/29/26.
//

import Foundation


struct NextPaydaySummaryResponse: Codable {
    let today: String
    let next_payday: String
    let your_payday: Bool
    let wife_payday: Bool
    let paycheck_count: Int
    let total_due: Double
    let payments: [Payment]
}
