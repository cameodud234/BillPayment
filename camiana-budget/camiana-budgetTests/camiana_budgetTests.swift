//
//  camiana_budgetTests.swift
//  camiana-budgetTests
//
//  Created by Cameron Dudley on 3/21/26.
//

import XCTest
@testable import camiana_budget

final class camiana_budgetTests: XCTestCase {

    private let liveBaseURL = URL(string: "http://localhost:8000")!
    private let decoder = JSONDecoder()
    private let encoder = JSONEncoder()

    func testPaymentDecodesFromBackendSchema() throws {
        let json = """
        {
            "id": 42,
            "name": "Rent",
            "amount": 2500.0,
            "due_date": "2026-05-20",
            "category": "Housing",
            "account_id": 7,
            "split_method": "income_ratio",
            "is_recurring": 0,
            "due_day": null,
            "created_at": "2026-05-14 10:00:00"
        }
        """.data(using: .utf8)!

        let payment = try decoder.decode(Payment.self, from: json)

        XCTAssertEqual(payment.id, 42)
        XCTAssertEqual(payment.name, "Rent")
        XCTAssertEqual(payment.amount, 2500.0)
        XCTAssertEqual(payment.due_date, "2026-05-20")
        XCTAssertEqual(payment.category, .housing)
        XCTAssertEqual(payment.account_id, 7)
        XCTAssertEqual(payment.split_method, .incomeRatio)
        XCTAssertEqual(payment.is_recurring, 0)
        XCTAssertNil(payment.due_day)
        XCTAssertEqual(payment.created_at, "2026-05-14 10:00:00")
    }

    func testAddPaymentRequestEncodesRequiredParticipantAndSplitFields() throws {
        let request = AddPaymentRequest(
            name: "Internet",
            amount: 100,
            due_date: "2026-05-20",
            category: PaymentCategory.utilities.rawValue,
            account_id: 1,
            participant_ids: [1, 2],
            split_method: .equal,
            is_recurring: false,
            due_day: nil
        )

        let json = try encodedJSONObject(request)

        XCTAssertEqual(json["name"] as? String, "Internet")
        XCTAssertEqual(json["amount"] as? Double, 100)
        XCTAssertEqual(json["due_date"] as? String, "2026-05-20")
        XCTAssertEqual(json["category"] as? String, "Utilities")
        XCTAssertEqual(json["account_id"] as? Int, 1)
        XCTAssertEqual(json["participant_ids"] as? [Int], [1, 2])
        XCTAssertEqual(json["split_method"] as? String, "equal")
        XCTAssertEqual(json["is_recurring"] as? Bool, false)
        XCTAssertNil(json["due_day"])
    }

    func testRecurringPaymentRequestEncodesBoolAndDueDay() throws {
        let request = AddPaymentRequest(
            name: "Rent",
            amount: 2500,
            due_date: "2026-05-01",
            category: PaymentCategory.housing.rawValue,
            account_id: nil,
            participant_ids: [1],
            split_method: .incomeRatio,
            is_recurring: true,
            due_day: 1
        )

        let json = try encodedJSONObject(request)

        XCTAssertNil(json["account_id"])
        XCTAssertEqual(json["participant_ids"] as? [Int], [1])
        XCTAssertEqual(json["split_method"] as? String, "income_ratio")
        XCTAssertEqual(json["is_recurring"] as? Bool, true)
        XCTAssertEqual(json["due_day"] as? Int, 1)
    }

