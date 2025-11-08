"""
YouTube Metadata Generator

Generates YouTube channel information and video metadata (title, description, tags)
for psalm-based music videos.
"""

import sys
from pathlib import Path
import json
from typing import Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from parsers.psalm_parser import PsalmParser
from parsers.brand_vision_parser import BrandVisionParser


class YouTubeGenerator:
    """Generates YouTube metadata with AI assistance."""

    def __init__(self, config_path: str = "config/settings.json", use_ai: bool = True):
        """
        Initialize the YouTube generator.

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
        """Initialize AI client (Anthropic Claude or OpenAI) for AI-powered generation."""
        import os

        provider = self.config['generation'].get('provider', 'openai')

        try:
            if provider == 'anthropic':
                from anthropic import Anthropic

                api_key = os.getenv('ANTHROPIC_API_KEY')
                if not api_key:
                    print("Warning: ANTHROPIC_API_KEY not found. Falling back to template-based generation.")
                    self.use_ai = False
                    self.client = None
                else:
                    self.client = Anthropic(api_key=api_key)
                    self.provider = 'anthropic'
            else:  # openai
                from openai import OpenAI

                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    print("Warning: OPENAI_API_KEY not found. Falling back to template-based generation.")
                    self.use_ai = False
                    self.client = None
                else:
                    self.client = OpenAI(api_key=api_key)
                    self.provider = 'openai'
        except ImportError as e:
            print(f"Warning: {provider} package not installed. Falling back to template-based generation.")
            print(f"  Install with: pip install {provider}")
            self.use_ai = False
            self.client = None

    def generate_channel_info(
        self,
        artist_name: str
    ) -> Dict[str, Any]:
        """
        Generate YouTube channel title and description.

        Args:
            artist_name: Artist identifier

        Returns:
            Dictionary containing:
                - title: Channel title
                - description: Channel description
                - keywords: Channel keywords
        """
        vision_data = self.vision_parser.parse_brand_vision(artist_name)

        if self.use_ai and self.client:
            channel_info = self._generate_channel_with_ai(vision_data)
        else:
            channel_info = self._generate_channel_template(vision_data)

        return channel_info

    def generate_video_metadata(
        self,
        psalm_number: int,
        artist_name: str,
        song_title: Optional[str] = None,
        custom_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate YouTube video metadata.

        Args:
            psalm_number: Psalm number (1-150)
            artist_name: Artist identifier
            song_title: Optional custom song title
            custom_params: Optional custom parameters

        Returns:
            Dictionary containing:
                - title: Video title
                - description: Video description
                - tags: List of tags
                - category: Video category
        """
        # Parse inputs
        psalm_data = self.psalm_parser.parse_psalm(psalm_number)
        vision_data = self.vision_parser.parse_brand_vision(artist_name)

        # Generate title
        if song_title is None:
            song_title = self.psalm_parser.get_psalm_title_suggestion(psalm_data)

        # Generate metadata
        if self.use_ai and self.client:
            metadata = self._generate_video_with_ai(song_title, psalm_data, vision_data, custom_params)
        else:
            metadata = self._generate_video_template(song_title, psalm_data, vision_data, custom_params)

        metadata['psalm_number'] = psalm_number
        metadata['artist_name'] = artist_name

        return metadata

    def _generate_channel_with_ai(self, vision_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate channel info using AI."""
        artist_identity = vision_data.get('artist_identity', {})
        artist_name = artist_identity.get('name', vision_data['artist_name'])

        system_prompt = """You are a YouTube channel optimization expert.
Create compelling channel titles and descriptions that attract the right audience
while staying true to the artist's mission and vision."""

        user_prompt = f"""Create YouTube channel information for this worship music artist:

ARTIST NAME: {artist_name}
VISION: {vision_data['summary']}
THEMES: {', '.join(vision_data.get('themes', ['worship', 'psalms']))}
TARGET AUDIENCE: {vision_data.get('target_audience', {}).get('full_description', 'Worship music listeners')}

Provide:
1. Channel Title (include artist name and focus on psalms)
2. Channel Description (2-3 paragraphs, engaging, include mission and content focus)
3. Keywords (10-15 relevant keywords for channel)"""

        if self.provider == 'anthropic':
            response = self.client.messages.create(
                model=self.config['generation']['ai_model'],
                max_tokens=500,
                temperature=0.7,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            content = response.content[0].text
        else:  # openai
            response = self.client.chat.completions.create(
                model=self.config['generation']['ai_model'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            content = response.choices[0].message.content

        # Simple parsing - in production, you'd want more robust parsing
        return {
            'title': f"{artist_name} - Psalmody Press",
            'description': content,
            'keywords': self._extract_keywords_from_vision(vision_data)
        }

    def _generate_channel_template(self, vision_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate channel info using template."""
        artist_identity = vision_data.get('artist_identity', {})
        artist_name = artist_identity.get('name', vision_data['artist_name'])
        tagline = artist_identity.get('tagline', 'Worship Music from the Psalms')

        description = f"""{artist_name} - {tagline}

{vision_data['summary']}

On this channel, you'll find worship music inspired by all 150 Psalms, bringing ancient words to life through contemporary sound. Each song is crafted to create space for reflection, worship, and encounter with God.

New videos released regularly. Subscribe to join us on this journey through the Psalms.

Connect with us:
• Website: [Your Website]
• Instagram: @{vision_data['artist_name']}
• Spotify: {artist_name}

#Psalms #WorshipMusic #ChristianMusic"""

        return {
            'title': f"{artist_name} - Psalmody Press",
            'description': description,
            'keywords': self._extract_keywords_from_vision(vision_data)
        }

    def _generate_video_with_ai(
        self,
        song_title: str,
        psalm_data: Dict[str, Any],
        vision_data: Dict[str, Any],
        custom_params: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate video metadata using AI."""
        system_prompt = """You are a YouTube video optimization expert for worship music.
Create compelling titles, descriptions, and tags that maximize discoverability
while authentically representing the content."""

        user_prompt = f"""Create YouTube video metadata for a worship song based on Psalm {psalm_data['number']}.

SONG TITLE: {song_title}
PSALM THEMES: {', '.join(psalm_data['themes'])}
FIRST LINE: {psalm_data['first_line']}
ARTIST: {vision_data['artist_name']}

Provide:
1. Video Title (engaging, includes "Psalm {psalm_data['number']}", optimized for search)
2. Description (3 paragraphs: hook, psalm context, artist info, links, hashtags)
3. Tags (15-20 tags, mix of broad and specific, include "psalm {psalm_data['number']}")"""

        if self.provider == 'anthropic':
            response = self.client.messages.create(
                model=self.config['generation']['ai_model'],
                max_tokens=600,
                temperature=0.7,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            content = response.content[0].text
        else:  # openai
            response = self.client.chat.completions.create(
                model=self.config['generation']['ai_model'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=600
            )
            content = response.choices[0].message.content

        # Basic parsing
        return {
            'title': f"Psalm {psalm_data['number']} - {song_title} | {vision_data['artist_name']}",
            'description': content,
            'tags': self._generate_tags(psalm_data, vision_data),
            'category': 'Music'
        }

    def _generate_video_template(
        self,
        song_title: str,
        psalm_data: Dict[str, Any],
        vision_data: Dict[str, Any],
        custom_params: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate video metadata using template."""
        artist_identity = vision_data.get('artist_identity', {})
        artist_name = artist_identity.get('name', vision_data['artist_name'])

        # Title
        title = f"Psalm {psalm_data['number']} - {song_title} | {artist_name}"

        # Description
        description = f"""🎵 Psalm {psalm_data['number']} - {song_title}

{psalm_data['first_line']}

This worship song is inspired by Psalm {psalm_data['number']}, bringing the ancient words of Scripture to life through contemporary music. The themes of {', '.join(psalm_data['themes'][:3])} resonate throughout this piece, creating space for reflection and worship.

About {artist_name}:
{vision_data['summary']}

We're on a journey to create worship music for all 150 Psalms. Subscribe to follow along and discover the beauty of Scripture through song.

🔗 CONNECT WITH US:
• Website: [Your Website]
• Spotify: {artist_name}
• Instagram: @{vision_data['artist_name']}
• Apple Music: {artist_name}

📖 PSALM {psalm_data['number']} (excerpt):
{psalm_data['first_line']}

#Psalm{psalm_data['number']} #WorshipMusic #ChristianMusic #Psalms #BibleVerses
{' '.join(['#' + theme.title() for theme in psalm_data['themes'][:5]])}

© {artist_name} | Psalmody Press"""

        # Tags
        tags = self._generate_tags(psalm_data, vision_data)

        return {
            'title': title,
            'description': description,
            'tags': tags,
            'category': 'Music'
        }

    def _generate_tags(self, psalm_data: Dict[str, Any], vision_data: Dict[str, Any]) -> list:
        """Generate video tags."""
        tags = [
            f"psalm {psalm_data['number']}",
            "psalms",
            "worship music",
            "christian music",
            "contemporary worship",
            "bible verses",
            "scripture songs",
            vision_data['artist_name']
        ]

        # Add musical style tags
        musical = vision_data.get('musical_style', {})
        if musical.get('genres'):
            tags.extend([g.lower() for g in musical['genres']])

        # Add theme tags
        tags.extend(psalm_data['themes'])

        # Add artist identity
        artist_identity = vision_data.get('artist_identity', {})
        if artist_identity.get('name'):
            tags.append(artist_identity['name'].lower())

        # Remove duplicates and limit to 500 chars (YouTube limit)
        tags = list(dict.fromkeys(tags))  # Preserve order, remove duplicates

        # YouTube has 500 character limit for all tags combined
        total_length = 0
        final_tags = []
        for tag in tags:
            if total_length + len(tag) + 2 < 500:  # +2 for quotes/comma
                final_tags.append(tag)
                total_length += len(tag) + 2
            else:
                break

        return final_tags

    def _extract_keywords_from_vision(self, vision_data: Dict[str, Any]) -> list:
        """Extract keywords from vision for channel."""
        keywords = ['psalms', 'worship music', 'christian music', 'bible songs']

        # Add themes
        if vision_data.get('themes'):
            keywords.extend(vision_data['themes'][:5])

        # Add musical genres
        musical = vision_data.get('musical_style', {})
        if musical.get('genres'):
            keywords.extend([g.lower() for g in musical['genres']])

        return list(dict.fromkeys(keywords))[:15]  # Limit to 15 unique keywords

    def save_output(
        self,
        channel_info: Optional[Dict[str, Any]] = None,
        video_metadata: Optional[Dict[str, Any]] = None,
        output_dir: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Save generated YouTube metadata to files.

        Args:
            channel_info: Optional channel information
            video_metadata: Optional video metadata
            output_dir: Optional custom output directory

        Returns:
            Dictionary of file paths written
        """
        files_written = {}

        # Save channel info
        if channel_info:
            if output_dir is None:
                output_dir = Path(self.config['paths']['output_base'])
            else:
                output_dir = Path(output_dir)

            output_dir.mkdir(parents=True, exist_ok=True)

            channel_file = output_dir / self.config['output_files']['youtube_channel']
            with open(channel_file, 'w', encoding='utf-8') as f:
                json.dump(channel_info, f, indent=2)

            files_written['channel'] = str(channel_file)

        # Save video metadata
        if video_metadata:
            if output_dir is None:
                artist_name = video_metadata.get('artist_name', 'unknown')
                psalm_num = video_metadata.get('psalm_number', 0)
                output_dir = Path(self.config['paths']['output_base']) / \
                            artist_name / f"psalm_{psalm_num:03d}"
            else:
                output_dir = Path(output_dir)

            output_dir.mkdir(parents=True, exist_ok=True)

            video_file = output_dir / self.config['output_files']['youtube_video']
            with open(video_file, 'w', encoding='utf-8') as f:
                json.dump(video_metadata, f, indent=2)

            files_written['video'] = str(video_file)

        return files_written


if __name__ == "__main__":
    print("YouTube Generator Test\n")

    generator = YouTubeGenerator(use_ai=False)
    print("Available artists:", generator.vision_parser.list_available_artists())
    print("Available psalms:", len(generator.psalm_parser.list_available_psalms()))
