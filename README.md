# py-fmpapi

Provides a flexible interface to the ['Financial Modeling Prep' API](https://site.financialmodelingprep.com/developer/docs). The package supports all available endpoints and parameters, enabling Python users to interact with a wide range of financial data.

This library is a product of Christoph Scheuch and not sponsored by or affiliated with FMP in any way. For an R implementation, please consider the [`r-fmpapi`](https://github.com/tidy-finance/r-fmpapi) package.

## Installation

You can install the development version from GitHub:

```r
pip install "git+https://github.com/tidy-finance/py-fmpapi"
```

## Setup

Before using the package, you need to set your Financial Modeling Prep API key. You can set it using the `fmp_set_api_key()` function, which saves the key to your `.Renviron` file for future use (either in your project or home folder).

```python
import from fmpapi fmp_set_api_key

fmp_set_api_key()
```

## Usage

Since the FMP API has a myriad of endpoints and parameters, the package provides a single function to handle requests: `fmp_get()`.

You can retrieve a company’s profile by providing its stock symbol to the `profile` endpoint:

```python
import from fmpapi fmp_get

fmp_get(resource = "profile", symbol = "AAPL")
```

To retrieve the balance sheet statements for a company, use the `balance-sheet-statement` endpoint. You can specify whether to retrieve annual or quarterly data using the `period` parameter and the number of records via `limit`. Note that you need a paid account for quarterly data. 

```python
fmp_get(resource = "balance-sheet-statement", symbol = "AAPL", params = {"period": "annual", "limit": 5})
```

The `income-statement` endpoint allows you to retrieve income statements for a specific stock symbol. 

```python
fmp_get(resource = "income-statement", symbol = "AAPL")
```

You can fetch cash flow statements using the `cash-flow-statement` endpoint.

```r
fmp_get(resource = "cash-flow-statement", symbol = "AAPL")
```

Most free endpoints live under API version 3, but you can also control the api version in `fmp_get()`, which you need for some paid endpoints. For instance, the `symbol_change` endpoint:

```python
fmp_get(resource = "symbol_change", api_version = "v4")
```

## Relation to Existing Libraries

There is an existing Python module that also provide an interface to the FMP API. However, the module lacks flexibility because it provides dedicated functions for specific endpoints, which means that users need to study both the FMP API docs and the package documentation and developers have to create new functions for each new endpoint. 

- [fmp-python](https://pypi.org/project/fmp-python/): last comupdated more than 3 years ago. 

## Contributing

Feel free to open issues or submit pull requests to improve the package. Contributions are welcome!

## License

This package is licensed under the MIT License.