//
//  APIErrorResponse.swift
//  camiana-budget
//
//  Created by Cameron Dudley on 3/29/26.
//

import Foundation

struct APIErrorResponse: Codable {
    let detail: String?
    let error: String?
}
