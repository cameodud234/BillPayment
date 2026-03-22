//
//  apiservice.swift
//  camiana-budget
//
//  Created by Cameron Dudley on 3/21/26.
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

final class APIService {
    static let shared = APIService()

    private let baseURL = "http://127.0.0.1:8000"

    private init() {}

    func fetchPayments() async throws -> [Payment] {
        guard let url = URL(string: "\(baseURL)/payments") else {
            throw APIServiceError.invalidURL
        }

        do {
            let (data, response) = try await URLSession.shared.data(from: url)

            print("RAW RESPONSE:")
            print(String(data: data, encoding: .utf8) ?? "No response body")
            print("URL RESPONSE:")
            print(response)

            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIServiceError.invalidResponse
            }

            guard 200..<300 ~= httpResponse.statusCode else {
                throw try parseServerError(from: data)
            }

            do {
                return try JSONDecoder().decode([Payment].self, from: data)
            } catch {
                print("DECODING ERROR:", error)
                throw APIServiceError.decodingError
            }
        } catch {
            print("NETWORK ERROR:", error)
            throw error
        }
    }

    func addPayment(_ requestBody: AddPaymentRequest) async throws {
        guard let url = URL(string: "\(baseURL)/add") else {
            throw APIServiceError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        do {
            request.httpBody = try JSONEncoder().encode(requestBody)
        } catch {
            throw APIServiceError.encodingError
        }

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIServiceError.invalidResponse
        }

        guard 200..<300 ~= httpResponse.statusCode else {
            throw try parseServerError(from: data)
        }
    }

    func calculateWeeklyBudget(payday: String) async throws -> WeeklyBudgetResponse {
        guard let url = URL(string: "\(baseURL)/weekly") else {
            throw APIServiceError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let body = WeeklyBudgetRequest(payday: payday)

        do {
            request.httpBody = try JSONEncoder().encode(body)
        } catch {
            throw APIServiceError.encodingError
        }

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIServiceError.invalidResponse
        }

        guard 200..<300 ~= httpResponse.statusCode else {
            throw try parseServerError(from: data)
        }

        do {
            return try JSONDecoder().decode(WeeklyBudgetResponse.self, from: data)
        } catch {
            throw APIServiceError.decodingError
        }
    }

    private func parseServerError(from data: Data) throws -> APIServiceError {
        if let apiError = try? JSONDecoder().decode(APIErrorResponse.self, from: data) {
            let message = apiError.detail ?? apiError.error ?? "Server error."
            return .serverError(message)
        }
        return .serverError("Server error.")
    }
}
