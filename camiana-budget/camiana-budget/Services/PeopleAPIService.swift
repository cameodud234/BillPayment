//
//  PeopleAPIService.swift
//  camiana-budget
//
//  Created by Cameron Dudley on 3/29/26.
//

import Foundation

final class PeopleAPIService {
    static let shared = PeopleAPIService()

    private init() {}

    func fetchPeople() async throws -> [Person] {
        let data = try await sendRequest(path: "/people")
        return try decode([Person].self, from: data)
    }

    func fetchPerson(id: Int) async throws -> Person {
        let data = try await sendRequest(path: "/people/\(id)")
        return try decode(Person.self, from: data)
    }

    func addPerson(_ requestBody: AddPersonRequest) async throws -> WriteResponse {
        let data = try await sendRequest(path: "/people", method: "POST", body: encode(requestBody))
        return try decode(WriteResponse.self, from: data)
    }

    func updatePerson(id: Int, requestBody: UpdatePersonRequest) async throws -> WriteResponse {
        let data = try await sendRequest(path: "/people/\(id)", method: "PUT", body: encode(requestBody))
        return try decode(WriteResponse.self, from: data)
    }

    func deletePerson(id: Int) async throws -> WriteResponse {
        let data = try await sendRequest(path: "/people/\(id)", method: "DELETE")
        return try decode(WriteResponse.self, from: data)
    }

    private func sendRequest(
        path: String,
        method: String = "GET",
        body: Data? = nil
    ) async throws -> Data {
        guard let url = URL(string: "\(APIConfig.baseURL)\(path)") else {
            throw APIServiceError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = method

        if let body {
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.httpBody = body
        }

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIServiceError.invalidResponse
        }

        guard 200..<300 ~= httpResponse.statusCode else {
            throw parseServerError(from: data)
        }

        return data
    }

    private func decode<T: Decodable>(_ type: T.Type, from data: Data) throws -> T {
        do {
            return try JSONDecoder().decode(type, from: data)
        } catch {
            throw APIServiceError.decodingError
        }
    }

    private func encode<T: Encodable>(_ value: T) throws -> Data {
        do {
            return try JSONEncoder().encode(value)
        } catch {
            throw APIServiceError.encodingError
        }
    }

    private func parseServerError(from data: Data) -> APIServiceError {
        if let apiError = try? JSONDecoder().decode(APIErrorResponse.self, from: data) {
            let message = apiError.detail?.message ?? apiError.error ?? "Server error."
            return .serverError(message)
        }

        return .serverError("Server error.")
    }
}
