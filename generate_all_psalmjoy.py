#!/usr/bin/env python3
"""
Batch generate all 150 psalms for PsalmJoy artist
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from generators import SunoGenerator, MidjourneyGenerator, TypographyGenerator, YouTubeGenerator
from utils.prompt_helpers import get_tracker_statistics


def main():
    artist_name = "PsalmJoy"

    print("=" * 70)
    print(f"GENERATING ALL 150 PSALMS FOR {artist_name.upper()}")
    print("=" * 70)
    print()

    # Initialize all generators (template mode, no AI required)
    print("Initializing generators...")
    suno_gen = SunoGenerator(use_ai=False)
    midjourney_gen = MidjourneyGenerator(use_ai=False)
    typography_gen = TypographyGenerator(use_ai=False)
    youtube_gen = YouTubeGenerator(use_ai=False)
    print("✓ All generators initialized\n")

    # Get available psalms
    available_psalms = suno_gen.psalm_parser.list_available_psalms()

    print(f"Available psalms: {len(available_psalms)}")
    print(f"Range: Psalm {min(available_psalms)} - Psalm {max(available_psalms)}")
    print()

    # Generate channel info once
    print("Generating YouTube channel information...")
    channel_info = youtube_gen.generate_channel_info(artist_name)
    youtube_gen.save_output(channel_info=channel_info)
    print("✓ Channel info saved\n")

    # Process each psalm
    total = len(available_psalms)
    success_count = 0
    error_count = 0

    for idx, psalm_num in enumerate(available_psalms, 1):
        print(f"[{idx}/{total}] Processing Psalm {psalm_num}...")

        try:
            # Generate all assets
            lyrics_data = suno_gen.generate_lyrics(psalm_num, artist_name)
            music_data = suno_gen.generate_music_prompt(psalm_num, artist_name)
            midjourney_data = midjourney_gen.generate_prompt(psalm_num, artist_name)
            typography_data = typography_gen.generate_prompt(psalm_num, artist_name)
            video_data = youtube_gen.generate_video_metadata(
                psalm_num,
                artist_name,
                song_title=lyrics_data['base_title']
            )

            # Save outputs
            suno_gen.save_output(lyrics_data, music_data)
            midjourney_gen.save_output(midjourney_data)
            typography_gen.save_output(typography_data)
            youtube_gen.save_output(video_metadata=video_data)

            print(f"  ✓ Psalm {psalm_num} complete (IDs: {lyrics_data['sequence_id']}, "
                  f"{music_data['sequence_id']}, {midjourney_data['sequence_id']}, "
                  f"{typography_data['sequence_id']})")
            success_count += 1

        except Exception as e:
            print(f"  ❌ Error on Psalm {psalm_num}: {str(e)}")
            error_count += 1

        # Progress update every 10 psalms
        if idx % 10 == 0:
            print(f"  Progress: {idx}/{total} psalms processed ({success_count} success, {error_count} errors)")
            print()

    # Final summary
    print()
    print("=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70)
    print()
    print(f"Total psalms processed: {total}")
    print(f"Successful: {success_count}")
    print(f"Errors: {error_count}")
    print()

    # Show tracking stats
    stats = get_tracker_statistics()
    print("Sequence Tracking Statistics:")
    print(f"  Total prompts registered: {stats['total_prompts']}")
    print(f"  Current sequence: {stats['current_sequence_id']}")
    print()
    print("Prompts by type:")
    for ptype, count in stats.get('prompts_by_type', {}).items():
        print(f"  - {ptype}: {count}")
    print()

    print(f"✓ All outputs saved to: data/output/{artist_name}/")
    print()


if __name__ == "__main__":
    main()
