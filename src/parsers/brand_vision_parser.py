"""
Artist Brand Vision Parser

Reads and parses artist brand vision markdown files.
Extracts artist identity, musical style, visual aesthetic, and other key attributes.
"""

from pathlib import Path
from typing import Optional, Dict, Any
import re


class BrandVisionParser:
    """Parser for artist brand vision markdown files."""

    def __init__(self, artists_directory: str = "data/input/artists"):
        """
        Initialize the brand vision parser.

        Args:
            artists_directory: Path to directory containing artist subdirectories
        """
        self.artists_dir = Path(artists_directory)

    def get_brand_vision_path(self, artist_name: str) -> Path:
        """
        Get the path to an artist's brand vision file.

        Args:
            artist_name: Artist identifier (directory name)

        Returns:
            Path to brand_vision.md file
        """
        return self.artists_dir / artist_name / "brand_vision.md"

    def parse_brand_vision(self, artist_name: str) -> Dict[str, Any]:
        """
        Parse an artist's brand vision file.

        Args:
            artist_name: Artist identifier

        Returns:
            Dictionary containing:
                - artist_name: Artist identifier
                - full_text: Complete brand vision text
                - sections: Dict of section name -> content
                - musical_style: Extracted musical style info
                - visual_aesthetic: Extracted visual info
                - themes: Key themes and messages
                - target_audience: Audience description
                - summary: Brief summary

        Raises:
            FileNotFoundError: If brand vision file doesn't exist
        """
        vision_path = self.get_brand_vision_path(artist_name)

        if not vision_path.exists():
            raise FileNotFoundError(f"Brand vision file not found: {vision_path}")

        # Read the file
        with open(vision_path, 'r', encoding='utf-8') as f:
            text = f.read().strip()

        if not text:
            raise ValueError(f"Brand vision file for {artist_name} is empty")

        # Parse sections
        sections = self._parse_sections(text)

        # Extract specific attributes
        musical_style = self._extract_musical_style(sections)
        visual_aesthetic = self._extract_visual_aesthetic(sections)
        themes = self._extract_themes(sections)
        target_audience = self._extract_target_audience(sections)
        artist_identity = self._extract_artist_identity(sections)

        return {
            'artist_name': artist_name,
            'full_text': text,
            'sections': sections,
            'artist_identity': artist_identity,
            'musical_style': musical_style,
            'visual_aesthetic': visual_aesthetic,
            'themes': themes,
            'target_audience': target_audience,
            'summary': self._create_summary(sections),
            'file_path': str(vision_path)
        }

    def _parse_sections(self, text: str) -> Dict[str, str]:
        """
        Parse markdown sections from the brand vision.

        Args:
            text: Full brand vision text

        Returns:
            Dictionary of section headers -> content
        """
        sections = {}

        # Split by markdown headers (## or ###)
        lines = text.split('\n')
        current_section = None
        current_content = []

        for line in lines:
            # Check for header
            header_match = re.match(r'^#{1,3}\s+(.+)$', line)

            if header_match:
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()

                # Start new section
                current_section = header_match.group(1).strip()
                current_content = []
            else:
                # Add to current section
                if current_section:
                    current_content.append(line)

        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

    def _extract_musical_style(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """Extract musical style information."""
        musical_info = {}

        # Look for musical style section
        style_keys = ['Musical Style & Genre', 'Musical Style', 'Genre', 'Music Style']
        for key in style_keys:
            if key in sections:
                content = sections[key]
                musical_info['full_description'] = content

                # Extract specific attributes
                musical_info['genres'] = self._extract_list_items(content, ['Primary', 'Secondary', 'Genre'])
                musical_info['influences'] = self._extract_value(content, 'Influences')
                musical_info['instrumentation'] = self._extract_value(content, 'Instrumentation')
                musical_info['tempo'] = self._extract_value(content, 'Tempo')
                musical_info['vocal_style'] = self._extract_value(content, 'Vocal')

                break

        return musical_info

    def _extract_visual_aesthetic(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """Extract visual aesthetic information."""
        visual_info = {}

        visual_keys = ['Visual Aesthetic', 'Visual Style', 'Aesthetic']
        for key in visual_keys:
            if key in sections:
                content = sections[key]
                visual_info['full_description'] = content

                # Extract specific attributes
                visual_info['color_palette'] = self._extract_value(content, 'Color')
                visual_info['style'] = self._extract_value(content, 'Style')
                visual_info['imagery'] = self._extract_value(content, 'Imagery')
                visual_info['typography'] = self._extract_value(content, 'Typography')

                break

        return visual_info

    def _extract_themes(self, sections: Dict[str, str]) -> list:
        """Extract themes and messages."""
        themes = []

        theme_keys = ['Themes & Messages', 'Themes', 'Messages', 'Key Themes']
        for key in theme_keys:
            if key in sections:
                content = sections[key]
                # Extract bullet points or lines
                lines = [line.strip('- ').strip() for line in content.split('\n') if line.strip()]
                themes.extend([line for line in lines if line and len(line) > 5])
                break

        return themes

    def _extract_target_audience(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """Extract target audience information."""
        audience_info = {}

        audience_keys = ['Target Audience', 'Audience']
        for key in audience_keys:
            if key in sections:
                content = sections[key]
                audience_info['full_description'] = content
                audience_info['age'] = self._extract_value(content, 'Age')
                audience_info['interests'] = self._extract_value(content, 'Interests')
                audience_info['setting'] = self._extract_value(content, 'Setting')
                break

        return audience_info

    def _extract_artist_identity(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """Extract artist identity information."""
        identity = {}

        identity_keys = ['Artist Name & Identity', 'Artist Identity', 'Identity']
        for key in identity_keys:
            if key in sections:
                content = sections[key]
                identity['full_description'] = content
                identity['name'] = self._extract_value(content, 'Name')
                identity['tagline'] = self._extract_value(content, 'Tagline')
                break

        return identity

    def _extract_value(self, text: str, keyword: str) -> Optional[str]:
        """
        Extract a value following a keyword.

        Args:
            text: Text to search
            keyword: Keyword to find

        Returns:
            Extracted value or None
        """
        # Look for patterns like "Keyword: value" or "**Keyword**: value"
        patterns = [
            rf'\*\*{keyword}[^:]*\*\*:\s*(.+?)(?:\n|$)',
            rf'{keyword}[^:]*:\s*(.+?)(?:\n|$)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_list_items(self, text: str, keywords: list) -> list:
        """Extract list items after keywords."""
        items = []

        for keyword in keywords:
            value = self._extract_value(text, keyword)
            if value:
                items.append(value)

        return items

    def _create_summary(self, sections: Dict[str, str]) -> str:
        """
        Create a brief summary of the brand vision.

        Args:
            sections: Parsed sections

        Returns:
            Summary string
        """
        # Try to find vision/mission section
        vision_keys = ['Artistic Vision & Mission', 'Vision', 'Mission']
        for key in vision_keys:
            if key in sections:
                content = sections[key]
                # Take first sentence or first 150 characters
                sentences = content.split('.')
                if sentences:
                    return sentences[0].strip() + '.'

        # Fallback: return first section content
        if sections:
            first_content = list(sections.values())[0]
            return first_content[:150] + '...' if len(first_content) > 150 else first_content

        return "No summary available"

    def list_available_artists(self) -> list:
        """
        List all artists with brand vision files.

        Returns:
            List of artist names
        """
        if not self.artists_dir.exists():
            return []

        artists = []
        for item in self.artists_dir.iterdir():
            if item.is_dir():
                vision_file = item / "brand_vision.md"
                if vision_file.exists():
                    artists.append(item.name)

        return sorted(artists)


if __name__ == "__main__":
    # Test the parser
    print("Brand Vision Parser Test\n")

    parser = BrandVisionParser()

    # Check for available artists
    artists = parser.list_available_artists()
    print(f"Available artists: {len(artists)}")

    if artists:
        # Parse the first available artist
        artist_name = artists[0]
        print(f"\nParsing brand vision for: {artist_name}")

        vision = parser.parse_brand_vision(artist_name)

        print(f"  Artist name: {vision['artist_name']}")
        print(f"  Sections found: {', '.join(vision['sections'].keys())}")
        print(f"  Summary: {vision['summary']}")

        if vision['musical_style']:
            print(f"  Musical genres: {vision['musical_style'].get('genres', [])}")

        if vision['themes']:
            print(f"  Themes: {', '.join(vision['themes'][:3])}")

    else:
        print("No artist brand vision files found in data/input/artists/")
        print("Create artist directories with brand_vision.md files")
