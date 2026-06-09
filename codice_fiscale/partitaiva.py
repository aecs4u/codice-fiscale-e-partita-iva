from __future__ import annotations

import re


def _calculate_check_digit(vat_number: str) -> str:
    """Calculate the check digit for an Italian VAT number."""
    if len(vat_number) != 10:
        raise ValueError("VAT number must be 10 digits long (excluding check digit)")

    odd_sum = 0
    even_sum = 0

    for i, digit in enumerate(vat_number):
        if not digit.isdigit():
            raise ValueError("VAT number must contain only digits")

        digit_val = int(digit)

        if i % 2 == 0:  # odd position (1-based indexing)
            odd_sum += digit_val
        else:  # even position
            doubled = digit_val * 2
            even_sum += doubled if doubled < 10 else doubled - 9

    total = odd_sum + even_sum
    check_digit = (10 - (total % 10)) % 10
    return str(check_digit)


def is_valid(partita_iva: str) -> bool:
    """
    Check if the given string is a valid Italian VAT number (Partita IVA).

    Args:
        partita_iva: The VAT number to validate

    Returns:
        True if valid, False otherwise
    """
    if not partita_iva:
        return False

    # Remove spaces and convert to uppercase
    partita_iva = re.sub(r"\s+", "", partita_iva.upper())

    # Check if it's exactly 11 digits
    if not re.match(r"^\d{11}$", partita_iva):
        return False

    # Extract first 10 digits and check digit
    base_number = partita_iva[:10]
    provided_check_digit = partita_iva[10]

    # Calculate expected check digit
    try:
        expected_check_digit = _calculate_check_digit(base_number)
        return provided_check_digit == expected_check_digit
    except ValueError:
        return False


def encode(
    base_number: str,
) -> str:
    """
    Generate a complete Italian VAT number by adding the check digit.

    Args:
        base_number: The first 10 digits of the VAT number

    Returns:
        The complete 11-digit VAT number

    Raises:
        ValueError: If base_number is not exactly 10 digits
    """
    if not re.match(r"^\d{10}$", base_number):
        raise ValueError("Base number must be exactly 10 digits")

    check_digit = _calculate_check_digit(base_number)
    return base_number + check_digit


def decode(partita_iva: str) -> dict[str, str | bool | None]:
    """
    Decode an Italian VAT number and return its components.

    Args:
        partita_iva: The VAT number to decode

    Returns:
        Dictionary with validation results and components
    """
    # Clean the input
    cleaned_piva = re.sub(r"\s+", "", partita_iva.upper()) if partita_iva else ""

    result = {
        "code": partita_iva,
        "valid": False,
        "base_number": None,
        "check_digit": None,
        "calculated_check_digit": None,
    }

    if not cleaned_piva or not re.match(r"^\d{11}$", cleaned_piva):
        return result

    base_number = cleaned_piva[:10]
    check_digit = cleaned_piva[10]

    result["base_number"] = base_number
    result["check_digit"] = check_digit

    try:
        calculated_check_digit = _calculate_check_digit(base_number)
        result["calculated_check_digit"] = calculated_check_digit
        result["valid"] = check_digit == calculated_check_digit
    except ValueError:
        pass

    return result
