import polars as pl
import httpx
import os
import re

def fmp_get(
    resource, 
    symbol=None, 
    params={},
    api_version="v3", 
    snake_case=True
    ):
    """
    Retrieve Financial Data from the Financial Modeling Prep (FMP) API

    This function fetches financial data from the FMP API, including 
    balance sheet statements, income statements, cash flow statements, 
    historical market data, stock lists, and company profiles.

    Parameters:
        resource (str):  A string indicating the API resource to query. Examples
            include `"balance-sheet-statement"`, `"income-statement"`, `"cash-flow-statement"`, 
            `"historical-market-capitalization"`, `"profile"`, and `"stock/list"`.
        symbol (str, optional): A string specifying the stock ticker symbol.
        params (dict, optional): Additional arguments to customize the query.
        api_version (strA string specifying the version of the FMP API to use. Defaults to `"v3"`.
        snake_case (bool, optional): A boolean indicating whether column names are converted
            to snake_case. Defaults to `True`.

    Returns:
        pl.DataFrame: A Polars DataFrame containing the processed financial data.

    Raises:
        ValueError: If the response is empty or invalid parameters are provided.

    Example:
        >>> fmp_get(resource = "balance-sheet-statement", symbol = "AAPL")
        >>> fmp_get(resource = "income-statement", symbol = "AAPL", params = {"limit": 1})
        >>> fmp_get(resource = "cash-flow-statement", symbol = "AAPL", params = {"period": "annual"})
        >>> fmp_get(resource = "historical-market-capitalization", symbol = "UNH", params = {"from": "2023-12-01", "to": "2023-12-31"})
        >>> fmp_get(resource = "stock/list")
        >>> fmp_get(resource = "profile", symbol = "AAPL")
        >>> fmp_get(resource = "search", params = {"query": "AAP"})
        >>> fmp_get(resource = "profile", symbol = "AAPL", snake_case = False)
    """
    if symbol:
        validate_symbol(symbol)
        resource = f"{resource}/{symbol}"
        
    if "limit" in params:
        validate_limit(params["limit"])
    if "period" in params:
        validate_period(params["period"])
        
    data_raw = perform_request(resource=resource, api_version=api_version, **params)
        
    if not data_raw:
        raise ValueError("Response body is empty. Check your resource and parameter specification.")
        
    data_processed = pl.DataFrame(data_raw)
    data_processed = convert_column_types(data_processed)
        
    if snake_case:
        data_processed = convert_column_names(data_processed)
        
    return data_processed

def perform_request(
    resource, 
    base_url="https://financialmodelingprep.com/api/", 
    api_version="v3", 
    **kwargs
    ):
    """
    Perform a GET request to the Financial Modeling Prep (FMP) API.

    Parameters:
        resource (str): The API resource to query (e.g., "profile", "balance-sheet-statement").
        base_url (str, optional): The base URL for the FMP API. Defaults to "https://financialmodelingprep.com/api/".
        api_version (str, optional): The version of the API to use. Defaults to "v3".
        **kwargs: Additional query parameters to include in the request.

    Returns:
        list: A list of parsed JSON objects from the API response.

    Raises:
        httpx.HTTPStatusError: If the HTTP request fails or returns an error status.
    """
    url = f"{base_url}{api_version}/{resource}"
    headers = {
        "User-Agent": "fmpapi Python package (https://github.com/tidy-finance/py-fmpapi)"
    }
    api_key = os.getenv("FMP_API_KEY")
    params = {"apikey": api_key, **kwargs}
        
    with httpx.Client() as client:
        response = client.get(url, headers=headers, params=params)
        response.raise_for_status()
        
    data = response.json()
    return data

def validate_symbol(symbol):
    """
    Validate the provided stock ticker symbol.

    Parameters:
        symbol (str): The stock ticker symbol to validate.

    Raises:
        ValueError: If the symbol is not a valid non-empty string.
    """
    if not isinstance(symbol, str) or len(symbol) == 0:
        raise ValueError("Please provide a valid symbol.")

def validate_period(period):
    """
    Validate the reporting period parameter.

    Parameters:
        period (str): The reporting period to validate ("annual" or "quarter").

    Raises:
        ValueError: If the period is not "annual" or "quarter".
    """
    if period not in ["annual", "quarter"]:
        raise ValueError("Period must be either 'annual' or 'quarter'.")
    
def validate_limit(limit):
    """
    Validate the limit parameter for API requests.

    Parameters:
        limit (int): The maximum number of results to retrieve.

    Raises:
        ValueError: If the limit is not a positive integer.
    """
    if not isinstance(limit, int) or limit < 1:
        raise ValueError("Limit must be an integer larger than 0.")

def convert_column_names(df):
    """
    Convert column names in a Polars DataFrame to snake_case.

    Parameters:
        df (pl.DataFrame): The input Polars DataFrame.

    Returns:
       pl.DataFrame: A Polars DataFrame with column names converted to snake_case.
    """
    df = df.rename({col: re.sub(r'([a-z])([A-Z])', r'\1_\2', col).lower() for col in df.columns})
    return df

def convert_column_types(df):
    """
    Convert column types in a Polars DataFrame.

    Parameters:
        df (pl.DataFrame): The input Polars DataFrame.

    Returns:
        pl.DataFrame: A DataFrame with converted column types.
    """
    for col in df.columns:
        if "Year" in col or "year" in col:
            df = df.with_columns(pl.col(col).cast(pl.Int32))
        if "Date" in col or "date" in col:
            try:
                df = df.with_columns(pl.col(col).str.to_date())
            except Exception:
                df = df.with_columns(pl.col(col).str.to_datetime()) 

    return df
