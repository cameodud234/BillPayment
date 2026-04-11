//
//  Payment.swift
//  camiana-budget
//
//  Created by Cameron Dudley on 3/21/26.
//

import Foundation

struct Payment: Codable, Identifiable {
    let doc_id: Int
    let name: String
    let amount: Double
    let due_date: String
    let category: String?

    var id: Int { doc_id }
}
