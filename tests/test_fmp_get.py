import httpx
import pandas as pd
import polars as pl
import pytest
from pytest_httpx import HTTPXMock

from fmpapi.fmp_get import (
    build_base_url,
    build_resource,
    convert_column_names,
    convert_column_types,
    fmp_get,
    is_module_available,
    perform_request,
)

# Validation tests --------------------------------------------------------


def test_validate_limit():
    with pytest.raises(ValueError, match="Limit must be an integer larger than 0"):
        fmp_get(resource="balance-sheet-statement", symbol="AAPL", params={"limit": -1})

    with pytest.raises(ValueError, match="Limit must be an integer larger than 0"):
        fmp_get(
            resource="balance-sheet-statement", symbol="AAPL", params={"limit": "ten"}
        )


def test_validate_period():
    with pytest.raises(ValueError, match="Period must be either 'annual' or 'quarter'"):
        fmp_get(
            resource="cash-flow-statement", symbol="AAPL", params={"period": "monthly"}
        )


def test_validate_symbol():
    with pytest.raises(ValueError, match="Please provide a valid symbol."):
        fmp_get(resource="profile", symbol=["AAPL", "MSFT"])


# Request handling tests --------------------------------------------------


def test_fmp_get_parses_response_without_symbol(httpx_mock: HTTPXMock):
    example_body = [
        {
            "symbol": "ABCX.US",
            "name": "AlphaBeta Corporation",
            "price": 152.35,
            "exchange": "New York Stock Exchange",
            "exchangeShortName": "NYSE",
            "type": "stock",
        },
        {
            "symbol": "GLOTECH.TO",
            "name": "Global Technologies Inc.",
            "price": 88.50,
            "exchange": "Toronto Stock Exchange",
            "exchangeShortName": "TSX",
            "type": "stock",
        },
    ]

    httpx_mock.add_response(json=example_body)

    with httpx.Client() as client:
        result = fmp_get(resource="stock/list")
        assert isinstance(result, pl.DataFrame)
        assert result.shape == (2, len(example_body[0]))


def test_fmp_get_parses_response_with_symbol(httpx_mock: HTTPXMock):
    example_body = [
        {
            "date": "2024-09-28",
            "symbol": "XYZC",
            "reportedCurrency": "USD",
            "cik": "0001234567",
            "fillingDate": "2024-11-01",
            "acceptedDate": "2024-11-01 06:01:36",
            "calendarYear": "2024",
            "period": "FY",
            "cashAndCashEquivalents": 67890,
        }
    ]

    httpx_mock.add_response(json=example_body)

    with httpx.Client() as client:
        result = fmp_get(resource="balance-sheet-statement", symbol="AAPL")
        assert isinstance(result, pl.DataFrame)
        assert result.shape == (1, 9)


def test_perform_request_throws_error_on_non_200_response(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=400, json={"error": "Invalid request"})

    with httpx.Client() as client:
        with pytest.raises(httpx.HTTPStatusError):
            perform_request(resource="invalid-resource")


def test_perform_request_handles_empty_response(httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=[])

    with httpx.Client() as client:
        with pytest.raises(ValueError, match="Response body is empty."):
            fmp_get(resource="invalid-resource")


# Conversion tests --------------------------------------------------------


def test_convert_column_names():
    df = pl.DataFrame(
        {
            "calendarYear": [2023],
            "Date": ["2023-12-31"],
            "SymbolName": ["AAPL"],
        }
    )
    df_converted = convert_column_names(df)
    assert df_converted.columns == ["calendar_year", "date", "symbol_name"]


def test_convert_column_types():
    df = pl.DataFrame(
        {
            "calendarYear": ["2023", "2022"],
            "date": ["2023-12-31", "2022-12-31"],
            "value": [12345, 54321],
        }
    )
    df_converted = convert_column_types(df)
    assert df_converted.schema["calendarYear"] == pl.Int32
    assert df_converted.schema["date"] == pl.Date
    assert df_converted.schema["value"] == pl.Int64


# Pandas conversion test ---------------------------------------------------


def test_fmp_get_returns_pandas_data_frame(httpx_mock: HTTPXMock):
    example_body = [
        {
            "date": "2024-09-28",
            "symbol": "ABC",
            "reportedCurrency": "USD",
            "cik": "0001234567",
            "fillingDate": "2024-11-01",
            "acceptedDate": "2024-11-01 06:01:36",
            "calendarYear": "2024",
            "period": "FY",
            "cashAndCashEquivalents": 67890,
        }
    ]

    httpx_mock.add_response(json=example_body)

    with httpx.Client() as client:
        result = fmp_get(
            resource="balance-sheet-statement", symbol="AAPL", to_pandas=True
        )
        assert isinstance(result, pd.DataFrame)


def test_is_module_available_true():
    result = is_module_available("polars")
    assert result == True


def test_is_module_available_false():
    result = is_module_available("xxx")
    assert result == False


def test_build_base_url_appends_api_for_v123():
    assert build_base_url("https://ex.com/", "v2") == "https://ex.com/api/"


def test_build_base_url_preserves_slashes_and_duplicates():
    # No trailing slash: function does NOT insert one before 'api/'
    assert build_base_url("https://ex.com", "v1") == "https://ex.comapi/"
    # Trailing slash remains a single slash
    assert build_base_url("https://ex.com/", "v1") == "https://ex.com/api/"
    # If 'api/' already present, it will be duplicated when condition is true
    assert build_base_url("https://ex.com/api/", "v1") == "https://ex.com/api/api/"


def test_build_resource_symbol_none_no_validation_called():
    # Should return resource unchanged for both stable and non-stable
    assert build_resource("users", None, "stable") == "users"
    assert build_resource("users", None, "v3") == "users"


def test_build_resource_stable_with_symbol_validates_but_returns_resource():
    out = build_resource("users", "AAPL", "stable")
    assert out == "users"


def test_build_resource_nonstable_with_symbol_validates_and_appends():
    out = build_resource("users", "AAPL", "v3")
    assert out == "users/AAPL"


def test_build_resource_trailing_slash_is_not_normalized():
    # Current behavior: keep existing trailing slash, leading to double slash
    out = build_resource("users/", "AAPL", "v3")
    assert out == "users//AAPL"
