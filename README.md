[![](https://img.shields.io/pypi/pyversions/python-codicefiscale.svg?logoColor=white&color=blue&logo=python)](https://www.python.org/)
[![](https://img.shields.io/pypi/v/python-codicefiscale.svg?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/python-codicefiscale/)
[![](https://static.pepy.tech/badge/python-codicefiscale/month)](https://pepy.tech/project/python-codicefiscale)
[![](https://img.shields.io/github/stars/fabiocaccamo/python-codicefiscale?logo=github&style=flat)](https://github.com/fabiocaccamo/python-codicefiscale/stargazers)
[![](https://img.shields.io/pypi/l/python-codicefiscale.svg?color=blue&)](https://github.com/fabiocaccamo/python-codicefiscale/blob/main/LICENSE)

[![](https://results.pre-commit.ci/badge/github/fabiocaccamo/python-codicefiscale/main.svg)](https://results.pre-commit.ci/latest/github/fabiocaccamo/python-codicefiscale/main)
[![](https://img.shields.io/github/actions/workflow/status/fabiocaccamo/python-codicefiscale/test-package.yml?branch=main&label=build&logo=github)](https://github.com/fabiocaccamo/python-codicefiscale)
[![](https://img.shields.io/codecov/c/gh/fabiocaccamo/python-codicefiscale?logo=codecov)](https://codecov.io/gh/fabiocaccamo/python-codicefiscale)
[![](https://img.shields.io/codacy/grade/8927f48c9498408f85167da9287edd86?logo=codacy)](https://www.codacy.com/app/fabiocaccamo/python-codicefiscale)
[![](https://img.shields.io/scrutinizer/quality/g/fabiocaccamo/python-codicefiscale?logo=scrutinizer)](https://scrutinizer-ci.com/g/fabiocaccamo/python-codicefiscale/?branch=main)
[![](https://img.shields.io/badge/code%20style-black-000000.svg?logo=python&logoColor=black)](https://github.com/psf/black)
[![](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

# python-codicefiscale
python-codicefiscale is a library for encode/decode Italian fiscal code - **codifica/decodifica del Codice Fiscale**.

![Codice Fiscale](https://user-images.githubusercontent.com/1035294/72058207-fa77dd80-32cf-11ea-8995-52324e7d3efe.png)

## Features
- `NEW` **REST API** for web-based validation via FastAPI
- `NEW` **JWT Token Generator** for easy API testing with Clerk authentication
- `NEW` **VAT Number (Partita IVA)** validation and encoding
- `NEW` **Auto-updated** data (once a week) directly from **ANPR** data-source.
- `NEW` **Command Line Interface** available.
- **Transliteration** for name/surname
- **Multiple** birthdate formats (date/string) *(you can see all the supported string formats [here](https://github.com/fabiocaccamo/python-codicefiscale/blob/main/tests/test_codicefiscale.py#L81-L140))*
- **Automatic** birthplace city/foreign-country code detection from name
- **Omocodia** support

## Installation

### Basic Installation
```bash
pip install python-codicefiscale
```

### With FastAPI Support (for REST API)
```bash
pip install 'python-codicefiscale[api]'
```

## 🚀 Quick Start for New Users

### Development Setup (API Testing)
```bash
# 1. Clone and install
git clone https://github.com/fabiocaccamo/python-codicefiscale.git
cd python-codicefiscale
pip install uv && uv sync

# 2. Setup JWT token generation for API testing
cd frontend && npm install && npm run setup

# 3. Start API server and test
cd .. && uv run python -m codice_fiscale.__main_api__ &
cd frontend && npm run test-api
```

The setup script will guide you through:
- ✅ Configuring Clerk authentication (or disabling it for simple testing)
- ✅ Generating JWT tokens for API access
- ✅ Testing all API endpoints

## Usage

### Python

#### Import
```python
from codice_fiscale import codice_fiscale
```
#### Encode
```python
codice_fiscale.encode(
    lastname="Caccamo",
    firstname="Fabio",
    gender="M",
    birthdate="03/04/1985",
    birthplace="Torino",
)

# "CCCFBA85D03L219P"
```
#### Decode
```python
codice_fiscale.decode("CCCFBA85D03L219P")

# {
#     "code": "CCCFBA85D03L219P",
#     "gender": "M",
#     "birthdate": datetime.datetime(1985, 4, 3, 0, 0),
#     "birthplace": {
#         "name": "TORINO"
#         "province": "TO",
#         "code": "L219",
#     },
#     "omocodes": [
#         "CCCFBA85D03L219P",
#         "CCCFBA85D03L21VE",
#         "CCCFBA85D03L2MVP",
#         "CCCFBA85D03LNMVE",
#         "CCCFBA85D0PLNMVA",
#         "CCCFBA85DLPLNMVL",
#         "CCCFBA8RDLPLNMVX",
#         "CCCFBAURDLPLNMVU",
#     ],
#     "raw": {
#         "code": "CCCFBA85D03L219P",
#         "lastname": "CCC",
#         "firstname": "FBA",
#         "birthdate": "85D03",
#         "birthdate_year": "85"
#         "birthdate_month": "D",
#         "birthdate_day": "03",
#         "birthplace": "L219",
#         "cin": "P",
#     },
# }
```

#### Check
```python
codice_fiscale.is_valid("CCCFBA85D03L219P")

# True
```
```python
codice_fiscale.is_omocode("CCCFBA85D03L219P")

# False
```

#### VAT Number (Partita IVA) Support
```python
from codice_fiscale.codice_fiscale import partitaiva

# Validate a VAT number
partitaiva.is_valid("01234567890")
# True

# Generate VAT number from base 10 digits
partitaiva.encode("0123456789")
# "01234567890"

# Decode VAT number
partitaiva.decode("01234567890")
# {
#     "code": "01234567890",
#     "valid": True,
#     "base_number": "0123456789",
#     "check_digit": "0",
#     "calculated_check_digit": "0",
# }
```

### REST API
Start the FastAPI validation server:
```bash
uv run python -m codice_fiscale.__main_api__
```

The API will be available at `http://localhost:8000` with automatic documentation at `http://localhost:8000/docs`.

#### Authentication
The API supports optional Clerk authentication. To enable authentication:

1. Set up a [Clerk](https://clerk.com) account and create an application
2. Set the environment variable:
   ```bash
   export CLERK_PUBLISHABLE_KEY="pk_test_..."
   ```
3. Include the Bearer token in API requests:
   ```bash
   curl -H "Authorization: Bearer <your-clerk-jwt-token>" ...
   ```

**Note**: If `CLERK_PUBLISHABLE_KEY` is not set, the API runs without authentication (public access).

#### API Endpoints

**Fiscal Code Validation:**
```bash
# Without authentication (if disabled)
curl -X POST "http://localhost:8000/fiscal-code/validate" \
     -H "Content-Type: application/json" \
     -d '{"code": "CCCFBA85D03L219P"}'

# With Clerk authentication (if enabled)
curl -X POST "http://localhost:8000/fiscal-code/validate" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <your-clerk-jwt-token>" \
     -d '{"code": "CCCFBA85D03L219P"}'
```

**VAT Number Validation:**
```bash
curl -X POST "http://localhost:8000/vat/validate" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <your-clerk-jwt-token>" \
     -d '{"partita_iva": "01234567890"}'
```

**Fiscal Code Generation:**
```bash
curl -X POST "http://localhost:8000/fiscal-code/encode" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <your-clerk-jwt-token>" \
     -d '{ 
       "lastname": "Caccamo",
       "firstname": "Fabio", 
       "gender": "M",
       "birthdate": "03/04/1985",
       "birthplace": "Torino"
     }'
```

### Command Line
This library can be used also as a CLI tool, for more info run:
```bash
uv run python -m codice_fiscale --help
```

#### Encode (CLI)
```bash
uv run python -m codice_fiscale encode --firstname Fabio --lastname Caccamo --gender M --birthdate 03/04/1985 --birthplace Torino
```

#### Decode (CLI)
```bash
python -m codice_fiscale decode CCCFBA85D03L219P
```

## Testing
```bash
# clone repository
git clone https://github.com/fabiocaccamo/python-codicefiscale.git && cd python-codicefiscale

# create virtualenv and activate it
python -m venv venv && . venv/bin/activate

# upgrade pip
python -m pip install --upgrade pip

# install requirements
pip install -r requirements.txt -r requirements-test.txt

# install pre-commit to run formatters and linters
pre-commit install --install-hooks

# run tests using tox
tox

# or run tests using pytest
pytest
```

## License
Released under [MIT License](LICENSE.txt).

---

## Supporting

- :star: Star this project on [GitHub](https://github.com/fabiocaccamo/python-codicefiscale)
- :octocat: Follow me on [GitHub](https://github.com/fabiocaccamo)
- :blue_heart: Follow me on [Bluesky](https://bsky.app/profile/fabiocaccamo.bsky.social)
- :moneybag: Sponsor me on [Github](https://github.com/sponsors/fabiocaccamo)

## See also

- [`python-benedict`](https://github.com/fabiocaccamo/python-benedict) - dict subclass with keylist/keypath support, I/O shortcuts (base64, csv, json, pickle, plist, query-string, toml, xml, yaml) and many utilities. 📘

- [`python-fontbro`](https://github.com/fabiocaccamo/python-fontbro) - friendly font operations. 🧢

- [`python-fsutil`](https://github.com/fabiocaccamo/python-fsutil) - file-system utilities for lazy devs. 🧟‍♂️
✅ Project cleaned up and all branches merged
