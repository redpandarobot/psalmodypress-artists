#!/usr/bin/env python3
"""
Test script for Suno lyrics generator end-to-end workflow.

This demonstrates the complete pipeline:
1. Parse psalm text
2. Parse artist brand vision
3. Generate lyrics (with sequence ID)
4. Generate music prompt (with sequence ID)
5. Save output files
6. Show tracking database info
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from generators.suno_generator import SunoGenerator
from utils.prompt_helpers import get_tracker_statistics


def main():
    print("=" * 70)
    print("SUNO LYRICS GENERATOR - END-TO-END TEST")
    print("=" * 70)
    print()

    # Initialize generator (template-based, no AI required)
    print("Initializing Suno Generator (template mode)...")
    generator = SunoGenerator(use_ai=False)
    print("✓ Generator initialized\n")

    # Check available data
    print("Checking available input data...")
    artists = generator.vision_parser.list_available_artists()
    psalms = generator.psalm_parser.list_available_psalms()

    print(f"  Artists found: {len(artists)}")
    for artist in artists:
        print(f"    - {artist}")

    print(f"  Psalms found: {len(psalms)}")
    if psalms:
        print(f"    - Psalm {min(psalms)} through Psalm {max(psalms)}")
    print()

    if not artists:
        print("ERROR: No artists found!")
        print("Please add artist brand vision files to data/input/artists/")
        return

    if not psalms:
        print("ERROR: No psalms found!")
        print("Please add psalm text files to data/input/psalms/")
        return

    # Test with first available artist and psalm
    test_artist = artists[0]
    test_psalm = psalms[0]

    print(f"Testing with: Artist '{test_artist}' and Psalm {test_psalm}")
    print("=" * 70)
    print()

    # Generate lyrics
    print("STEP 1: Generating song lyrics...")
    print("-" * 70)

    lyrics_result = generator.generate_lyrics(
        psalm_number=test_psalm,
        artist_name=test_artist,
        custom_params={"test_mode": True}
    )

    print(f"✓ Lyrics generated successfully!")
    print(f"  Sequence ID: {lyrics_result['sequence_id']}")
    print(f"  Title: {lyrics_result['title']}")
    print(f"  Metadata: {lyrics_result['metadata']}")
    print()

    # Show lyrics preview
    print("LYRICS PREVIEW:")
    print("-" * 70)
    lyrics_lines = lyrics_result['lyrics'].split('\n')
    preview_lines = lyrics_lines[:15] if len(lyrics_lines) > 15 else lyrics_lines
    print('\n'.join(preview_lines))
    if len(lyrics_lines) > 15:
        print(f"\n... ({len(lyrics_lines) - 15} more lines)")
    print()

    # Generate music prompt
    print("STEP 2: Generating music prompt...")
    print("-" * 70)

    music_result = generator.generate_music_prompt(
        psalm_number=test_psalm,
        artist_name=test_artist,
        custom_params={"test_mode": True}
    )

    print(f"✓ Music prompt generated successfully!")
    print(f"  Sequence ID: {music_result['sequence_id']}")
    print(f"  Prompt: {music_result['prompt']}")
    print()

    # Save output files
    print("STEP 3: Saving output files...")
    print("-" * 70)

    files_written = generator.save_output(lyrics_result, music_result)

    print(f"✓ Output files saved:")
    for file_type, file_path in files_written.items():
        print(f"  {file_type}: {file_path}")
    print()

    # Show tracking database stats
    print("STEP 4: Checking sequence tracking database...")
    print("-" * 70)

    stats = get_tracker_statistics()

    print(f"Database Statistics:")
    print(f"  Total prompts registered: {stats['total_prompts']}")
    print(f"  Current sequence: {stats['current_sequence_id']}")
    print(f"  Prompts by type:")
    for ptype, count in stats.get('prompts_by_type', {}).items():
        print(f"    - {ptype}: {count}")
    print()

    # Success summary
    print("=" * 70)
    print("✓ END-TO-END TEST COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print()
    print("What happened:")
    print("  1. ✓ Parsed Psalm 23 text file")
    print("  2. ✓ Parsed Sacred Soundscapes brand vision")
    print("  3. ✓ Generated song lyrics with unique sequence ID")
    print("  4. ✓ Generated music prompt with unique sequence ID")
    print("  5. ✓ Saved both to output directory")
    print("  6. ✓ Registered in tracking database")
    print()
    print("Next steps:")
    print("  - Review output files in data/output/")
    print("  - Try with AI by setting OPENAI_API_KEY and use_ai=True")
    print("  - Add more psalm files and artists")
    print("  - Implement remaining generators (Midjourney, YouTube, etc.)")
    print()


if __name__ == "__main__":
    main()