    func testPaymentAllocationResponseDecodes() throws {
        let json = """
        {
            "status": "ok",
            "payment_id": 42,
            "allocations": [
                {
                    "id": 1,
                    "payment_id": 42,
                    "person_id": 1,
                    "share_percentage": 40.0,
                    "allocated_amount": 1000.0
                },
                {
                    "id": 2,
                    "payment_id": 42,
                    "person_id": 2,
                    "share_percentage": 60.0,
                    "allocated_amount": 1500.0
                }
            ]
        }
        """.data(using: .utf8)!

        let response = try decoder.decode(PaymentAllocationsResponse.self, from: json)

        XCTAssertEqual(response.status, "ok")
        XCTAssertEqual(response.payment_id, 42)
        XCTAssertEqual(response.allocations.count, 2)
        XCTAssertEqual(response.allocations[0].person_id, 1)
        XCTAssertEqual(response.allocations[0].share_percentage, 40.0)
        XCTAssertEqual(response.allocations[0].allocated_amount, 1000.0)
        XCTAssertEqual(response.allocations[1].person_id, 2)
        XCTAssertEqual(response.allocations[1].share_percentage, 60.0)
        XCTAssertEqual(response.allocations[1].allocated_amount, 1500.0)
    }

    func testStructuredAPIErrorResponseDecodes() throws {
        let json = """
        {
            "detail": {
                "code": "PERSON_ACCOUNT_EXISTS",
                "message": "This person already has an account"
            }
        }
        """.data(using: .utf8)!

        let response = try decoder.decode(APIErrorResponse.self, from: json)

        XCTAssertEqual(response.detail?.code, "PERSON_ACCOUNT_EXISTS")
        XCTAssertEqual(response.detail?.message, "This person already has an account")
        XCTAssertNil(response.error)
    }

    func testLegacyStringAPIErrorResponseStillDecodes() throws {
        let json = """
        {
            "detail": "Payment not found"
        }
        """.data(using: .utf8)!

        let response = try decoder.decode(APIErrorResponse.self, from: json)

        XCTAssertNil(response.detail?.code)
        XCTAssertEqual(response.detail?.message, "Payment not found")
    }

    func testPersonDecodesFromBackendSchema() throws {
        let json = """
        {
            "id": 1,
            "name": "Cameron",
            "payday": "Friday",
            "pay_schedule": "weekly",
            "anchor_date": null,
            "average_income": 1000.0,
            "created_at": "2026-05-14 10:00:00"
        }
        """.data(using: .utf8)!

        let person = try decoder.decode(Person.self, from: json)

        XCTAssertEqual(person.id, 1)
        XCTAssertEqual(person.name, "Cameron")
        XCTAssertEqual(person.payday, "Friday")
        XCTAssertEqual(person.pay_schedule, "weekly")
        XCTAssertNil(person.anchor_date)
        XCTAssertEqual(person.average_income, 1000.0)
        XCTAssertEqual(person.created_at, "2026-05-14 10:00:00")
    }

    func testBankAccountDecodesFromBackendSchema() throws {
        let json = """
        {
            "id": 7,
            "person_id": 1,
            "name": "Bills Checking",
            "account_type": "checking",
            "balance": 2500.0,
            "updated_at": "2026-05-14"
        }
        """.data(using: .utf8)!

        let account = try decoder.decode(BankAccount.self, from: json)

        XCTAssertEqual(account.id, 7)
        XCTAssertEqual(account.person_id, 1)
        XCTAssertEqual(account.name, "Bills Checking")
        XCTAssertEqual(account.account_type, .checking)
        XCTAssertEqual(account.balance, 2500.0)
        XCTAssertEqual(account.updated_at, "2026-05-14")
    }

    func testAddAccountRequestEncodesOneAccountPerPersonShape() throws {
        let request = AddAccountRequest(
            person_id: 1,
            name: "Bills Checking",
            account_type: .checking,
            balance: 2500,
            updated_at: "2026-05-14"
        )

        let json = try encodedJSONObject(request)

        XCTAssertEqual(json["person_id"] as? Int, 1)
        XCTAssertEqual(json["name"] as? String, "Bills Checking")
        XCTAssertEqual(json["account_type"] as? String, "checking")
        XCTAssertEqual(json["balance"] as? Double, 2500)
        XCTAssertEqual(json["updated_at"] as? String, "2026-05-14")
    }

