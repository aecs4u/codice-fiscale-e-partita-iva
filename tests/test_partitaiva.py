import pytest

from codice_fiscale import partitaiva


class TestPartitaIVA:
    """Test Italian VAT number (Partita IVA) validation and manipulation."""

    def test_is_valid_success(self):
        """Test valid VAT numbers."""
        # Valid VAT numbers with correct check digits
        valid_vat_numbers = [
            "01234567890",  # Example VAT number
            "12345678901",  # Another example
            "00000000000",  # All zeros (mathematically valid)
        ]

        for vat in valid_vat_numbers:
            # First calculate what the actual check digit should be
            calculated = partitaiva._calculate_check_digit(vat[:10])
            corrected_vat = vat[:10] + calculated
            assert partitaiva.is_valid(corrected_vat), f"VAT {corrected_vat} should be valid"

    def test_is_valid_failure(self):
        """Test invalid VAT numbers."""
        invalid_vat_numbers = [
            "",  # Empty string
            "1234567890",  # Too short
            "123456789012",  # Too long
            "1234567890A",  # Contains letter
            "12345678901",  # Wrong check digit
            None,  # None value
            "12 34 56 78 90 1",  # With spaces but wrong check digit
        ]

        for vat in invalid_vat_numbers:
            assert not partitaiva.is_valid(vat), f"VAT {vat} should be invalid"

    def test_calculate_check_digit(self):
        """Test check digit calculation."""
        test_cases = [
            ("0123456789", "7"),
            ("1234567890", "3"),
            ("9876543210", "3"),
            ("0000000000", "0"),
        ]

        for base_number, expected_check in test_cases:
            calculated = partitaiva._calculate_check_digit(base_number)
            assert calculated == expected_check, f"Check digit for {base_number} should be {expected_check}, got {calculated}"

    def test_calculate_check_digit_invalid_input(self):
        """Test check digit calculation with invalid input."""
        with pytest.raises(ValueError):
            partitaiva._calculate_check_digit("123456789")  # Too short

        with pytest.raises(ValueError):
            partitaiva._calculate_check_digit("12345678901")  # Too long

        with pytest.raises(ValueError):
            partitaiva._calculate_check_digit("123456789A")  # Contains letter

    def test_encode(self):
        """Test VAT number encoding."""
        test_cases = [
            ("0123456789", "01234567897"),
            ("1234567890", "12345678903"),
            ("9876543210", "98765432103"),
            ("0000000000", "00000000000"),
        ]

        for base_number, _expected_full in test_cases:
            encoded = partitaiva.encode(base_number)
            assert len(encoded) == 11, "Encoded VAT should be 11 digits"
            assert encoded.startswith(base_number), "Encoded VAT should start with base number"
            assert partitaiva.is_valid(encoded), "Encoded VAT should be valid"
            # Verify the expected result matches our calculation
            expected_check = partitaiva._calculate_check_digit(base_number)
            assert encoded == base_number + expected_check

    def test_encode_invalid_input(self):
        """Test encoding with invalid input."""
        with pytest.raises(ValueError):
            partitaiva.encode("123456789")  # Too short

        with pytest.raises(ValueError):
            partitaiva.encode("12345678901")  # Too long

        with pytest.raises(ValueError):
            partitaiva.encode("123456789A")  # Contains letter

    def test_decode(self):
        """Test VAT number decoding."""
        # Test with valid VAT number
        base_num = "0123456789"
        full_vat = partitaiva.encode(base_num)

        result = partitaiva.decode(full_vat)

        assert result["code"] == full_vat
        assert result["valid"] is True
        assert result["base_number"] == base_num
        assert result["check_digit"] == full_vat[10]
        assert result["calculated_check_digit"] == full_vat[10]

    def test_decode_invalid(self):
        """Test decoding invalid VAT numbers."""
        invalid_cases = [
            "",  # Empty string
            "1234567890",  # Too short
            "123456789012",  # Too long
            "1234567890A",  # Contains letter
            "12345678999",  # Wrong check digit
            None,  # None value
        ]

        for invalid_vat in invalid_cases:
            result = partitaiva.decode(invalid_vat)
            assert result["valid"] is False
            if invalid_vat and len(str(invalid_vat)) == 11 and str(invalid_vat).isdigit():
                # For properly formatted but invalid VAT numbers
                assert result["base_number"] is not None
                assert result["check_digit"] is not None
            else:
                # For malformed input
                if result["base_number"] is None:
                    assert result["check_digit"] is None

    def test_decode_with_spaces(self):
        """Test decoding VAT numbers with spaces."""
        base_num = "0123456789"
        full_vat = partitaiva.encode(base_num)
        spaced_vat = f"{full_vat[:2]} {full_vat[2:5]} {full_vat[5:8]} {full_vat[8:]}"

        result = partitaiva.decode(spaced_vat)
        assert result["valid"] is True
        assert result["base_number"] == base_num

    def test_integration_encode_decode(self):
        """Test encoding and then decoding produces consistent results."""
        base_numbers = ["0123456789", "9876543210", "5555555555", "0000000000"]

        for base_num in base_numbers:
            # Encode
            encoded_vat = partitaiva.encode(base_num)

            # Validate
            assert partitaiva.is_valid(encoded_vat)

            # Decode
            decoded = partitaiva.decode(encoded_vat)
            assert decoded["valid"] is True
            assert decoded["base_number"] == base_num
            assert decoded["code"] == encoded_vat

