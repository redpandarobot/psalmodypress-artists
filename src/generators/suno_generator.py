"""
Suno Lyrics and Music Prompt Generator

Generates song lyrics and music generation prompts from psalm text and artist brand visions.
Integrates with sequence tracking system for unique ID generation.
"""

import sys
from pathlib import Path
import json
from typing import Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from parsers.psalm_parser import PsalmParser
from parsers.brand_vision_parser import BrandVisionParser
from utils.prompt_helpers import register_suno_lyrics, register_suno_music, embed_sequence_in_title


class SunoGenerator:
    """Generates Suno lyrics and music prompts with AI assistance."""

    def __init__(self, config_path: str = "config/settings.json", use_ai: bool = True):
        """
        Initialize the Suno generator.

        Args:
            config_path: Path to configuration file
            use_ai: Whether to use AI for generation (False = template-based only)
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

    def generate_lyrics(
        self,
        psalm_number: int,
        artist_name: str,
        custom_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate song lyrics from a psalm.

        Args:
            psalm_number: Psalm number (1-150)
            artist_name: Artist identifier
            custom_params: Optional custom parameters (genre, tempo, etc.)

        Returns:
            Dictionary containing:
                - lyrics: Generated song lyrics
                - sequence_id: Unique tracking ID
                - title: Song title with embedded sequence ID
                - metadata: Generation metadata
        """
        # Parse inputs
        psalm_data = self.psalm_parser.parse_psalm(psalm_number)
        vision_data = self.vision_parser.parse_brand_vision(artist_name)

        # Generate lyrics
        if self.use_ai and self.client:
            lyrics = self._generate_lyrics_with_ai(psalm_data, vision_data, custom_params)
        else:
            lyrics = self._generate_lyrics_template(psalm_data, vision_data, custom_params)

        # Determine genre and other metadata
        metadata = self._build_metadata(vision_data, custom_params)

        # Register with sequence tracking
        sequence_id = register_suno_lyrics(
            psalm_number=psalm_number,
            artist_name=artist_name,
            lyrics=lyrics,
            metadata=metadata
        )

        # Create title
        base_title = self._generate_title(psalm_data, vision_data)
        title_with_id = embed_sequence_in_title(base_title, sequence_id)

        return {
            'lyrics': lyrics,
            'sequence_id': sequence_id,
            'title': title_with_id,
            'base_title': base_title,
            'metadata': metadata,
            'psalm_number': psalm_number,
            'artist_name': artist_name
        }

    def generate_music_prompt(
        self,
        psalm_number: int,
        artist_name: str,
        custom_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate Suno music generation prompt.

        Args:
            psalm_number: Psalm number (1-150)
            artist_name: Artist identifier
            custom_params: Optional custom parameters

        Returns:
            Dictionary containing:
                - prompt: Music generation prompt
                - sequence_id: Unique tracking ID
                - metadata: Generation metadata
        """
        # Parse inputs
        psalm_data = self.psalm_parser.parse_psalm(psalm_number)
        vision_data = self.vision_parser.parse_brand_vision(artist_name)

        # Generate music prompt
        if self.use_ai and self.client:
            music_prompt = self._generate_music_prompt_with_ai(psalm_data, vision_data, custom_params)
        else:
            music_prompt = self._generate_music_prompt_template(vision_data, custom_params)

        # Build metadata
        metadata = self._build_metadata(vision_data, custom_params)

        # Register with sequence tracking
        sequence_id = register_suno_music(
            psalm_number=psalm_number,
            artist_name=artist_name,
            music_prompt=music_prompt,
            metadata=metadata
        )

        return {
            'prompt': music_prompt,
            'sequence_id': sequence_id,
            'metadata': metadata,
            'psalm_number': psalm_number,
            'artist_name': artist_name
        }

    def _generate_lyrics_with_ai(
        self,
        psalm_data: Dict[str, Any],
        vision_data: Dict[str, Any],
        custom_params: Optional[Dict[str, Any]]
    ) -> str:
        """Generate lyrics using AI (GPT-4)."""
        # Build prompt for AI
        system_prompt = self._build_lyrics_system_prompt()
        user_prompt = self._build_lyrics_user_prompt(psalm_data, vision_data, custom_params)

        # Call AI
        response = self.client.chat.completions.create(
            model=self.config['generation']['ai_model'],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.config['generation']['temperature'],
            max_tokens=self.config['generation']['max_tokens']
        )

        lyrics = response.choices[0].message.content.strip()
        return lyrics

    def _generate_lyrics_template(
        self,
        psalm_data: Dict[str, Any],
        vision_data: Dict[str, Any],
        custom_params: Optional[Dict[str, Any]]
    ) -> str:
        """Generate lyrics using template-based approach (no AI)."""
        # Simple template: restructure psalm text into verses
        lines = psalm_data['lines']

        # Group into verses (4 lines per verse)
        verses = []
        for i in range(0, len(lines), 4):
            verse_lines = lines[i:i+4]
            verses.append('\n'.join(verse_lines))

        # Add chorus from first line (repeated)
        chorus = lines[0] if lines else "Praise the Lord"

        # Build song structure: V1, C, V2, C, V3 (if available)
        song_parts = []

        if len(verses) >= 1:
            song_parts.append(f"[Verse 1]\n{verses[0]}")

        song_parts.append(f"\n[Chorus]\n{chorus}")

        if len(verses) >= 2:
            song_parts.append(f"\n[Verse 2]\n{verses[1]}")
            song_parts.append(f"\n[Chorus]\n{chorus}")

        if len(verses) >= 3:
            song_parts.append(f"\n[Verse 3]\n{verses[2]}")

        lyrics = '\n'.join(song_parts)
        return lyrics

    def _generate_music_prompt_with_ai(
        self,
        psalm_data: Dict[str, Any],
        vision_data: Dict[str, Any],
        custom_params: Optional[Dict[str, Any]]
    ) -> str:
        """Generate music prompt using AI."""
        system_prompt = "You are a music production expert who creates detailed music generation prompts for AI music tools like Suno."

        user_prompt = f"""Create a music generation prompt for Suno AI based on:

Psalm {psalm_data['number']} - Themes: {', '.join(psalm_data['themes'])}

Artist Style: {vision_data['summary']}
Musical Style: {vision_data.get('musical_style', {}).get('full_description', 'Contemporary worship')}

The prompt should specify: genre, tempo, mood, instrumentation, vocal style.
Keep it concise (1-2 sentences).
"""

        response = self.client.chat.completions.create(
            model=self.config['generation']['ai_model'],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )

        return response.choices[0].message.content.strip()

    def _generate_music_prompt_template(
        self,
        vision_data: Dict[str, Any],
        custom_params: Optional[Dict[str, Any]]
    ) -> str:
        """Generate music prompt using template."""
        musical_style = vision_data.get('musical_style', {})

        genre = "contemporary worship"
        if musical_style.get('genres'):
            genre = musical_style['genres'][0]

        tempo = musical_style.get('tempo', 'moderate tempo')
        instrumentation = musical_style.get('instrumentation', 'piano, acoustic guitar, strings')

        prompt = f"{genre}, {tempo}, {instrumentation}, warm vocals, contemplative mood"
        return prompt

    def _build_lyrics_system_prompt(self) -> str:
        """Build system prompt for lyrics generation."""
        return """You are an expert worship songwriter who adapts biblical psalms into modern, singable song lyrics.

Your task is to:
1. Preserve the spiritual essence and meaning of the psalm
2. Create lyrics that are easy to sing and remember
3. Use modern language while maintaining reverence
4. Structure the song with verses and a chorus
5. Match the artist's musical style and brand vision

Guidelines:
- Use [Verse 1], [Chorus], [Verse 2], etc. as section markers
- Make the chorus memorable and repeatable
- Keep verses 4-8 lines each
- Chorus should be 2-4 lines
- Use natural rhyme schemes appropriate to the genre
- Maintain the emotional tone of the psalm"""

    def _build_lyrics_user_prompt(
        self,
        psalm_data: Dict[str, Any],
        vision_data: Dict[str, Any],
        custom_params: Optional[Dict[str, Any]]
    ) -> str:
        """Build user prompt for lyrics generation."""
        prompt = f"""Create song lyrics adapted from Psalm {psalm_data['number']}.

PSALM TEXT:
{psalm_data['text']}

ARTIST BRAND VISION:
{vision_data['summary']}

MUSICAL STYLE:
{vision_data.get('musical_style', {}).get('full_description', 'Contemporary worship music')}

KEY THEMES:
{', '.join(psalm_data['themes'])}

TARGET STRUCTURE:
- 2-3 verses (4-6 lines each)
- 1 chorus (2-4 lines, repeatable)
- Song structure: Verse 1, Chorus, Verse 2, Chorus, Verse 3 (optional)

Generate the complete song lyrics with section markers."""

        return prompt

    def _generate_title(self, psalm_data: Dict[str, Any], vision_data: Dict[str, Any]) -> str:
        """Generate a song title."""
        # Use psalm title suggestion as base
        base = self.psalm_parser.get_psalm_title_suggestion(psalm_data)

        # Clean up
        title = base.replace('...', '').strip()

        # Add psalm number reference
        final_title = f"Psalm {psalm_data['number']} - {title}"

        return final_title

    def _build_metadata(
        self,
        vision_data: Dict[str, Any],
        custom_params: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build metadata for sequence tracking."""
        metadata = {}

        # Extract from vision
        musical_style = vision_data.get('musical_style', {})

        if musical_style.get('genres'):
            metadata['genre'] = musical_style['genres'][0]

        if musical_style.get('tempo'):
            metadata['tempo'] = musical_style['tempo']

        if musical_style.get('instrumentation'):
            metadata['instrumentation'] = musical_style['instrumentation']

        # Add custom params
        if custom_params:
            metadata.update(custom_params)

        return metadata

    def save_output(
        self,
        lyrics_data: Dict[str, Any],
        music_prompt_data: Optional[Dict[str, Any]] = None,
        output_dir: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Save generated lyrics and music prompt to files.

        Args:
            lyrics_data: Lyrics generation result
            music_prompt_data: Optional music prompt result
            output_dir: Optional custom output directory

        Returns:
            Dictionary of file paths written
        """
        if output_dir is None:
            output_dir = Path(self.config['paths']['output_base']) / \
                        lyrics_data['artist_name'] / \
                        f"psalm_{lyrics_data['psalm_number']:03d}"
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        files_written = {}

        # Save lyrics
        lyrics_file = output_dir / self.config['output_files']['suno_lyrics']
        with open(lyrics_file, 'w', encoding='utf-8') as f:
            f.write(f"Title: {lyrics_data['title']}\n")
            f.write(f"Sequence ID: {lyrics_data['sequence_id']}\n")
            f.write(f"Psalm: {lyrics_data['psalm_number']}\n")
            f.write(f"Artist: {lyrics_data['artist_name']}\n")
            f.write(f"\n{'='*60}\n\n")
            f.write(lyrics_data['lyrics'])

        files_written['lyrics'] = str(lyrics_file)

        # Save music prompt if provided
        if music_prompt_data:
            prompt_file = output_dir / self.config['output_files']['suno_prompt']
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(f"Sequence ID: {music_prompt_data['sequence_id']}\n")
                f.write(f"Psalm: {music_prompt_data['psalm_number']}\n")
                f.write(f"Artist: {music_prompt_data['artist_name']}\n")
                f.write(f"\n{'='*60}\n\n")
                f.write(music_prompt_data['prompt'])

            files_written['music_prompt'] = str(prompt_file)

        return files_written


if __name__ == "__main__":
    print("Suno Generator Test\n")

    # Test with template-based generation (no AI required)
    generator = SunoGenerator(use_ai=False)

    print("Available artists:", generator.vision_parser.list_available_artists())
    print("Available psalms:", len(generator.psalm_parser.list_available_psalms()))

    # Note: This test will fail if no input files exist
    # Run this after adding sample data
