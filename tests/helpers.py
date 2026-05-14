def assert_service_error(result, code, message=None, status_code=None):
    assert result["status"] == "error"
    assert "error" in result
    assert result["error"]["code"] == code

    if message is not None:
        assert result["error"]["message"] == message

    if status_code is not None:
        assert result["error"]["status_code"] == status_code


def assert_route_error(response, status_code, code, message=None):
    assert response.status_code == status_code

    body = response.json()
    assert "detail" in body
    assert body["detail"]["code"] == code

    if message is not None:
        assert body["detail"]["message"] == message