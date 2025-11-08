"""
Midjourney Album Cover Art Prompt Generator

Generates Midjourney image prompts for album cover art based on psalm themes
and artist brand vision.
"""

import sys
from pathlib import Path
import json
from typing import Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from parsers.psalm_parser import PsalmParser
from parsers.brand_vision_parser import BrandVisionParser
from utils.prompt_helpers import register_midjourney, embed_sequence_in_title


class MidjourneyGenerator:
    """Generates Midjourney prompts with AI assistance."""

    def __init__(self, config_path: str = "config/settings.json", use_ai: bool = True):
        """
        Initialize the Midjourney generator.

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
        Generate Midjourney album cover art prompt.

        Args:
            psalm_number: Psalm number (1-150)
            artist_name: Artist identifier
            custom_params: Optional custom parameters (aspect_ratio, style, etc.)

        Returns:
            Dictionary containing:
                - prompt: Midjourney prompt with embedded sequence ID
                - sequence_id: Unique tracking ID
                - metadata: Generation metadata
        """
        # Parse inputs
        psalm_data = self.psalm_parser.parse_psalm(psalm_number)
        vision_data = self.vision_parser.parse_brand_vision(artist_name)

        # Generate base prompt
        if self.use_ai and self.client:
            base_prompt = self._generate_with_ai(psalm_data, vision_data, custom_params)
        else:
            base_prompt = self._generate_template(psalm_data, vision_data, custom_params)

        # Build metadata
        metadata = self._build_metadata(vision_data, custom_params)

        # Add Midjourney parameters
        mj_params = self._build_mj_parameters(metadata, custom_params)
        full_prompt = f"{base_prompt} {mj_params}"

        # Register with sequence tracking
        sequence_id = register_midjourney(
            psalm_number=psalm_number,
            artist_name=artist_name,
            image_prompt=full_prompt,
            metadata=metadata
        )

        # Embed sequence ID in prompt (at the end, before parameters)
        final_prompt = f"{base_prompt} [{sequence_id}] {mj_params}"

        return {
            'prompt': final_prompt,
            'base_prompt': base_prompt,
            'sequence_id': sequence_id,
            'parameters': mj_params,
            'metadata': metadata,
            'psalm_number': psalm_number,
            'artist_name': artist_name
        }

    def _generate_with_ai(
        self,
        psalm_data: Dict[str, Any],
        vision_data: Dict[str, Any],
        custom_params: Optional[Dict[str, Any]]
    ) -> str:
        """Generate Midjourney prompt using AI."""
        system_prompt = """You are an expert at creating Midjourney prompts for album cover art.
Create vivid, artistic image descriptions that capture the spiritual essence of biblical psalms
while matching the artist's visual aesthetic.

Guidelines:
- Focus on imagery, mood, lighting, and composition
- Be specific but concise (50-100 words)
- Avoid text/words in the image
- Match the artist's color palette and style
- Create reverent, beautiful imagery
- Do not include Midjourney parameters (--ar, --s, etc.) - just the description"""

        user_prompt = f"""Create a Midjourney prompt for album cover art for Psalm {psalm_data['number']}.

PSALM THEMES: {', '.join(psalm_data['themes'])}
FIRST LINE: {psalm_data['first_line']}

ARTIST VISUAL AESTHETIC:
{vision_data.get('visual_aesthetic', {}).get('full_description', 'Minimalist, nature-inspired')}

COLOR PALETTE: {vision_data.get('visual_aesthetic', {}).get('color_palette', 'Deep blues, warm golds, earth tones')}

Create a prompt that captures the psalm's spiritual essence through visual imagery."""

        response = self.client.chat.completions.create(
            model=self.config['generation']['ai_model'],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,  # Slightly higher for creative imagery
            max_tokens=300
        )

        return response.choices[0].message.content.strip()

    def _generate_template(
        self,
        psalm_data: Dict[str, Any],
        vision_data: Dict[str, Any],
        custom_params: Optional[Dict[str, Any]]
    ) -> str:
        """Generate Midjourney prompt using template."""
        visual = vision_data.get('visual_aesthetic', {})
        themes = psalm_data['themes']

        # Build prompt based on themes
        imagery_map = {
            'praise': 'radiant light beams, uplifted hands, golden hour',
            'trust': 'peaceful landscape, solid rock formation, calm waters',
            'deliverance': 'breaking chains, dawn light, open door',
            'lament': 'stormy skies, lone figure, deep shadows',
            'creation': 'majestic mountains, starry sky, flowing water',
            'justice': 'balanced scales, strong pillars, clear light',
            'mercy': 'gentle rain, healing hands, soft glow',
            'guidance': 'winding path, guiding star, open book',
            'hope': 'sunrise, blooming flower, distant horizon'
        }

        # Get imagery for first theme
        primary_theme = themes[0] if themes else 'praise'
        imagery = imagery_map.get(primary_theme, 'peaceful landscape, natural beauty')

        # Get style and colors
        style = visual.get('style', 'minimalist, ethereal')
        colors = visual.get('color_palette', 'deep blues, warm golds, earth tones')

        prompt = f"{imagery}, {colors}, {style}, photorealistic, cinematic composition, album cover art"

        return prompt

    def _build_mj_parameters(
        self,
        metadata: Dict[str, Any],
        custom_params: Optional[Dict[str, Any]]
    ) -> str:
        """Build Midjourney command parameters."""
        params = []

        # Aspect ratio (default to square for album art)
        ar = custom_params.get('aspect_ratio', '1:1') if custom_params else '1:1'
        params.append(f"--ar {ar}")

        # Quality
        quality = custom_params.get('quality', 2) if custom_params else 2
        params.append(f"--q {quality}")

        # Stylization
        style = custom_params.get('stylize', 500) if custom_params else 500
        params.append(f"--s {style}")

        return ' '.join(params)

    def _build_metadata(
        self,
        vision_data: Dict[str, Any],
        custom_params: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build metadata for sequence tracking."""
        metadata = {}

        # Extract from vision
        visual = vision_data.get('visual_aesthetic', {})

        if visual.get('color_palette'):
            metadata['color_palette'] = visual['color_palette']

        if visual.get('style'):
            metadata['visual_style'] = visual['style']

        # Add parameters
        metadata['aspect_ratio'] = custom_params.get('aspect_ratio', '1:1') if custom_params else '1:1'
        metadata['quality'] = custom_params.get('quality', 2) if custom_params else 2
        metadata['stylize'] = custom_params.get('stylize', 500) if custom_params else 500

        # Add custom params
        if custom_params:
            metadata.update({k: v for k, v in custom_params.items()
                           if k not in ['aspect_ratio', 'quality', 'stylize']})

        return metadata

    def save_output(
        self,
        prompt_data: Dict[str, Any],
        output_dir: Optional[str] = None
    ) -> str:
        """
        Save generated Midjourney prompt to file.

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
        prompt_file = output_dir / self.config['output_files']['midjourney_prompt']
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(f"Sequence ID: {prompt_data['sequence_id']}\n")
            f.write(f"Psalm: {prompt_data['psalm_number']}\n")
            f.write(f"Artist: {prompt_data['artist_name']}\n")
            f.write(f"\n{'='*60}\n\n")
            f.write(f"FULL PROMPT:\n{prompt_data['prompt']}\n\n")
            f.write(f"BASE DESCRIPTION:\n{prompt_data['base_prompt']}\n\n")
            f.write(f"PARAMETERS:\n{prompt_data['parameters']}\n\n")
            f.write(f"METADATA:\n{json.dumps(prompt_data['metadata'], indent=2)}\n")

        return str(prompt_file)


if __name__ == "__main__":
    print("Midjourney Generator Test\n")

    generator = MidjourneyGenerator(use_ai=False)
    print("Available artists:", generator.vision_parser.list_available_artists())
    print("Available psalms:", len(generator.psalm_parser.list_available_psalms()))
