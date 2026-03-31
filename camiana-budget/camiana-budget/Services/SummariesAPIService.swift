//
//  SummariesAPIService.swift
//  camiana-budget
//
//  Created by Cameron Dudley on 3/29/26.
//

import Foundation

import Foundation

final class SummariesAPIService {
    static let shared = SummariesAPIService()

    private init() {}

    func fetchNextPaydaySummary(today: String? = nil) async throws -> NextPaydaySummaryResponse {
        var urlString = "\(APIConfig.baseURL)/summaries/next-payday"

        if let today, !today.isEmpty {
            urlString += "?today=\(today)"
        }

        guard let url = URL(string: urlString) else {
            throw APIServiceError.invalidURL
        }

        let (data, response) = try await URLSession.shared.data(from: url)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIServiceError.invalidResponse
        }

        guard 200..<300 ~= httpResponse.statusCode else {
            throw try parseServerError(from: data)
        }

        do {
            return try JSONDecoder().decode(NextPaydaySummaryResponse.self, from: data)
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
