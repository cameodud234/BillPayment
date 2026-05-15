//
//  APIErrorResponse.swift
//  camiana-budget
//
//  Created by Cameron Dudley on 3/29/26.
//

import Foundation

struct APIErrorResponse: Decodable {
    let detail: APIErrorDetail?
    let error: String?

    private enum CodingKeys: String, CodingKey {
        case detail
        case error
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        error = try container.decodeIfPresent(String.self, forKey: .error)

        if let detailObject = try? container.decode(APIErrorDetail.self, forKey: .detail) {
            detail = detailObject
        } else if let detailMessage = try? container.decode(String.self, forKey: .detail) {
            detail = APIErrorDetail(code: nil, message: detailMessage)
        } else {
            detail = nil
        }
    }
}

struct APIErrorDetail: Decodable {
    let code: String?
    let message: String
}
