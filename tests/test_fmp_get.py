import pytest
import polars as pl
from fmpapi.fmp_get import fmp_get, convert_column_names, convert_column_types, perform_request

# Validation tests --------------------------------------------------------

def test_validate_limit():
    with pytest.raises(ValueError, match="Limit must be an integer larger than 0"):
        fmp_get(resource="balance-sheet-statement", symbol="AAPL", params={"limit": -1})
    
    with pytest.raises(ValueError, match="Limit must be an integer larger than 0"):
        fmp_get(resource="balance-sheet-statement", symbol="AAPL", params={"limit": "ten"})

def test_validate_period():
    with pytest.raises(ValueError, match="Period must be either 'annual' or 'quarter'"):
        fmp_get(resource="cash-flow-statement", symbol="AAPL", params={"period": "monthly"})

def test_validate_symbol():
    with pytest.raises(ValueError, match="Please provide a valid symbol."):
        fmp_get(resource="profile", symbol=["AAPL", "MSFT"])

# Request handling tests --------------------------------------------------

# import httpx
# from unittest.mock import patch
# def test_fmp_get_parses_response_without_symbol():
#     example_body = [
#         {
#             "symbol": "ABCX.US",
#             "name": "AlphaBeta Corporation",
#             "price": 152.35,
#             "exchange": "New York Stock Exchange",
#             "exchangeShortName": "NYSE",
#             "type": "stock",
#         },
#         {
#             "symbol": "GLOTECH.TO",
#             "name": "Global Technologies Inc.",
#             "price": 88.50,
#             "exchange": "Toronto Stock Exchange",
#             "exchangeShortName": "TSX",
#             "type": "stock",
#         },
#     ]

#     with patch("fmpapi.fmp_get.perform_request", return_value=example_body):
#         result = fmp_get(resource="stock/list")
#         assert isinstance(result, pl.DataFrame)

# def test_fmp_get_parses_response_with_symbol():
#     example_body = [
#         {
#             "date": "2024-09-28",
#             "symbol": "XYZC",
#             "reportedCurrency": "USD",
#             "cik": "0001234567",
#             "fillingDate": "2024-11-01",
#             "acceptedDate": "2024-11-01 06:01:36",
#             "calendarYear": "2024",
#             "period": "FY",
#             "cashAndCashEquivalents": 67890,
#         }
#     ]

#     with patch("your_module.perform_request", return_value=example_body):
#         result = fmp_get(resource="balance-sheet-statement", symbol="AAPL")
#         assert isinstance(result, pl.DataFrame)

# def test_perform_request_throws_error_on_non_200_response():
#     with patch("httpx.Client.get") as mock_get:
#         mock_get.return_value.status_code = 400
#         mock_get.return_value.json.return_value = {"error": "Invalid request"}
#         with pytest.raises(httpx.HTTPStatusError):
#             perform_request(resource="invalid-resource")

# def test_perform_request_handles_empty_response():
#     with patch("httpx.Client.get") as mock_get:
#         mock_get.return_value.status_code = 200
#         mock_get.return_value.json.return_value = []
#         with pytest.raises(ValueError, match="Response body is empty."):
#             perform_request(resource="invalid-resource")

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