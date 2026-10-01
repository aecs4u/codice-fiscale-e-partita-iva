# Project Overview

`python-codice_fiscale` is a comprehensive Python library designed for the encoding, decoding, and validation of Italian fiscal codes (Codice Fiscale) and VAT numbers (Partita IVA). It offers a versatile set of interfaces, including a direct Python API, a command-line interface (CLI), and a robust FastAPI-based REST API.

The REST API is built for scalability and features optional Clerk authentication, making it suitable for secure deployments, particularly on Google Cloud Run. A notable feature of this project is its ability to auto-update geographical data (municipalities and countries), ensuring accuracy and relevance.

## Main Technologies

*   **Backend:** Python, FastAPI, Uvicorn
*   **Authentication:** Clerk (for REST API)
*   **Dependency Management:** `uv`, `pip`
*   **Testing:** `pytest`, `tox`
*   **Code Quality:** `black` (formatter), `ruff` (linter), `mypy` (type checker)
*   **Deployment:** Google Cloud Run, Docker

# Building and Running

## Installation

*   **Basic Library Installation:**
    ```bash
    pip install python-codice_fiscale
    ```
*   **With FastAPI Support (for REST API):**
    ```bash
    pip install 'python-codice_fiscale[api]'
    ```

## Development Setup (API Testing)

To set up the project for development and test the API with JWT token generation:

```bash
git clone https://github.com/fabiocaccamo/python-codice_fiscale.git
cd python-codice_fiscale
pip install uv && uv sync
cd frontend && npm install && npm run setup
cd .. && uv run python -m codice_fiscale.__main_api__ &
cd frontend && npm run test-api
```

## Running the REST API

To start the FastAPI server locally:

```bash
python -m codice_fiscale.__main_api__
```

The API will be available at `http://localhost:8000`, with interactive documentation at `http://localhost:8000/docs`.

## Running the Command-Line Interface (CLI)

The library can also be used as a CLI tool. For general help:

```bash
python -m codice_fiscale --help
```

**Examples:**

*   **Encode Fiscal Code:**
    ```bash
    python -m codice_fiscale encode --firstname Fabio --lastname Caccamo --gender M --birthdate 03/04/1985 --birthplace Torino
    ```
*   **Decode Fiscal Code:**
    ```bash
    python -m codice_fiscale decode CCCFBA85D03L219P
    ```

## Testing

The project uses `pytest` for unit testing and `tox` for running tests across multiple Python environments.

*   **Run tests with Tox (recommended for comprehensive testing):**
    ```bash
    tox
    ```
*   **Run tests with Pytest:**
    ```bash
    pytest
    ```

## Deployment to Google Cloud Run

The project includes a shell script for deploying the FastAPI application to Google Cloud Run.

**Prerequisites:**
*   Google Cloud SDK (`gcloud`) installed and authenticated.
*   Docker installed.

**Usage:**

```bash
./deploy-cloudrun.sh -p <your-project-id> [OPTIONS]
```

**Example:**

```bash
./deploy-cloudrun.sh -p my-gcp-project-id -r europe-west1 --auth
```

The script will:
1.  Set your Google Cloud project.
2.  Generate `requirements.txt` if not present.
3.  Enable necessary Google Cloud APIs.
4.  Dynamically create a `Dockerfile`.
5.  Deploy the service to Cloud Run, configuring memory, CPU, instances, and authentication based on provided options.

# Development Conventions

*   **Code Formatting:** The project adheres to `black` formatting standards, configured in `pyproject.toml`.
*   **Linting:** `ruff` is used for linting, with rules defined in `pyproject.toml` to maintain code quality and consistency.
*   **Type Checking:** `mypy` is configured for static type checking, ensuring type correctness throughout the codebase.
*   **Testing Practices:** Comprehensive unit tests are implemented using `pytest`. `tox` is used to ensure compatibility across various Python versions and to automate code quality checks.
*   **Pre-commit Hooks:** The `tox` configuration includes `pre-commit run -a`, indicating that pre-commit hooks are utilized to enforce code quality standards before commits are made.
