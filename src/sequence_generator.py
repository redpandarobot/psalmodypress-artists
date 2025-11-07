"""
Base-36 Sequence Generator for Psalmody Press Artists

Generates unique 5-character alphanumeric IDs (A-Z, 0-9) for tracking prompts.
Base-36 gives us 36^5 = 60,466,176 possible unique IDs.

Example IDs: A0000, EO8HB, ZZ9ZZ, etc.
"""

import string

class SequenceGenerator:
    """Generates base-36 alphanumeric sequences."""

    # Base-36 character set: 0-9, A-Z
    CHARSET = string.digits + string.ascii_uppercase  # '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    BASE = 36
    SEQUENCE_LENGTH = 5
    MAX_VALUE = BASE ** SEQUENCE_LENGTH - 1  # 60,466,175

    @classmethod
    def number_to_sequence(cls, num: int) -> str:
        """
        Convert a number (0 to 60,466,175) to a 5-character base-36 string.

        Args:
            num: Integer to convert (0 to MAX_VALUE)

        Returns:
            5-character base-36 string (e.g., 'A0000', 'EO8HB')

        Raises:
            ValueError: If num is out of range
        """
        if not 0 <= num <= cls.MAX_VALUE:
            raise ValueError(f"Number {num} out of range (0 to {cls.MAX_VALUE})")

        if num == 0:
            return '0' * cls.SEQUENCE_LENGTH

        result = []
        while num > 0:
            result.append(cls.CHARSET[num % cls.BASE])
            num //= cls.BASE

        # Pad with zeros to ensure 5 characters and reverse
        sequence = ''.join(reversed(result))
        return sequence.zfill(cls.SEQUENCE_LENGTH)

    @classmethod
    def sequence_to_number(cls, sequence: str) -> int:
        """
        Convert a base-36 sequence back to a number.

        Args:
            sequence: 5-character base-36 string

        Returns:
            Integer value (0 to MAX_VALUE)

        Raises:
            ValueError: If sequence is invalid
        """
        sequence = sequence.upper()

        if len(sequence) != cls.SEQUENCE_LENGTH:
            raise ValueError(f"Sequence must be {cls.SEQUENCE_LENGTH} characters")

        num = 0
        for char in sequence:
            if char not in cls.CHARSET:
                raise ValueError(f"Invalid character '{char}' in sequence")
            num = num * cls.BASE + cls.CHARSET.index(char)

        return num

    @classmethod
    def is_valid_sequence(cls, sequence: str) -> bool:
        """
        Check if a string is a valid sequence ID.

        Args:
            sequence: String to validate

        Returns:
            True if valid, False otherwise
        """
        if len(sequence) != cls.SEQUENCE_LENGTH:
            return False

        return all(c in cls.CHARSET for c in sequence.upper())

    @classmethod
    def get_next_sequence(cls, current_num: int) -> tuple[int, str]:
        """
        Get the next sequence number and ID.

        Args:
            current_num: Current sequence number

        Returns:
            Tuple of (next_number, next_sequence_id)

        Raises:
            ValueError: If we've exhausted all possible sequences
        """
        next_num = current_num + 1

        if next_num > cls.MAX_VALUE:
            raise ValueError(f"Sequence exhausted! Max value {cls.MAX_VALUE} reached.")

        next_seq = cls.number_to_sequence(next_num)
        return next_num, next_seq


# Convenience functions for direct use
def generate_sequence_id(number: int) -> str:
    """Generate a sequence ID from a number."""
    return SequenceGenerator.number_to_sequence(number)


def parse_sequence_id(sequence_id: str) -> int:
    """Parse a sequence ID back to its number."""
    return SequenceGenerator.sequence_to_number(sequence_id)


def validate_sequence_id(sequence_id: str) -> bool:
    """Validate a sequence ID."""
    return SequenceGenerator.is_valid_sequence(sequence_id)


if __name__ == "__main__":
    # Test the sequence generator
    print("Base-36 Sequence Generator Test\n")
    print(f"Character set: {SequenceGenerator.CHARSET}")
    print(f"Base: {SequenceGenerator.BASE}")
    print(f"Sequence length: {SequenceGenerator.SEQUENCE_LENGTH}")
    print(f"Max sequences: {SequenceGenerator.MAX_VALUE + 1:,}\n")

    # Test some conversions
    test_numbers = [0, 1, 100, 1000, 10000, 100000, 1000000, 60466175]

    print("Number to Sequence conversions:")
    for num in test_numbers:
        seq = generate_sequence_id(num)
        back = parse_sequence_id(seq)
        print(f"  {num:>10,} -> '{seq}' -> {back:>10,} ✓" if num == back else f"  ERROR")

    print("\nSample sequences:")
    samples = [0, 36, 1296, 46656, 1679616, 60466175]
    for num in samples:
        print(f"  {num:>10,}: {generate_sequence_id(num)}")

    print("\nValidation tests:")
    valid_ids = ["00000", "A0000", "EO8HB", "ZZZZZ"]
    invalid_ids = ["123", "ABCDEF", "AB@CD", "abc12"]

    for seq in valid_ids:
        print(f"  '{seq}': {validate_sequence_id(seq)} (should be True)")

    for seq in invalid_ids:
        print(f"  '{seq}': {validate_sequence_id(seq)} (should be False)")
