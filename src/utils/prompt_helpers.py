"""
Prompt Helper Utilities

Convenience functions for registering prompts and managing sequence IDs
across all generator modules.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from prompt_tracker import get_tracker
from typing import Dict, Any, Optional


def register_suno_lyrics(
    psalm_number: int,
    artist_name: str,
    lyrics: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Register Suno lyrics prompt and get sequence ID.

    Args:
        psalm_number: Psalm number (1-150)
        artist_name: Artist identifier
        lyrics: The generated lyrics
        metadata: Optional metadata (genre, style, etc.)

    Returns:
        5-character sequence ID to embed in Suno prompt
    """
    tracker = get_tracker()
    return tracker.register_prompt(
        prompt_type="suno_lyrics",
        psalm_number=psalm_number,
        artist_name=artist_name,
        prompt_text=lyrics,
        metadata=metadata
    )


def register_suno_music(
    psalm_number: int,
    artist_name: str,
    music_prompt: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Register Suno music generation prompt and get sequence ID.

    Args:
        psalm_number: Psalm number (1-150)
        artist_name: Artist identifier
        music_prompt: The music generation prompt
        metadata: Optional metadata (tempo, instrumentation, etc.)

    Returns:
        5-character sequence ID to embed in Suno prompt
    """
    tracker = get_tracker()
    return tracker.register_prompt(
        prompt_type="suno_music",
        psalm_number=psalm_number,
        artist_name=artist_name,
        prompt_text=music_prompt,
        metadata=metadata
    )


def register_midjourney(
    psalm_number: int,
    artist_name: str,
    image_prompt: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Register Midjourney image prompt and get sequence ID.

    Args:
        psalm_number: Psalm number (1-150)
        artist_name: Artist identifier
        image_prompt: The Midjourney prompt
        metadata: Optional metadata (aspect ratio, style params, etc.)

    Returns:
        5-character sequence ID to embed in Midjourney prompt
    """
    tracker = get_tracker()
    return tracker.register_prompt(
        prompt_type="midjourney",
        psalm_number=psalm_number,
        artist_name=artist_name,
        prompt_text=image_prompt,
        metadata=metadata
    )


def register_typography(
    psalm_number: int,
    artist_name: str,
    typography_prompt: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Register Nano-Banana typography prompt and get sequence ID.

    Args:
        psalm_number: Psalm number (1-150)
        artist_name: Artist identifier
        typography_prompt: The typography prompt
        metadata: Optional metadata (font style, effects, etc.)

    Returns:
        5-character sequence ID
    """
    tracker = get_tracker()
    return tracker.register_prompt(
        prompt_type="typography",
        psalm_number=psalm_number,
        artist_name=artist_name,
        prompt_text=typography_prompt,
        metadata=metadata
    )


def embed_sequence_in_title(base_title: str, sequence_id: str) -> str:
    """
    Embed sequence ID in a title for Suno or Midjourney.

    Args:
        base_title: Base title (e.g., "Psalm 23 - The Lord is My Shepherd")
        sequence_id: 5-character sequence ID

    Returns:
        Title with embedded sequence ID

    Example:
        "Psalm 23 - The Lord is My Shepherd" -> "Psalm 23 - The Lord is My Shepherd [EO8HB]"
    """
    return f"{base_title} [{sequence_id}]"


def extract_sequence_from_title(title: str) -> Optional[str]:
    """
    Extract sequence ID from a title.

    Args:
        title: Title with embedded sequence (e.g., "Song Title [EO8HB]")

    Returns:
        Sequence ID or None if not found

    Example:
        "Psalm 23 - The Lord is My Shepherd [EO8HB]" -> "EO8HB"
    """
    import re
    match = re.search(r'\[([A-Z0-9]{5})\]', title)
    return match.group(1) if match else None


def extract_sequence_from_filename(filename: str) -> Optional[str]:
    """
    Extract sequence ID from a filename.

    Args:
        filename: Filename that may contain a sequence ID

    Returns:
        Sequence ID or None if not found

    Example:
        "song_EO8HB_final.mp3" -> "EO8HB"
        "midjourney_A1B2C_upscaled.png" -> "A1B2C"
    """
    import re
    # Match 5-character uppercase alphanumeric sequences
    matches = re.findall(r'[A-Z0-9]{5}', filename.upper())

    # Validate each match
    from sequence_generator import validate_sequence_id
    for match in matches:
        if validate_sequence_id(match):
            return match

    return None


def lookup_prompt_by_id(sequence_id: str) -> Optional[Dict[str, Any]]:
    """
    Look up prompt information by sequence ID.

    Args:
        sequence_id: 5-character sequence ID

    Returns:
        Prompt information dict or None
    """
    tracker = get_tracker()
    return tracker.get_prompt(sequence_id)


def register_downloaded_asset(
    sequence_id: str,
    asset_type: str,
    original_filename: str,
    local_path: str,
    service_metadata: Optional[Dict[str, Any]] = None
) -> int:
    """
    Register an asset downloaded from Suno or Midjourney.

    Args:
        sequence_id: Sequence ID from the title/filename
        asset_type: 'suno_song' or 'midjourney_image'
        original_filename: Original filename from service
        local_path: Where we saved the file locally
        service_metadata: Optional service-specific data

    Returns:
        Asset database ID
    """
    tracker = get_tracker()

    # Create our standardized filename
    prompt = tracker.get_prompt(sequence_id)
    if prompt:
        extension = Path(original_filename).suffix
        our_filename = f"psalm_{prompt['psalm_number']:03d}_{sequence_id}_{asset_type}{extension}"
    else:
        our_filename = original_filename

    return tracker.register_asset(
        sequence_id=sequence_id,
        asset_type=asset_type,
        original_filename=original_filename,
        our_filename=our_filename,
        file_path=local_path,
        service_metadata=service_metadata
    )


def get_tracker_statistics() -> Dict[str, Any]:
    """
    Get prompt tracker statistics.

    Returns:
        Statistics dictionary
    """
    tracker = get_tracker()
    return tracker.get_statistics()


if __name__ == "__main__":
    # Example usage
    print("Prompt Helpers Usage Example\n")

    # Register a Suno lyrics prompt
    seq_id = register_suno_lyrics(
        psalm_number=23,
        artist_name="test_artist",
        lyrics="The Lord is my shepherd...",
        metadata={"genre": "worship", "tempo": 80}
    )
    print(f"Registered Suno lyrics: {seq_id}")

    # Embed in title
    title = embed_sequence_in_title("Psalm 23 - The Shepherd", seq_id)
    print(f"Suno title with ID: {title}")

    # Extract from title
    extracted = extract_sequence_from_title(title)
    print(f"Extracted sequence: {extracted}")

    # Look up the prompt
    prompt_info = lookup_prompt_by_id(extracted)
    print(f"\nPrompt info:")
    print(f"  Type: {prompt_info['prompt_type']}")
    print(f"  Psalm: {prompt_info['psalm_number']}")
    print(f"  Artist: {prompt_info['artist_name']}")

    # Statistics
    stats = get_tracker_statistics()
    print(f"\nStatistics: {stats}")
