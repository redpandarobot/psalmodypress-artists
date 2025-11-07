# Sequence Tracking System

## Overview

The Psalmody Press Artists system uses a **base-36 alphanumeric sequence ID system** to uniquely identify and track every prompt sent to Suno and Midjourney. This enables seamless tracking from prompt creation through asset generation and final publishing.

## Why Sequence Tracking?

When you generate hundreds of songs and images through Suno and Midjourney, you need a way to:

1. **Track which prompt created which asset** - Know exactly what lyrics/prompt generated each song or image
2. **Embed identifiers without semantic meaning** - IDs like `EO8HB` won't be interpreted as words by AI
3. **Maintain a complete audit trail** - Full database of all prompts and generated assets
4. **Enable downstream processing** - Automatically title and organize assets
5. **Support regeneration** - Re-run specific prompts or variations

## How It Works

### Base-36 Sequence IDs

- **Format**: 5-character alphanumeric (A-Z, 0-9)
- **Examples**: `00000`, `A1B2C`, `EO8HB`, `ZZZZZ`
- **Total capacity**: 60,466,176 unique IDs (36^5)
- **Case-insensitive**: `eo8hb` and `EO8HB` are the same

### Workflow

```
1. Generate Prompt → 2. Get Sequence ID → 3. Embed in Title → 4. Send to Service → 5. Track Asset
```

#### Example: Generating a Suno Song

**Step 1: Generate lyrics for Psalm 23**
```
The Lord is my shepherd, I shall not want
He makes me lie down in green pastures...
```

**Step 2: Register and get sequence ID**
```python
sequence_id = register_suno_lyrics(
    psalm_number=23,
    artist_name="sacred_soundscapes",
    lyrics="The Lord is my shepherd...",
    metadata={"genre": "ambient worship", "tempo": 80}
)
# Returns: "A1B2C"
```

**Step 3: Embed ID in song title**
```
Original: "Psalm 23 - The Shepherd"
With ID:  "Psalm 23 - The Shepherd [A1B2C]"
```

**Step 4: Submit to Suno with embedded ID**
- Suno processes the song
- The title becomes part of the generated file/metadata
- Output: `psalm_23_the_shepherd_a1b2c.mp3`

**Step 5: Track the generated asset**
```python
register_downloaded_asset(
    sequence_id="A1B2C",
    asset_type="suno_song",
    original_filename="psalm_23_the_shepherd_a1b2c.mp3",
    local_path="data/output/sacred_soundscapes/psalm_023/song.mp3"
)
```

**Step 6: Look up the original prompt anytime**
```python
prompt_info = lookup_prompt_by_id("A1B2C")
# Returns full prompt details, lyrics, metadata, etc.
```

## Database Schema

The system maintains a SQLite database (`data/prompts.db`) with three main tables:

### 1. `prompts` Table
Stores all generated prompts with sequence IDs.

| Column | Type | Description |
|--------|------|-------------|
| sequence_id | TEXT | Unique 5-char ID (e.g., 'EO8HB') |
| prompt_type | TEXT | 'suno_lyrics', 'suno_music', 'midjourney', 'typography' |
| psalm_number | INTEGER | 1-150 |
| artist_name | TEXT | Artist identifier |
| prompt_text | TEXT | The actual prompt |
| created_at | TIMESTAMP | When created |
| metadata | TEXT | JSON metadata |

### 2. `generated_assets` Table
Links sequence IDs to actual files from services.

| Column | Type | Description |
|--------|------|-------------|
| sequence_id | TEXT | Links to prompts table |
| asset_type | TEXT | 'suno_song', 'midjourney_image' |
| original_filename | TEXT | Filename from service |
| our_filename | TEXT | Our standardized filename |
| file_path | TEXT | Local file path |
| service_metadata | TEXT | JSON service data |
| created_at | TIMESTAMP | When registered |

### 3. `sequence_counter` Table
Tracks the current sequence number.

| Column | Type | Description |
|--------|------|-------------|
| current_value | INTEGER | Last used number (0 to 60,466,175) |
| last_updated | TIMESTAMP | Last update time |

## Usage in Code

### Registering Prompts

```python
from src.utils.prompt_helpers import (
    register_suno_lyrics,
    register_midjourney,
    embed_sequence_in_title
)

# Register Suno lyrics
seq_id = register_suno_lyrics(
    psalm_number=1,
    artist_name="my_artist",
    lyrics="Blessed is the man...",
    metadata={"genre": "worship", "key": "D"}
)

# Create title with embedded ID
title = embed_sequence_in_title("Psalm 1 - Blessed", seq_id)
# Result: "Psalm 1 - Blessed [00001]"

# Register Midjourney prompt
mj_seq = register_midjourney(
    psalm_number=1,
    artist_name="my_artist",
    image_prompt="Tree by water, golden hour, photorealistic --ar 1:1",
    metadata={"aspect_ratio": "1:1", "quality": 2}
)
```

### Extracting Sequence IDs

```python
from src.utils.prompt_helpers import (
    extract_sequence_from_title,
    extract_sequence_from_filename,
    lookup_prompt_by_id
)

# From Suno song title
title = "Psalm 23 - The Shepherd [A1B2C]"
seq = extract_sequence_from_title(title)  # Returns: "A1B2C"

# From Midjourney filename
filename = "midjourney_EO8HB_v4_upscale.png"
seq = extract_sequence_from_filename(filename)  # Returns: "EO8HB"

# Look up original prompt
prompt = lookup_prompt_by_id(seq)
print(prompt['prompt_text'])
print(prompt['psalm_number'])
print(prompt['metadata'])
```

