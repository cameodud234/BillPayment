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

    func addPayment(_ requestBody: AddPaymentRequest) async throws -> WriteResponse {
        guard let url = URL(string: "\(APIConfig.baseURL)/payments") else {
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

        do {
            return try JSONDecoder().decode(WriteResponse.self, from: data)
        } catch {
            throw APIServiceError.decodingError
        }
    }

    func updatePayment(id: Int, requestBody: UpdatePaymentRequest) async throws -> WriteResponse {
        guard let url = URL(string: "\(APIConfig.baseURL)/payments/\(id)") else {
            throw APIServiceError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "PUT"
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

        do {
            return try JSONDecoder().decode(WriteResponse.self, from: data)
        } catch {
            throw APIServiceError.decodingError
        }
    }

    func deletePayment(id: Int) async throws -> WriteResponse {
        guard let url = URL(string: "\(APIConfig.baseURL)/payments/\(id)") else {
            throw APIServiceError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "DELETE"

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIServiceError.invalidResponse
        }

        guard 200..<300 ~= httpResponse.statusCode else {
            throw try parseServerError(from: data)
        }

        do {
            return try JSONDecoder().decode(WriteResponse.self, from: data)
        } catch {
            throw APIServiceError.decodingError
        }
    }

    func fetchAllocations(paymentID: Int) async throws -> [PaymentAllocation] {
        guard let url = URL(string: "\(APIConfig.baseURL)/payments/\(paymentID)/allocations") else {
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
            return try JSONDecoder().decode(PaymentAllocationsResponse.self, from: data).allocations
        } catch {
            throw APIServiceError.decodingError
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
            let message = apiError.detail?.message ?? apiError.error ?? "Server error."
            return .serverError(message)
        }
        return .serverError("Server error.")
    }
}
