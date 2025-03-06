# py-fmpapi
![PyPI](https://img.shields.io/pypi/v/fmpapi?label=pypi%20package)
![PyPI Downloads](https://img.shields.io/pypi/dm/fmpapi)
[![python-package.yml](https://github.com/tidy-finance/py-fmpapi/actions/workflows/python-package.yml/badge.svg)](https://github.com/tidy-finance/py-fmpapi/actions/workflows/python-package.yml)
[![codecov.yml](https://codecov.io/gh/tidy-finance/py-fmpapi/graph/badge.svg)](https://app.codecov.io/gh/tidy-finance/py-fmpapi)
[![License:
MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Provides a flexible Polars-based interface to the ['Financial Modeling Prep' API](https://site.financialmodelingprep.com/developer/docs). The package supports all available endpoints and parameters, enabling Python users to interact with a wide range of financial data.

> 💡 This package is developed by Christoph Scheuch and not sponsored by or affiliated with FMP. However, you can get **15% off** your FMP subscription by using [this affiliate link](https://site.financialmodelingprep.com/pricing-plans?couponCode=tidyfinance). By signing up through this link, you also support the development of this package at no extra cost to you.

For an R implementation, please consider the [`r-fmpapi`](https://github.com/tidy-finance/r-fmpapi) package.

## Installation

You can install the release version from PyPI: 

```
pip install fmpapi
```

If you want to use the package with `pandas`, then install via:

```
pip install fmpapi[pandas]
```

You can install the development version from GitHub:

```
pip install "git+https://github.com/tidy-finance/py-fmpapi"
```

## Setup

Before using the package, you need to set your Financial Modeling Prep API key. You can set it using the `fmp_set_api_key()` function, which saves the key to your `.env` file for future use (either in your project or home folder).

```python
from fmpapi import fmp_set_api_key

fmp_set_api_key()
```

## Usage

Since the FMP API has a myriad of endpoints and parameters, the package provides a single function to handle requests: `fmp_get()`.

You can retrieve a company’s profile by providing its stock symbol to the `profile` endpoint:

```python
from fmpapi import fmp_get

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

```python
fmp_get(resource = "cash-flow-statement", symbol = "AAPL")
```

Most free endpoints live under API version 3, but you can also control the api version in `fmp_get()`, which you need for some paid endpoints. For instance, the `symbol_change` endpoint:

```python
fmp_get(resource = "symbol_change", api_version = "v4")
```

If you want to get a `pandas` data frame instead of `polars`, you can use the `to_pandas` option (note that `pandas` and `pyarrow` must be installed):

```python
fmp_get(resource = "cash-flow-statement", symbol = "AAPL", to_pandas = True)
```

## Relation to Existing Libraries

There is an existing Python module that also provide an interface to the FMP API. However, the module lacks flexibility because it provides dedicated functions for specific endpoints, which means that users need to study both the FMP API docs and the package documentation and developers have to create new functions for each new endpoint. 

- [fmp-python](https://pypi.org/project/fmp-python/): last commit more than 3 years ago. 

## Contributing

Feel free to open issues or submit pull requests to improve the package. Contributions are welcome!

## License

This package is licensed under the MIT License.