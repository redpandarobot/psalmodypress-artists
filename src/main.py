#!/usr/bin/env python3
"""
Psalmody Press Artists - Main CLI

Generate complete asset packages for psalm-based worship songs.
Produces Suno lyrics/prompts, Midjourney art, typography, and YouTube metadata.
"""

import click
import sys
from pathlib import Path
from typing import Optional
import json

# Import generators
from generators import SunoGenerator, MidjourneyGenerator, TypographyGenerator, YouTubeGenerator
from parsers import PsalmParser, BrandVisionParser
from utils.prompt_helpers import get_tracker_statistics


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Psalmody Press Artists - Generate worship song assets from psalms."""
    pass


@cli.command()
@click.option('--artist', '-a', required=True, help='Artist name (directory in data/input/artists/)')
@click.option('--psalm', '-p', type=int, help='Single psalm number (1-150)')
@click.option('--start', type=int, default=1, help='Start psalm number for range')
@click.option('--end', type=int, default=150, help='End psalm number for range')
@click.option('--use-ai/--no-ai', default=False, help='Use AI for generation (requires OPENAI_API_KEY)')
@click.option('--output-dir', '-o', type=click.Path(), help='Custom output directory')
def generate(artist: str, psalm: Optional[int], start: int, end: int, use_ai: bool, output_dir: Optional[str]):
    """Generate all assets for one or more psalms."""

    click.echo("=" * 70)
    click.echo("PSALMODY PRESS ARTISTS - ASSET GENERATOR")
    click.echo("=" * 70)
    click.echo()

    # Validate inputs
    vision_parser = BrandVisionParser()
    available_artists = vision_parser.list_available_artists()

    if artist not in available_artists:
        click.echo(f"❌ Error: Artist '{artist}' not found.", err=True)
        click.echo(f"Available artists: {', '.join(available_artists)}", err=True)
        sys.exit(1)

    # Determine psalm range
    if psalm:
        psalm_numbers = [psalm]
    else:
        psalm_numbers = list(range(start, end + 1))

    psalm_parser = PsalmParser()
    available_psalms = psalm_parser.list_available_psalms()

    # Filter to only available psalms
    psalm_numbers = [p for p in psalm_numbers if p in available_psalms]

    if not psalm_numbers:
        click.echo("❌ Error: No psalms found in specified range.", err=True)
        sys.exit(1)

    # Initialize generators
    click.echo(f"Artist: {artist}")
    click.echo(f"Psalms to process: {len(psalm_numbers)} ({min(psalm_numbers)}-{max(psalm_numbers)})")
    click.echo(f"AI Generation: {'Enabled' if use_ai else 'Disabled (template mode)'}")
    click.echo()

    click.echo("Initializing generators...")
    suno_gen = SunoGenerator(use_ai=use_ai)
    midjourney_gen = MidjourneyGenerator(use_ai=use_ai)
    typography_gen = TypographyGenerator(use_ai=use_ai)
    youtube_gen = YouTubeGenerator(use_ai=use_ai)
    click.echo("✓ Generators ready")
    click.echo()

    # Generate channel info once
    click.echo("Generating YouTube channel information...")
    channel_info = youtube_gen.generate_channel_info(artist)
    youtube_gen.save_output(channel_info=channel_info)
    click.echo("✓ Channel info saved")
    click.echo()

    # Process each psalm
    total_psalms = len(psalm_numbers)

    for idx, psalm_num in enumerate(psalm_numbers, 1):
        click.echo("=" * 70)
        click.echo(f"Processing Psalm {psalm_num} ({idx}/{total_psalms})")
        click.echo("=" * 70)

        try:
            # 1. Generate Suno lyrics
            click.echo(f"  [1/5] Generating Suno lyrics...")
            lyrics_data = suno_gen.generate_lyrics(psalm_num, artist)
            click.echo(f"        ✓ Sequence ID: {lyrics_data['sequence_id']}")

            # 2. Generate Suno music prompt
            click.echo(f"  [2/5] Generating Suno music prompt...")
            music_data = suno_gen.generate_music_prompt(psalm_num, artist)
            click.echo(f"        ✓ Sequence ID: {music_data['sequence_id']}")

            # 3. Generate Midjourney prompt
            click.echo(f"  [3/5] Generating Midjourney prompt...")
            midjourney_data = midjourney_gen.generate_prompt(psalm_num, artist)
            click.echo(f"        ✓ Sequence ID: {midjourney_data['sequence_id']}")

            # 4. Generate Typography prompt
            click.echo(f"  [4/5] Generating typography prompt...")
            typography_data = typography_gen.generate_prompt(psalm_num, artist)
            click.echo(f"        ✓ Sequence ID: {typography_data['sequence_id']}")

            # 5. Generate YouTube metadata
            click.echo(f"  [5/5] Generating YouTube metadata...")
            video_data = youtube_gen.generate_video_metadata(
                psalm_num,
                artist,
                song_title=lyrics_data['base_title']
            )
            click.echo(f"        ✓ Video metadata ready")

            # Save all outputs
            click.echo(f"  Saving outputs...")
            output_path = output_dir if output_dir else None

            suno_gen.save_output(lyrics_data, music_data, output_path)
            midjourney_gen.save_output(midjourney_data, output_path)
            typography_gen.save_output(typography_data, output_path)
            youtube_gen.save_output(video_metadata=video_data, output_dir=output_path)

            click.echo(f"  ✓ All assets saved for Psalm {psalm_num}")
            click.echo()

        except Exception as e:
            click.echo(f"  ❌ Error processing Psalm {psalm_num}: {str(e)}", err=True)
            click.echo()
            continue

    # Final summary
    click.echo("=" * 70)
    click.echo("GENERATION COMPLETE")
    click.echo("=" * 70)
    click.echo()

    stats = get_tracker_statistics()
    click.echo(f"Total prompts registered: {stats['total_prompts']}")
    click.echo(f"Current sequence: {stats['current_sequence_id']}")
    click.echo()
    click.echo("Prompts by type:")
    for ptype, count in stats.get('prompts_by_type', {}).items():
        click.echo(f"  - {ptype}: {count}")
    click.echo()
    click.echo("✓ All done!")


@cli.command()
@click.option('--artist', '-a', help='Filter by artist name')
def stats(artist: Optional[str]):
    """Show sequence tracking statistics."""

    click.echo("SEQUENCE TRACKING STATISTICS")
    click.echo("=" * 70)
    click.echo()

    stats_data = get_tracker_statistics()

    click.echo(f"Current Sequence: {stats_data['current_sequence_id']} (#{stats_data['current_sequence']})")
    click.echo(f"Total Prompts: {stats_data['total_prompts']}")
    click.echo(f"Total Assets: {stats_data['total_assets']}")
    click.echo()

    if stats_data.get('prompts_by_type'):
        click.echo("Prompts by Type:")
        for ptype, count in stats_data['prompts_by_type'].items():
            click.echo(f"  {ptype:20s} {count:>5d}")
        click.echo()

    if stats_data.get('assets_by_type'):
        click.echo("Assets by Type:")
        for atype, count in stats_data['assets_by_type'].items():
            click.echo(f"  {atype:20s} {count:>5d}")
        click.echo()


@cli.command()
def list_artists():
    """List all available artists."""

    vision_parser = BrandVisionParser()
    artists = vision_parser.list_available_artists()

    click.echo("AVAILABLE ARTISTS")
    click.echo("=" * 70)
    click.echo()

    if not artists:
        click.echo("No artists found in data/input/artists/")
        click.echo()
        click.echo("Add artist directories with brand_vision.md files.")
        return

    for artist in artists:
        try:
            vision = vision_parser.parse_brand_vision(artist)
            click.echo(f"• {artist}")
            click.echo(f"  {vision['summary'][:80]}...")
            click.echo()
        except Exception as e:
            click.echo(f"• {artist} (Error loading: {e})")
            click.echo()


@cli.command()
def list_psalms():
    """List all available psalms."""

    psalm_parser = PsalmParser()
    psalms = psalm_parser.list_available_psalms()

    click.echo("AVAILABLE PSALMS")
    click.echo("=" * 70)
    click.echo()

    if not psalms:
        click.echo("No psalm files found in data/input/psalms/")
        click.echo()
        click.echo("Add psalm text files named: psalm_001.txt, psalm_002.txt, etc.")
        return

    click.echo(f"Total: {len(psalms)} psalms")
    click.echo(f"Range: Psalm {min(psalms)} - Psalm {max(psalms)}")
    click.echo()

    # Show gaps if any
    missing = [i for i in range(1, 151) if i not in psalms]
    if missing:
        click.echo(f"Missing: {len(missing)} psalms")
        if len(missing) <= 10:
            click.echo(f"  {', '.join(map(str, missing))}")
        else:
            click.echo(f"  {', '.join(map(str, missing[:10]))} ...")
        click.echo()


if __name__ == '__main__':
    cli()
