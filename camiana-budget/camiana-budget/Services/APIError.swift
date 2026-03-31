//
//  APIError.swift
//  camiana-budget
//
//  Created by Cameron Dudley on 3/29/26.
//

import Foundation

enum APIServiceError: LocalizedError {
    case invalidURL
    case invalidResponse
    case serverError(String)
    case decodingError
    case encodingError

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid server URL."
        case .invalidResponse:
            return "Invalid response from server."
        case .serverError(let message):
            return message
        case .decodingError:
            return "Could not decode server response."
        case .encodingError:
            return "Could not encode request."
        }
    }
}
