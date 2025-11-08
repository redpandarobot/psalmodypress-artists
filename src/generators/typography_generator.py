"""
Nano-Banana Typography Prompt Generator

Generates typography prompts for key verses from psalms with artistic text treatments.
"""

import sys
from pathlib import Path
import json
from typing import Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from parsers.psalm_parser import PsalmParser
from parsers.brand_vision_parser import BrandVisionParser
from utils.prompt_helpers import register_typography


class TypographyGenerator:
    """Generates typography prompts with AI assistance."""

    def __init__(self, config_path: str = "config/settings.json", use_ai: bool = True):
        """
        Initialize the typography generator.

        Args:
            config_path: Path to configuration file
            use_ai: Whether to use AI for generation
        """
        self.psalm_parser = PsalmParser()
        self.vision_parser = BrandVisionParser()
        self.use_ai = use_ai

        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        # Initialize AI client if needed
        if self.use_ai:
            self._init_ai_client()

    def _init_ai_client(self):
        """Initialize OpenAI client for AI-powered generation."""
        try:
            from openai import OpenAI
            import os

            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                print("Warning: OPENAI_API_KEY not found. Falling back to template-based generation.")
                self.use_ai = False
                self.client = None
            else:
                self.client = OpenAI(api_key=api_key)
        except ImportError:
            print("Warning: openai package not installed. Falling back to template-based generation.")
            self.use_ai = False
            self.client = None

    def generate_prompt(
        self,
        psalm_number: int,
        artist_name: str,
        custom_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate typography prompt for a key verse.

        Args:
            psalm_number: Psalm number (1-150)
            artist_name: Artist identifier
            custom_params: Optional custom parameters

        Returns:
            Dictionary containing:
                - prompt: Typography prompt
                - key_verse: Selected key verse
                - sequence_id: Unique tracking ID
                - metadata: Generation metadata
        """
        # Parse inputs
        psalm_data = self.psalm_parser.parse_psalm(psalm_number)
        vision_data = self.vision_parser.parse_brand_vision(artist_name)

        # Select key verse
        key_verse = self._select_key_verse(psalm_data, custom_params)

        # Generate typography prompt
        if self.use_ai and self.client:
            typo_prompt = self._generate_with_ai(key_verse, psalm_data, vision_data, custom_params)
        else:
            typo_prompt = self._generate_template(key_verse, vision_data, custom_params)

        # Build metadata
        metadata = self._build_metadata(vision_data, key_verse, custom_params)

        # Register with sequence tracking
        sequence_id = register_typography(
            psalm_number=psalm_number,
            artist_name=artist_name,
            typography_prompt=typo_prompt,
            metadata=metadata
        )

        return {
            'prompt': typo_prompt,
            'key_verse': key_verse,
            'sequence_id': sequence_id,
            'metadata': metadata,
            'psalm_number': psalm_number,
            'artist_name': artist_name
        }

    def _select_key_verse(
        self,
        psalm_data: Dict[str, Any],
        custom_params: Optional[Dict[str, Any]]
    ) -> str:
        """
        Select the key verse for typography.

        Args:
            psalm_data: Parsed psalm data
            custom_params: Optional custom params (can specify verse_index)

        Returns:
            Selected verse text
        """
        # Allow custom verse selection
        if custom_params and 'verse_index' in custom_params:
            idx = custom_params['verse_index']
            if 0 <= idx < len(psalm_data['lines']):
                return psalm_data['lines'][idx]

        # Default: use first line (often the most memorable)
        return psalm_data['first_line']

    def _generate_with_ai(
        self,
        key_verse: str,
        psalm_data: Dict[str, Any],
        vision_data: Dict[str, Any],
        custom_params: Optional[Dict[str, Any]]
    ) -> str:
        """Generate typography prompt using AI."""
        system_prompt = """You are an expert typography designer creating prompts for AI typography tools.
Create detailed descriptions of how text should be styled and presented artistically.

Guidelines:
- Specify font style, weight, and treatment
- Describe text layout and composition
- Include color, effects, and decorative elements
- Match the artist's visual aesthetic
- Keep prompt clear and actionable (100-150 words)"""

        user_prompt = f"""Create a typography design prompt for this verse from Psalm {psalm_data['number']}:

VERSE: "{key_verse}"

ARTIST VISUAL STYLE:
{vision_data.get('visual_aesthetic', {}).get('full_description', 'Minimalist, clean design')}

TYPOGRAPHY PREFERENCES: {vision_data.get('visual_aesthetic', {}).get('typography', 'Clean, modern serif fonts')}
COLOR PALETTE: {vision_data.get('visual_aesthetic', {}).get('color_palette', 'Deep blues, warm golds')}

Create a prompt describing how to present this verse beautifully with artistic typography."""

        response = self.client.chat.completions.create(
            model=self.config['generation']['ai_model'],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            max_tokens=300
        )

        return response.choices[0].message.content.strip()

    def _generate_template(
        self,
        key_verse: str,
        vision_data: Dict[str, Any],
        custom_params: Optional[Dict[str, Any]]
    ) -> str:
        """Generate typography prompt using template."""
        visual = vision_data.get('visual_aesthetic', {})

        # Get style preferences
        typography = visual.get('typography', 'Modern serif font, clean and elegant')
        colors = visual.get('color_palette', 'Deep blues, warm golds, earth tones')
        style = visual.get('style', 'Minimalist, ethereal')

        prompt = f"""Typography design for verse: "{key_verse}"

Font: {typography}
Colors: {colors}
Style: {style}
Layout: Centered, generous spacing
Effects: Subtle shadows, elegant serifs
Background: Minimal, complementary to text
Overall aesthetic: Beautiful, reverent, artistic"""

        return prompt

    def _build_metadata(
        self,
        vision_data: Dict[str, Any],
        key_verse: str,
        custom_params: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build metadata for sequence tracking."""
        metadata = {
            'key_verse': key_verse,
            'verse_length': len(key_verse)
        }

        # Extract from vision
        visual = vision_data.get('visual_aesthetic', {})

        if visual.get('typography'):
            metadata['typography_style'] = visual['typography']

        if visual.get('color_palette'):
            metadata['color_palette'] = visual['color_palette']

        # Add custom params
        if custom_params:
            metadata.update(custom_params)

        return metadata

    def save_output(
        self,
        prompt_data: Dict[str, Any],
        output_dir: Optional[str] = None
    ) -> str:
        """
        Save generated typography prompt to file.

        Args:
            prompt_data: Prompt generation result
            output_dir: Optional custom output directory

        Returns:
            Path to saved file
        """
        if output_dir is None:
            output_dir = Path(self.config['paths']['output_base']) / \
                        prompt_data['artist_name'] / \
                        f"psalm_{prompt_data['psalm_number']:03d}"
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        # Save prompt
        prompt_file = output_dir / self.config['output_files']['typography_prompt']
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(f"Sequence ID: {prompt_data['sequence_id']}\n")
            f.write(f"Psalm: {prompt_data['psalm_number']}\n")
            f.write(f"Artist: {prompt_data['artist_name']}\n")
            f.write(f"\n{'='*60}\n\n")
            f.write(f"KEY VERSE:\n\"{prompt_data['key_verse']}\"\n\n")
            f.write(f"TYPOGRAPHY PROMPT:\n{prompt_data['prompt']}\n\n")
            f.write(f"METADATA:\n{json.dumps(prompt_data['metadata'], indent=2)}\n")

        return str(prompt_file)


if __name__ == "__main__":
    print("Typography Generator Test\n")

    generator = TypographyGenerator(use_ai=False)
    print("Available artists:", generator.vision_parser.list_available_artists())
    print("Available psalms:", len(generator.psalm_parser.list_available_psalms()))
