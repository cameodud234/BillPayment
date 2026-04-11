import Foundation

final class PaymentsAPIService {
    static let shared = PaymentsAPIService()

    private init() {}

    func fetchPayments() async throws -> [Payment] {
        guard let url = URL(string: "\(APIConfig.baseURL)/payments") else {
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
            return try JSONDecoder().decode([Payment].self, from: data)
        } catch {
            throw APIServiceError.decodingError
        }
    }

    func addPayment(_ requestBody: AddPaymentRequest) async throws {
        guard let url = URL(string: "\(APIConfig.baseURL)/payments") else {
            throw APIServiceError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        do {
            request.httpBody = try JSONEncoder().encode(requestBody)
            print("POST BODY:", String(data: request.httpBody!, encoding: .utf8)!)
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
        guard let url = URL(string: "\(APIConfig.baseURL)/payments/weekly") else {
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
