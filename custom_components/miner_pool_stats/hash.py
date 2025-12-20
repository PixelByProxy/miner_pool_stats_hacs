"""Hash rate calculations for the Miner Pool Stats integration."""

from enum import IntEnum


class HashRateUnit(IntEnum):
    """Enumeration of hash rate units."""

    H = 1
    KH = int(H) * 1000
    MH = int(KH) * 1000
    GH = int(MH) * 1000
    TH = int(GH) * 1000
    PH = int(TH) * 1000
    EH = int(PH) * 1000
    ZH = int(EH) * 1000

    def __str__(self):
        """Return the string representation of the hash rate unit."""

        if self.value == self.KH:
            return "KH/s"
        if self.value == self.MH:
            return "MH/s"
        if self.value == self.GH:
            return "GH/s"
        if self.value == self.TH:
            return "TH/s"
        if self.value == self.PH:
            return "PH/s"
        if self.value == self.EH:
            return "EH/s"
        if self.value == self.ZH:
            return "ZH/s"
        return "H/s"

    @classmethod
    def from_str(cls, value: str):
        """Create a HashRateUnit from a string representation."""

        if value in {"KH", "K"}:
            return cls.KH
        if value in {"MH", "M"}:
            return cls.MH
        if value in {"GH", "G"}:
            return cls.GH
        if value in {"TH", "T"}:
            return cls.TH
        if value in {"PH", "P"}:
            return cls.PH
        if value in {"EH", "E"}:
            return cls.EH
        if value in {"ZH", "Z"}:
            return cls.ZH
        return cls.H

    def __repr__(self):
        """Return a string representation of the hash rate unit."""

        return str(self)

    def model_dump(self):
        """Return a dictionary representation of the hash rate unit."""

        return {"value": self.value, "suffix": str(self)}


class HashRate:
    """Class to represent a hash rate value with a unit."""

    def __init__(self, value: float, unit: HashRateUnit) -> None:
        """Initialize a HashRate instance with a value and unit."""
        self.value = self._format_value(value)
        self.unit = unit

    @classmethod
    def from_known_number(cls, value: float, unit: str):
        """Create a HashRate instance from a numeric value and unit string."""

        if unit in {"KH", "K"}:
            return cls(value, HashRateUnit.KH)
        if unit in {"MH", "M"}:
            return cls(value, HashRateUnit.MH)
        if unit in {"GH", "G"}:
            return cls(value, HashRateUnit.GH)
        if unit in {"TH", "T"}:
            return cls(value, HashRateUnit.TH)
        if unit in {"PH", "P"}:
            return cls(value, HashRateUnit.PH)
        if unit in {"EH", "E"}:
            return cls(value, HashRateUnit.EH)
        if unit in {"ZH", "Z"}:
            return cls(value, HashRateUnit.ZH)

        return cls(value, HashRateUnit.H)

    @classmethod
    def from_number(cls, value: float):
        """Create a HashRate instance from a numeric value."""

        unit = HashRateUnit.EH  # default to largest unit

        if value < HashRateUnit.KH.value:
            unit = HashRateUnit.H
        elif value < HashRateUnit.MH.value:
            unit = HashRateUnit.KH
        elif value < HashRateUnit.GH.value:
            unit = HashRateUnit.MH
        elif value < HashRateUnit.TH.value:
            unit = HashRateUnit.GH
        elif value < HashRateUnit.PH.value:
            unit = HashRateUnit.TH
        elif value < HashRateUnit.EH.value:
            unit = HashRateUnit.PH

        translated_value = value / unit.value

        return cls(translated_value, unit)

    @classmethod
    def from_string(cls, value: str):
        """Create a HashRate instance from a string (e.g., '1.2G' or '1.35T').

        Args:
            value: A string in the format 'floatValueUnit' (e.g., '1.2G', '1.35T')

        Returns:
            A HashRate instance representing the parsed value
        """
        if not value or value == "0":
            return cls(0, HashRateUnit.H)

        # Find the last digit in the string
        last_digit_index = -1
        for i, char in enumerate(value):
            if char.isdigit() or char == ".":
                last_digit_index = i

        # Split into value and unit parts
        value_part = value[: last_digit_index + 1]
        unit_part = value[last_digit_index + 1 :]

        try:
            float_value = float(value_part)
            return cls.from_known_number(float_value, unit_part)
        except (ValueError, TypeError):
            return cls(0, HashRateUnit.H)

    def to_unit(self, unit: HashRateUnit):
        """Convert the hash rate to a different unit."""

        if self.unit == unit:
            return self

        if self.unit < unit:
            # Convert to a larger unit
            conversion_factor = 1
            for hru in HashRateUnit:
                if hru.value <= self.unit.value:
                    continue
                if hru.value > unit.value:
                    break
                conversion_factor *= 1000

            converted_value = self.value / conversion_factor
        else:
            # Convert to a smaller unit
            conversion_factor = 1
            for hru in reversed(HashRateUnit):
                if hru.value >= self.unit.value:
                    continue
                if hru.value < unit.value:
                    break
                conversion_factor *= 1000

            converted_value = self.value * conversion_factor

        return HashRate(converted_value, unit)

    def _format_value(self, value: float) -> float:
        """Format to the smallest readable number."""
        # For values less than 1, count leading zeros after decimal
        if value < 1:
            leading_zeros = self._count_digits_until_non_zero(value)
            if leading_zeros > 2:
                return value

        return round(value, 2)

    def _count_digits_until_non_zero(self, num: float) -> int:
        """Count the number of digits after the decimal point until the first non-zero digit."""
        # Convert the number to a string
        num_str = f"{num:.16f}".rstrip("0")  # Format to avoid floating-point issues
        if "." not in num_str:
            return 0  # No decimal point means no digits after it

        decimal_part = num_str.split(".")[1]  # Get the part after the decimal
        count = 0

        for digit in decimal_part:
            if digit == "0":
                count += 1
            else:
                break

        return count

    def __str__(self):
        """Return the string representation of the hash rate."""

        return f"{self.value} {self.unit}"

    def __repr__(self):
        """Return a string representation of the HashRate instance."""

        return f"HashRate(value={self.value}, unit={self.unit})"

    def model_dump(self):
        """Return a dictionary representation of the HashRate instance."""

        return {"value": self.value, "unit": str(self.unit)}
