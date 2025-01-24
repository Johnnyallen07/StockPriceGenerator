from fractions import Fraction


def parse_float(value_str):
    """
    Parses a parameter string that can be a float or a fraction (e.g., "1/365") and returns its float value.

    :param value_str: The string to parse.
    :return: The float representation of the input string.
    :raises ValueError: If the string cannot be parsed into a float or a valid fraction.
    """
    try:
        # Attempt to parse as a fraction first
        return float(Fraction(value_str))
    except (ValueError, ZeroDivisionError):
        try:
            # If fraction parsing fails, try converting directly to float
            return float(value_str)
        except ValueError:
            raise ValueError(f"Invalid parameter format: '{value_str}'. Expected a number or a fraction like '1/365'.")

