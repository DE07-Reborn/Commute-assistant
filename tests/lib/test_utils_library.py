import pytest
from unittest.mock import patch, MagicMock

from src.lib.utils.library_api_utils import Library_api_collector

# --------------------------------------------------
# Fixtures
# --------------------------------------------------
@pytest.fixture
def env_library_key(monkeypatch):
    monkeypatch.setenv("LIBRARY_KEY", "test-library-key")

@pytest.fixture
def collector(env_library_key):
    return Library_api_collector("2025-12-12")


# --------------------------------------------------
# Success case
# --------------------------------------------------
@patch("src.lib.utils.library_api_utils.requests.get")
def test_request_loan_data_success(mock_get, collector):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "response": {
            "docs": [
                {"doc": {"bookname": "테스트 책", "loan_count": "10"}}
            ]
        }
    }

    mock_get.return_value = mock_response

    result = collector.request_loan_data()

    assert "response" in result
    assert len(result["response"]["docs"]) == 1
    assert result["response"]["docs"][0]["doc"]["bookname"] == "테스트 책"


# --------------------------------------------------
# Empty docs → ValueError
# --------------------------------------------------
@patch("src.lib.utils.library_api_utils.requests.get")
def test_request_loan_data_empty_docs(mock_get, collector):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "response": {
            "docs": []
        }
    }

    mock_get.return_value = mock_response

    with pytest.raises(ValueError, match="empty docs"):
        collector.request_loan_data()


# --------------------------------------------------
# Timeout
# --------------------------------------------------
@patch("src.lib.utils.library_api_utils.requests.get")
def test_request_loan_data_timeout(mock_get, collector):
    mock_get.side_effect = Exception("Timeout")

    with pytest.raises(Exception):
        collector.request_loan_data()


# --------------------------------------------------
# HTTP Error
# --------------------------------------------------
@patch("src.lib.utils.library_api_utils.requests.get")
def test_request_loan_data_http_error(mock_get, collector):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("HTTP Error")

    mock_get.return_value = mock_response

    with pytest.raises(Exception):
        collector.request_loan_data()


# --------------------------------------------------
# Missing environment variable
# --------------------------------------------------
def test_missing_library_key(monkeypatch):
    monkeypatch.delenv("LIBRARY_KEY", raising=False)

    with pytest.raises(EnvironmentError):
        Library_api_collector("2025-12-12")