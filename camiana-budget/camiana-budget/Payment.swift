//
//  payment.swift
//  camiana-budget
//
//  Created by Cameron Dudley on 3/21/26.
//

import Foundation

struct Payment: Codable, Identifiable {
    let id: Int?
    let doc_id: Int?
    let name: String
    let amount: Double
    let due_date: String
    let category: String?

    var stableID: Int {
        doc_id ?? id ?? Int.random(in: 100000...999999)
    }

    var identifier: Int { stableID }
}