### Registering Downloaded Assets

```python
from src.utils.prompt_helpers import register_downloaded_asset

# After downloading from Suno
register_downloaded_asset(
    sequence_id="A1B2C",
    asset_type="suno_song",
    original_filename="suno_xyz_abc_final.mp3",
    local_path="data/output/artist/psalm_023/song.mp3",
    service_metadata={"suno_job_id": "xyz-abc", "duration": 245}
)

# After downloading from Midjourney
register_downloaded_asset(
    sequence_id="EO8HB",
    asset_type="midjourney_image",
    original_filename="midjourney_job_12345.png",
    local_path="data/output/artist/psalm_023/cover.png",
    service_metadata={"midjourney_job_id": "12345", "upscaled": True}
)
```

## File Naming Conventions

### With Embedded Sequence IDs

**Suno Song Titles:**
```
"Psalm 1 - Blessed [00001]"
"Psalm 23 - The Shepherd [A1B2C]"
"Psalm 150 - Praise [EO8HB]"
```

**Midjourney Prompts:**
```
"Tree by water, photorealistic --ar 1:1 [00002]"
"Shepherd in pasture, golden hour --ar 1:1 [A1B2D]"
```

**Our Standardized Filenames:**
```
psalm_001_00001_song.mp3
psalm_023_A1B2C_song.mp3
psalm_001_00002_cover.png
psalm_023_A1B2D_cover.png
```

## API Reference

### Core Functions

#### `register_suno_lyrics(psalm_number, artist_name, lyrics, metadata=None) -> str`
Register Suno lyrics and get sequence ID.

#### `register_suno_music(psalm_number, artist_name, music_prompt, metadata=None) -> str`
Register Suno music generation prompt.

#### `register_midjourney(psalm_number, artist_name, image_prompt, metadata=None) -> str`
Register Midjourney image prompt.

#### `register_typography(psalm_number, artist_name, typography_prompt, metadata=None) -> str`
Register typography prompt.

#### `embed_sequence_in_title(base_title, sequence_id) -> str`
Add sequence ID to title: `"Title" -> "Title [ID]"`.

#### `extract_sequence_from_title(title) -> Optional[str]`
Extract sequence ID from title with `[ID]` format.

#### `extract_sequence_from_filename(filename) -> Optional[str]`
Find valid sequence ID anywhere in filename.

#### `lookup_prompt_by_id(sequence_id) -> Optional[Dict]`
Get full prompt information by sequence ID.

#### `register_downloaded_asset(sequence_id, asset_type, original_filename, local_path, service_metadata=None) -> int`
Register a downloaded asset from Suno/Midjourney.

#### `get_tracker_statistics() -> Dict`
Get database statistics (total prompts, assets, etc.).

## Sequence Number Format

### Conversion Examples

| Number | Base-36 ID | Description |
|--------|------------|-------------|
| 0 | `00000` | First sequence |
| 1 | `00001` | Second sequence |
| 35 | `0000Z` | 36th sequence |
| 36 | `00010` | 37th sequence (1 in base-36) |
| 1,295 | `000ZZ` | |
| 1,296 | `00100` | 36² |
| 46,656 | `01000` | 36³ |
| 1,679,616 | `10000` | 36⁴ |
| 60,466,175 | `ZZZZZ` | Maximum |

### Why 5 Characters?

- **Compact**: Short enough to embed in titles without clutter
- **Capacity**: 60+ million unique IDs (way more than needed)
- **Readable**: Not too long, easy to copy/paste
- **Non-semantic**: Won't be interpreted as words by AI models

## Best Practices

1. **Always register before sending to services** - Get the sequence ID first
2. **Embed IDs in titles/filenames** - Makes downstream tracking automatic
3. **Register assets after download** - Complete the tracking loop
4. **Use metadata fields** - Store additional context (genre, tempo, style, etc.)
5. **Query database for analysis** - Track what's working, what needs regeneration

## Examples

See:
- `src/sequence_generator.py` - Core sequence generation
- `src/prompt_tracker.py` - Database management
- `src/utils/prompt_helpers.py` - Convenience functions

Run tests:
```bash
python src/sequence_generator.py
python src/prompt_tracker.py
python src/utils/prompt_helpers.py
```

## Database Location

Default: `data/prompts.db`

To use a custom location:
```python
from src.prompt_tracker import get_tracker
tracker = get_tracker(db_path="path/to/custom.db")
```

## Troubleshooting

**Q: What if I forget to embed the sequence ID?**
A: You can still manually look up by psalm number and timestamp, but automation breaks down.

**Q: Can I use the same sequence ID twice?**
A: No - each ID is unique and auto-incremented.

**Q: What if I run out of IDs?**
A: With 60+ million IDs available, you won't. Even generating 1000 prompts per day would take 165+ years.

**Q: Can I reset the counter?**
A: Technically yes, but not recommended. The database maintains integrity through unique IDs.

**Q: How do I find all prompts for Psalm 23?**
```python
from src.prompt_tracker import get_tracker
tracker = get_tracker()
prompts = tracker.get_prompts_by_psalm(psalm_number=23, artist_name="my_artist")
```

## Summary

The sequence tracking system provides:
- ✅ Unique identification for every prompt
- ✅ Complete audit trail from prompt to asset
- ✅ Automated title/filename management
- ✅ Easy lookup and regeneration
- ✅ Metadata storage for analytics
- ✅ 60+ million capacity
- ✅ Simple API for all generators
