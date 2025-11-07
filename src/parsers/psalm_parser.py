"""
Psalm Text Parser

Reads and parses psalm text files from the input directory.
Extracts psalm content and basic metadata.
"""

from pathlib import Path
from typing import Optional, Dict, Any
import re


class PsalmParser:
    """Parser for psalm text files."""

    def __init__(self, psalms_directory: str = "data/input/psalms"):
        """
        Initialize the psalm parser.

        Args:
            psalms_directory: Path to directory containing psalm text files
        """
        self.psalms_dir = Path(psalms_directory)

    def get_psalm_path(self, psalm_number: int) -> Path:
        """
        Get the file path for a specific psalm.

        Args:
            psalm_number: Psalm number (1-150)

        Returns:
            Path to the psalm file

        Raises:
            ValueError: If psalm number is out of range
        """
        if not 1 <= psalm_number <= 150:
            raise ValueError(f"Psalm number must be between 1 and 150, got {psalm_number}")

        filename = f"psalm_{psalm_number:03d}.txt"
        return self.psalms_dir / filename

    def parse_psalm(self, psalm_number: int) -> Dict[str, Any]:
        """
        Parse a psalm file and extract content.

        Args:
            psalm_number: Psalm number (1-150)

        Returns:
            Dictionary containing:
                - number: Psalm number
                - text: Full psalm text
                - lines: List of individual lines
                - word_count: Number of words
                - verse_count: Estimated number of verses/stanzas
                - first_line: First line of the psalm
                - themes: Extracted themes (basic keyword analysis)

        Raises:
            FileNotFoundError: If psalm file doesn't exist
        """
        psalm_path = self.get_psalm_path(psalm_number)

        if not psalm_path.exists():
            raise FileNotFoundError(f"Psalm file not found: {psalm_path}")

        # Read the file
        with open(psalm_path, 'r', encoding='utf-8') as f:
            text = f.read().strip()

        if not text:
            raise ValueError(f"Psalm {psalm_number} file is empty")

        # Strip metadata headers (lines starting with #)
        text = self._strip_metadata(text)

        # Split into lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # Basic analysis
        word_count = len(text.split())
        verse_count = self._estimate_verse_count(lines)
        first_line = lines[0] if lines else ""
        themes = self._extract_themes(text)

        return {
            'number': psalm_number,
            'text': text,
            'lines': lines,
            'word_count': word_count,
            'verse_count': verse_count,
            'first_line': first_line,
            'themes': themes,
            'file_path': str(psalm_path)
        }

    def _strip_metadata(self, text: str) -> str:
        """
        Strip metadata headers from psalm text.

        Removes lines starting with # and === markers.

        Args:
            text: Raw psalm text

        Returns:
            Cleaned psalm text
        """
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()
            # Skip comment lines and separator lines
            if stripped.startswith('#') or stripped.startswith('==='):
                continue
            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines).strip()

    def _estimate_verse_count(self, lines: list) -> int:
        """
        Estimate the number of verses/stanzas in a psalm.

        Uses blank lines as verse separators. If no blank lines,
        estimates based on line count.

        Args:
            lines: List of text lines

        Returns:
            Estimated verse count
        """
        # For now, estimate based on line count
        # Typical verse is 2-4 lines
        if len(lines) <= 4:
            return 1
        elif len(lines) <= 8:
            return 2
        elif len(lines) <= 12:
            return 3
        else:
            return max(3, len(lines) // 4)

    def _extract_themes(self, text: str) -> list:
        """
        Extract basic themes from psalm text using keyword matching.

        Args:
            text: Psalm text

        Returns:
            List of identified themes
        """
        text_lower = text.lower()
        themes = []

        # Theme keywords
        theme_keywords = {
            'praise': ['praise', 'glory', 'exalt', 'worship', 'celebrate'],
            'trust': ['trust', 'refuge', 'shelter', 'safety', 'protection'],
            'deliverance': ['deliver', 'save', 'rescue', 'salvation', 'redeem'],
            'thanksgiving': ['thank', 'grateful', 'gratitude'],
            'lament': ['cry', 'weep', 'sorrow', 'trouble', 'distress', 'afflict'],
            'justice': ['justice', 'righteous', 'judgment', 'right'],
            'creation': ['heaven', 'earth', 'creation', 'mountains', 'sea', 'stars'],
            'mercy': ['mercy', 'compassion', 'lovingkindness', 'steadfast love'],
            'guidance': ['guide', 'teach', 'instruct', 'path', 'way', 'law'],
            'hope': ['hope', 'wait', 'endure']
        }

        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)

        return themes if themes else ['general']

    def get_psalm_title_suggestion(self, psalm_data: Dict[str, Any]) -> str:
        """
        Suggest a title for a psalm based on its content.

        Args:
            psalm_data: Parsed psalm data

        Returns:
            Suggested title string
        """
        first_line = psalm_data['first_line']
        themes = psalm_data['themes']

        # Extract first few meaningful words
        words = first_line.split()[:6]
        short_title = ' '.join(words)

        # Add ellipsis if truncated
        if len(first_line.split()) > 6:
            short_title += '...'

        return short_title

    def list_available_psalms(self) -> list:
        """
        List all available psalm files in the directory.

        Returns:
            List of psalm numbers that have files
        """
        if not self.psalms_dir.exists():
            return []

        available = []
        for i in range(1, 151):
            if self.get_psalm_path(i).exists():
                available.append(i)

        return available


if __name__ == "__main__":
    # Test the parser
    print("Psalm Parser Test\n")

    parser = PsalmParser()

    # Check for available psalms
    available = parser.list_available_psalms()
    print(f"Available psalms: {len(available)}")

    if available:
        # Parse the first available psalm
        psalm_num = available[0]
        print(f"\nParsing Psalm {psalm_num}...")

        psalm_data = parser.parse_psalm(psalm_num)

        print(f"  Number: {psalm_data['number']}")
        print(f"  Word count: {psalm_data['word_count']}")
        print(f"  Verse count (estimated): {psalm_data['verse_count']}")
        print(f"  First line: {psalm_data['first_line']}")
        print(f"  Themes: {', '.join(psalm_data['themes'])}")
        print(f"  Suggested title: {parser.get_psalm_title_suggestion(psalm_data)}")
        print(f"\n  First 200 characters:")
        print(f"  {psalm_data['text'][:200]}...")
    else:
        print("No psalm files found in data/input/psalms/")
        print("Add psalm text files named: psalm_001.txt, psalm_002.txt, etc.")