    func testWeeklyBudgetResponseDecodesStatusAndPayments() throws {
        let json = """
        {
            "status": "ok",
            "total": 100.0,
            "payments": [
                {
                    "id": 3,
                    "name": "Internet",
                    "amount": 100.0,
                    "due_date": "2026-05-20",
                    "category": "Utilities",
                    "account_id": null,
                    "split_method": "equal",
                    "is_recurring": 0,
                    "due_day": null,
                    "created_at": "2026-05-14 10:00:00"
                }
            ]
        }
        """.data(using: .utf8)!

        let response = try decoder.decode(WeeklyBudgetResponse.self, from: json)

        XCTAssertEqual(response.status, "ok")
        XCTAssertEqual(response.total, 100.0)
        XCTAssertEqual(response.payments.count, 1)
        XCTAssertEqual(response.payments[0].id, 3)
        XCTAssertEqual(response.payments[0].category, .utilities)
    }

    func testLiveServerRootResponds() async throws {
        let (data, response) = try await URLSession.shared.data(from: liveBaseURL)

        let httpResponse = try XCTUnwrap(response as? HTTPURLResponse)
        XCTAssertEqual(httpResponse.statusCode, 200)

        let json = try jsonObject(from: data)
        XCTAssertEqual(json["message"] as? String, "Backend is running")
    }

    func testLiveServerNextPaydaySummaryResponds() async throws {
        let data = try await get(path: "/summaries/next-payday?today=2026-05-14")
        let summary = try decoder.decode(NextPaydaySummaryResponse.self, from: data)

        XCTAssertEqual(summary.status, "ok")
        XCTAssertEqual(summary.today, "2026-05-14")
        XCTAssertEqual(summary.next_payday, "2026-05-15")
        XCTAssertEqual(summary.total_due, 0)
    }

    func testLiveServerCanCreateSplitPaymentAndFetchAllocations() async throws {
        let suffix = UUID().uuidString
        let firstPerson = try await post(
            path: "/people",
            body: AddPersonRequest(
                name: "XCTest Cameron \(suffix)",
                payday: "Friday",
                pay_schedule: "weekly",
                anchor_date: nil,
                average_income: 1000
            )
        )
        let secondPerson = try await post(
            path: "/people",
            body: AddPersonRequest(
                name: "XCTest Partner \(suffix)",
                payday: "Friday",
                pay_schedule: "weekly",
                anchor_date: nil,
                average_income: 1500
            )
        )

        let firstPersonID = try XCTUnwrap(firstPerson["id"] as? Int)
        let secondPersonID = try XCTUnwrap(secondPerson["id"] as? Int)

        let account = try await post(
            path: "/accounts",
            body: AddAccountRequest(
                person_id: firstPersonID,
                name: "XCTest Checking \(suffix)",
                account_type: .checking,
                balance: 2500,
                updated_at: "2026-05-14"
            )
        )
        let accountID = try XCTUnwrap(account["id"] as? Int)

        let payment = try await post(
            path: "/payments",
            body: AddPaymentRequest(
                name: "XCTest Rent \(suffix)",
                amount: 2500,
                due_date: "2026-05-20",
                category: PaymentCategory.housing.rawValue,
                account_id: accountID,
                participant_ids: [firstPersonID, secondPersonID],
                split_method: .incomeRatio,
                is_recurring: false,
                due_day: nil
            )
        )
        let paymentID = try XCTUnwrap(payment["id"] as? Int)

        let allocationsData = try await get(path: "/payments/\(paymentID)/allocations")
        let allocationsResponse = try decoder.decode(PaymentAllocationsResponse.self, from: allocationsData)

        XCTAssertEqual(allocationsResponse.status, "ok")
        XCTAssertEqual(allocationsResponse.payment_id, paymentID)
        XCTAssertEqual(allocationsResponse.allocations.count, 2)
        XCTAssertEqual(
            allocationsResponse.allocations.reduce(0) { $0 + $1.allocated_amount },
            2500,
            accuracy: 0.01
        )

        _ = try await delete(path: "/payments/\(paymentID)")
        _ = try await delete(path: "/people/\(firstPersonID)")
        _ = try await delete(path: "/people/\(secondPersonID)")
    }

