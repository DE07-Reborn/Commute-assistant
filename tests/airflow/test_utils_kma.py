import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import requests

from src.airflow.plugins.utils.kma_api_utils import kma_api_collector

# -----------------------------------------------------
# Fixtures
# -----------------------------------------------------
@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv("KMA_KEY", "dummy_kma_key")


@pytest.fixture
def collector():
    return kma_api_collector("2025-12-12", "1200")


# -----------------------------------------------------
# STN Metadata Test
# -----------------------------------------------------
@patch('requests.get')
def test_reqeust_stn_metadata_success(mock_get, collector):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.text = (
        "# comment\n"
        "108 127.0 37.0 1 x x x x x x 서울\n"
        "109 128.0 36.0 1 x x x x x x 부산\n"
    )

    mock_get.return_value = mock_response

    df = collector.request_stn_metadata()

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == ["STN_ID", "경도", "위도", "STN_SP", "지역"]
    assert df.iloc[0]["STN_ID"] == 108
    assert df.iloc[1]["지역"] == "부산"


@patch("requests.get")
def test_request_stn_metadata_empty(mock_get, collector):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.text = "# only comment\n"

    mock_get.return_value = mock_response

    with pytest.raises(ValueError):
        collector.request_stn_metadata()


# -----------------------------------------------------
# Daily weather Test
# -----------------------------------------------------
@patch("requests.get")
def test_request_daily_weather_success(mock_get, collector):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None

    mock_response.text = (
        "# header\n"
        "20251212 108 " + " ".join(str(i) for i in range(1, 60))
    )

    mock_get.return_value = mock_response

    df = collector.request_daily_weather(stn=108)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert "STN" in df.columns
    assert df.iloc[0]["STN"] == "108"


@patch("requests.get")
def test_request_daily_weather_empty(mock_get, collector):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.text = "# only comment\n"

    mock_get.return_value = mock_response

    with pytest.raises(ValueError):
        collector.request_daily_weather()



# -----------------------------------------------------
# Exception Test
# -----------------------------------------------------
@patch("requests.get")
def test_request_daily_weather_timeout(mock_get, collector):
    mock_get.side_effect = requests.Timeout

    with pytest.raises(requests.Timeout):
        collector.request_daily_weather()


@patch("requests.get")
def test_request_daily_weather_http_error(mock_get, collector):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("403 Forbidden")
    mock_get.return_value = mock_response

    with pytest.raises(requests.HTTPError):
        collector.request_daily_weather()


# -----------------------------------------------------
# Exception Test
# -----------------------------------------------------

def test_kma_key_not_set(monkeypatch):
    monkeypatch.delenv("KMA_KEY", raising=False)

    with pytest.raises(EnvironmentError):
        kma_api_collector("2025-12-12", "1200")









