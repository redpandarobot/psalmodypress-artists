# Psalmody Press Artists - Usage Guide

Complete guide for generating worship song assets from psalms.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Step-by-Step Tutorial](#step-by-step-tutorial)
3. [All Available Commands](#all-available-commands)
4. [Generated Assets](#generated-assets)
5. [Customization](#customization)
6. [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Install and Test

```bash
# Install dependencies
pip install -r requirements.txt

# Test with sample data (no API key needed)
python test_all_generators.py
```

This generates all assets for Psalm 1 and saves them to `data/output/sacred_soundscapes/psalm_001/`.

### 2. View the Generated Assets

```bash
ls -la data/output/sacred_soundscapes/psalm_001/
```

You should see:
- `suno_lyrics.txt` - Song lyrics with sequence ID
- `suno_prompt.txt` - Music generation prompt
- `midjourney_prompt.txt` - Album cover art prompt
- `typography_prompt.txt` - Typography design prompt
- `youtube_video.json` - Video metadata (title, description, tags)

## Step-by-Step Tutorial

### Step 1: Add Your Psalm Files

Place your 150 psalm text files in `data/input/psalms/`:

```
data/input/psalms/
├── psalm_001.txt
├── psalm_002.txt
├── psalm_003.txt
└── ... (through psalm_150.txt)
```

**File Format**: Plain text, one psalm per file. Metadata headers (lines starting with `#` or `===`) are automatically stripped.

**Example** (`psalm_023.txt`):
```
The Lord is my shepherd; I shall not want.
He makes me lie down in green pastures.
He leads me beside still waters.
...
```

### Step 2: Create Your Artist Brand Vision

Create a directory for your artist in `data/input/artists/`:

```bash
mkdir -p data/input/artists/your_artist_name
```

Add a `brand_vision.md` file with your artist's vision and style. Use `data/input/artists/sacred_soundscapes/brand_vision.md` as a template.

**Required Sections**:
- Artist Name & Identity
- Musical Style & Genre
- Artistic Vision & Mission
- Visual Aesthetic
- Target Audience
- Themes & Messages
- Production Preferences

### Step 3: Generate Assets for One Psalm

```bash
python src/main.py generate --artist your_artist_name --psalm 1
```

This creates:
```
data/output/your_artist_name/psalm_001/
├── suno_lyrics.txt
├── suno_prompt.txt
├── midjourney_prompt.txt
├── typography_prompt.txt
└── youtube_video.json
```

### Step 4: Review and Use the Outputs

**Suno Lyrics** (`suno_lyrics.txt`):
- Copy the lyrics
- Paste into Suno with the title that includes `[XXXXX]` sequence ID
- Example: `"Psalm 1 - Blessed [00001]"`

**Suno Music Prompt** (`suno_prompt.txt`):
- Use this prompt to describe the musical style to Suno
- Contains genre, tempo, instrumentation, mood

**Midjourney Prompt** (`midjourney_prompt.txt`):
- Copy the FULL PROMPT line
- Paste into Midjourney
- The sequence ID `[XXXXX]` is embedded in the prompt
- Parameters (--ar, --q, --s) are included

**Typography Prompt** (`typography_prompt.txt`):
- Use for Nano-Banana or other typography tools
- Contains the key verse and design specifications

**YouTube Metadata** (`youtube_video.json`):
- Use title, description, and tags for your YouTube upload
- Optimized for discoverability

### Step 5: Track Your Assets

After downloading songs/images from Suno/Midjourney:

```python
from src.utils.prompt_helpers import (
    extract_sequence_from_filename,
    lookup_prompt_by_id,
    register_downloaded_asset
)

# Extract sequence ID from filename
seq_id = extract_sequence_from_filename("suno_song_00001.mp3")

# Look up the original prompt
prompt_info = lookup_prompt_by_id(seq_id)

# Register the downloaded asset
register_downloaded_asset(
    sequence_id=seq_id,
    asset_type="suno_song",
    original_filename="suno_song_00001.mp3",
    local_path="my_songs/psalm_001.mp3"
)
```

## All Available Commands

### Generate Command

Generate assets for one or more psalms:

```bash
# Single psalm
python src/main.py generate -a artist_name -p 23

# Range of psalms
python src/main.py generate -a artist_name --start 1 --end 10

# All 150 psalms
python src/main.py generate -a artist_name --start 1 --end 150

# With AI generation (requires OPENAI_API_KEY)
export OPENAI_API_KEY=sk-...
python src/main.py generate -a artist_name -p 23 --use-ai

# Custom output directory
python src/main.py generate -a artist_name -p 23 -o /path/to/output
```

### List Commands

```bash
# List all available artists
python src/main.py list-artists

# List all available psalms
python src/main.py list-psalms
```

### Stats Command

```bash
# View sequence tracking statistics
python src/main.py stats
```

## Generated Assets

### 1. Suno Lyrics (`suno_lyrics.txt`)

**Format**:
```
Title: Psalm 23 - The Lord is My Shepherd [A1B2C]
Sequence ID: A1B2C
Psalm: 23
Artist: sacred_soundscapes

============================================================

[Verse 1]
The Lord is my shepherd, I shall not want
He makes me lie down in green pastures
...

[Chorus]
The Lord is my shepherd
...
```

**How to Use**:
1. Copy the title (with `[XXXXX]` sequence ID)
2. Copy the lyrics
3. Paste both into Suno
4. Generate song
5. Download with sequence ID in filename

### 2. Suno Music Prompt (`suno_prompt.txt`)

**Format**:
```
Sequence ID: A1B2D
Psalm: 23
Artist: sacred_soundscapes

============================================================

Contemporary Christian Worship, slow tempo (70 BPM),
piano, strings, ambient pads, warm vocals, peaceful mood
```

**How to Use**:
- Use as the "style description" in Suno
- Guides the AI on musical style and instrumentation

### 3. Midjourney Prompt (`midjourney_prompt.txt`)

**Format**:
```
Sequence ID: A1B2E
Psalm: 23
Artist: sacred_soundscapes

============================================================

FULL PROMPT:
peaceful shepherd in green pasture, gentle stream, golden hour lighting,
deep blues, warm golds, minimalist, ethereal, photorealistic [A1B2E]
--ar 1:1 --q 2 --s 500

BASE DESCRIPTION:
peaceful shepherd in green pasture, gentle stream, golden hour lighting,
deep blues, warm golds, minimalist, ethereal, photorealistic

PARAMETERS:
--ar 1:1 --q 2 --s 500
```

**How to Use**:
1. Copy the FULL PROMPT
2. Paste into Midjourney
3. Generate image
4. The sequence ID `[A1B2E]` will be in the filename
5. Easy to match with original prompt

### 4. Typography Prompt (`typography_prompt.txt`)

**Format**:
```
Sequence ID: A1B2F
Psalm: 23
Artist: sacred_soundscapes

============================================================

KEY VERSE:
"The Lord is my shepherd; I shall not want."

TYPOGRAPHY PROMPT:
Modern serif font, elegant and clean. Deep blue text with
warm gold accents. Centered layout, generous spacing.
Subtle shadows, minimal background. Reverent and beautiful.
```

**How to Use**:
- Use with Nano-Banana or other typography tools
- Provides the verse and design specifications

### 5. YouTube Metadata (`youtube_video.json`)

**Format**:
```json
{
  "title": "Psalm 23 - The Lord is My Shepherd | Sacred Soundscapes",
  "description": "🎵 Psalm 23 - The Lord is My Shepherd\n\n...",
  "tags": ["psalm 23", "worship music", "christian music", ...],
  "category": "Music"
}
```

**How to Use**:
1. Upload video to YouTube
2. Copy title from JSON
3. Copy description from JSON
4. Add all tags (comma-separated)
5. Set category to Music

## Customization

### Custom Metadata

You can pass custom parameters to generators:

```python
from src.generators import SunoGenerator

generator = SunoGenerator(use_ai=False)

# Generate with custom parameters
result = generator.generate_lyrics(
    psalm_number=23,
    artist_name="my_artist",
    custom_params={
        "genre": "ambient",
        "tempo": 60,
        "key": "D major"
    }
)
```

### Custom Templates

Edit the templates in `templates/` directory to customize generation:
- `suno_template.txt`
- `midjourney_template.txt`
- `typography_template.txt`
- `youtube_template.txt`

### Configuration

Edit `config/settings.json` to customize:
- AI model (default: gpt-4)
- Temperature (creativity level)
- Max tokens (response length)
- File paths
- Output file names

## Troubleshooting

### No Artists Found

```
ERROR: No artists found in data/input/artists/
```

**Solution**: Create an artist directory with `brand_vision.md`:
```bash
mkdir -p data/input/artists/my_artist
cp data/input/artists/sacred_soundscapes/brand_vision.md data/input/artists/my_artist/
# Edit the file with your artist info
```

### No Psalms Found

```
ERROR: No psalms found in data/input/psalms/
```

**Solution**: Add psalm text files with correct naming:
```bash
# Files must be named: psalm_001.txt, psalm_002.txt, etc.
ls data/input/psalms/
```

### OpenAI API Error

```
Warning: OPENAI_API_KEY not found. Falling back to template-based generation.
```

**Solution**:
```bash
# Set your API key
export OPENAI_API_KEY=sk-your-key-here

# Or add to .env file
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

### Module Not Found: click

```
ModuleNotFoundError: No module named 'click'
```

**Solution**:
```bash
pip install click
# Or install all requirements
pip install -r requirements.txt
```

### Sequence ID Not Embedded

If sequence IDs aren't appearing in outputs, check:
1. Sequence tracking database is being created (`data/prompts.db`)
2. Generators are calling `register_*` functions
3. Output files show sequence IDs in headers

View stats to verify:
```bash
python src/main.py stats
```

## Next Steps

1. **Generate for all 150 psalms**:
   ```bash
   python src/main.py generate -a your_artist --start 1 --end 150
   ```

2. **Try AI-powered generation** for higher quality:
   ```bash
   export OPENAI_API_KEY=sk-...
   python src/main.py generate -a your_artist -p 1 --use-ai
   ```

3. **Create multiple artist brands** for different styles

4. **Track all generated assets** using the sequence ID system

5. **Build your workflow**:
   - Generate prompts → Submit to Suno/Midjourney → Download assets → Track with sequence IDs → Upload to YouTube

## Support

- See `README.md` for overview
- See `SEQUENCE_TRACKING.md` for detailed tracking system docs
- See `DATA_LOCATION_GUIDE.md` for file organization
- Check example outputs in `data/output/sacred_soundscapes/psalm_001/`