    func testLiveServerReturnsStructuredDuplicateAccountError() async throws {
        let suffix = UUID().uuidString
        let person = try await post(
            path: "/people",
            body: AddPersonRequest(
                name: "XCTest Duplicate Account \(suffix)",
                payday: "Friday",
                pay_schedule: "weekly",
                anchor_date: nil,
                average_income: 1000
            )
        )
        let personID = try XCTUnwrap(person["id"] as? Int)

        _ = try await post(
            path: "/accounts",
            body: AddAccountRequest(
                person_id: personID,
                name: "XCTest First Checking \(suffix)",
                account_type: .checking,
                balance: 100,
                updated_at: "2026-05-14"
            )
        )

        let duplicateResponse = try await postExpectingError(
            path: "/accounts",
            body: AddAccountRequest(
                person_id: personID,
                name: "XCTest Second Checking \(suffix)",
                account_type: .savings,
                balance: 200,
                updated_at: "2026-05-14"
            )
        )

        XCTAssertEqual(duplicateResponse.statusCode, 409)
        XCTAssertEqual(duplicateResponse.error.detail?.code, "PERSON_ACCOUNT_EXISTS")
        XCTAssertEqual(duplicateResponse.error.detail?.message, "This person already has an account")

        _ = try await delete(path: "/people/\(personID)")
    }

    private func encodedJSONObject<T: Encodable>(_ value: T) throws -> [String: Any] {
        let data = try encoder.encode(value)
        let object = try JSONSerialization.jsonObject(with: data)
        return try XCTUnwrap(object as? [String: Any])
    }

    private func get(path: String) async throws -> Data {
        let url = try url(for: path)
        let (data, response) = try await URLSession.shared.data(from: url)
        let httpResponse = try XCTUnwrap(response as? HTTPURLResponse)
        XCTAssertTrue(200..<300 ~= httpResponse.statusCode, "Expected success, got \(httpResponse.statusCode): \(String(data: data, encoding: .utf8) ?? "")")
        return data
    }

    private func post<T: Encodable>(path: String, body: T) async throws -> [String: Any] {
        let data = try await send(path: path, method: "POST", body: body, expectedStatusCodes: 200..<300)
        return try jsonObject(from: data)
    }

    private func delete(path: String) async throws -> [String: Any] {
        let data = try await send(path: path, method: "DELETE", body: Optional<String>.none, expectedStatusCodes: 200..<300)
        return try jsonObject(from: data)
    }

    private func postExpectingError<T: Encodable>(
        path: String,
        body: T
    ) async throws -> (statusCode: Int, error: APIErrorResponse) {
        let (data, statusCode) = try await sendForStatus(path: path, method: "POST", body: body)
        XCTAssertFalse(200..<300 ~= statusCode)
        return (statusCode, try decoder.decode(APIErrorResponse.self, from: data))
    }

    private func send<T: Encodable>(
        path: String,
        method: String,
        body: T?,
        expectedStatusCodes: Range<Int>
    ) async throws -> Data {
        let (data, statusCode) = try await sendForStatus(path: path, method: method, body: body)
        XCTAssertTrue(expectedStatusCodes ~= statusCode, "Expected \(expectedStatusCodes), got \(statusCode): \(String(data: data, encoding: .utf8) ?? "")")
        return data
    }

    private func sendForStatus<T: Encodable>(
        path: String,
        method: String,
        body: T?
    ) async throws -> (Data, Int) {
        let url = try url(for: path)
        var request = URLRequest(url: url)
        request.httpMethod = method

        if let body {
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.httpBody = try encoder.encode(body)
        }

        let (data, response) = try await URLSession.shared.data(for: request)
        let httpResponse = try XCTUnwrap(response as? HTTPURLResponse)
        return (data, httpResponse.statusCode)
    }

    private func url(for path: String) throws -> URL {
        let normalizedPath = path.hasPrefix("/") ? path : "/\(path)"
        return try XCTUnwrap(URL(string: "\(liveBaseURL.absoluteString)\(normalizedPath)"))
    }

    private func jsonObject(from data: Data) throws -> [String: Any] {
        let object = try JSONSerialization.jsonObject(with: data)
        return try XCTUnwrap(object as? [String: Any])
    }
}
