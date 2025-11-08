#!/usr/bin/env python3
"""
Test script for all generators end-to-end.

Tests Suno, Midjourney, Typography, and YouTube generators.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from generators import SunoGenerator, MidjourneyGenerator, TypographyGenerator, YouTubeGenerator
from utils.prompt_helpers import get_tracker_statistics


def main():
    print("=" * 70)
    print("ALL GENERATORS - END-TO-END TEST")
    print("=" * 70)
    print()

    # Initialize all generators (template mode, no AI required)
    print("Initializing all generators (template mode)...")
    suno_gen = SunoGenerator(use_ai=False)
    midjourney_gen = MidjourneyGenerator(use_ai=False)
    typography_gen = TypographyGenerator(use_ai=False)
    youtube_gen = YouTubeGenerator(use_ai=False)
    print("✓ All generators initialized\n")

    # Check available data
    artists = suno_gen.vision_parser.list_available_artists()
    psalms = suno_gen.psalm_parser.list_available_psalms()

    if not artists or not psalms:
        print("ERROR: No input data found!")
        return

    test_artist = artists[0]
    test_psalm = psalms[0]

    print(f"Testing with: Artist '{test_artist}' and Psalm {test_psalm}")
    print("=" * 70)
    print()

    # 1. Suno Lyrics
    print("STEP 1: Generating Suno lyrics...")
    print("-" * 70)
    lyrics_result = suno_gen.generate_lyrics(test_psalm, test_artist)
    print(f"✓ Lyrics generated")
    print(f"  Sequence ID: {lyrics_result['sequence_id']}")
    print(f"  Title: {lyrics_result['title']}")
    print()

    # 2. Suno Music Prompt
    print("STEP 2: Generating Suno music prompt...")
    print("-" * 70)
    music_result = suno_gen.generate_music_prompt(test_psalm, test_artist)
    print(f"✓ Music prompt generated")
    print(f"  Sequence ID: {music_result['sequence_id']}")
    print(f"  Prompt: {music_result['prompt'][:80]}...")
    print()

    # 3. Midjourney Prompt
    print("STEP 3: Generating Midjourney prompt...")
    print("-" * 70)
    midjourney_result = midjourney_gen.generate_prompt(test_psalm, test_artist)
    print(f"✓ Midjourney prompt generated")
    print(f"  Sequence ID: {midjourney_result['sequence_id']}")
    print(f"  Prompt: {midjourney_result['base_prompt'][:80]}...")
    print(f"  Parameters: {midjourney_result['parameters']}")
    print()

    # 4. Typography Prompt
    print("STEP 4: Generating typography prompt...")
    print("-" * 70)
    typography_result = typography_gen.generate_prompt(test_psalm, test_artist)
    print(f"✓ Typography prompt generated")
    print(f"  Sequence ID: {typography_result['sequence_id']}")
    print(f"  Key Verse: {typography_result['key_verse'][:60]}...")
    print()

    # 5. YouTube Channel Info
    print("STEP 5: Generating YouTube channel info...")
    print("-" * 70)
    channel_result = youtube_gen.generate_channel_info(test_artist)
    print(f"✓ Channel info generated")
    print(f"  Title: {channel_result['title']}")
    print(f"  Keywords: {len(channel_result['keywords'])} keywords")
    print()

    # 6. YouTube Video Metadata
    print("STEP 6: Generating YouTube video metadata...")
    print("-" * 70)
    video_result = youtube_gen.generate_video_metadata(
        test_psalm,
        test_artist,
        song_title=lyrics_result['base_title']
    )
    print(f"✓ Video metadata generated")
    print(f"  Title: {video_result['title']}")
    print(f"  Tags: {len(video_result['tags'])} tags")
    print(f"  Category: {video_result['category']}")
    print()

    # Save all outputs
    print("STEP 7: Saving all outputs...")
    print("-" * 70)

    files = {}
    files.update(suno_gen.save_output(lyrics_result, music_result))
    files['midjourney'] = midjourney_gen.save_output(midjourney_result)
    files['typography'] = typography_gen.save_output(typography_result)
    files.update(youtube_gen.save_output(video_metadata=video_result))

    print(f"✓ All files saved:")
    for name, path in files.items():
        print(f"  - {name}: {path}")
    print()

    # Show tracking statistics
    print("STEP 8: Checking sequence tracking database...")
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
    print("✓ ALL GENERATORS TEST COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print()
    print("What was generated:")
    print("  1. ✓ Suno lyrics with sequence ID")
    print("  2. ✓ Suno music prompt with sequence ID")
    print("  3. ✓ Midjourney album cover prompt with sequence ID")
    print("  4. ✓ Typography prompt with sequence ID")
    print("  5. ✓ YouTube channel information")
    print("  6. ✓ YouTube video metadata")
    print("  7. ✓ All outputs saved to files")
    print("  8. ✓ All prompts registered in tracking database")
    print()
    print("Next steps:")
    print("  - Review all output files in data/output/")
    print("  - Add OPENAI_API_KEY to use AI-powered generation")
    print("  - Process all 150 psalms with: python src/main.py generate -a artist_name")
    print()


if __name__ == "__main__":
    main()
