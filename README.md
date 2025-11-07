# Psalmody Press Artists

A content generation system that transforms Psalm translations and Artist Brand Visions into comprehensive creative assets for songs and music videos.

## Overview

This tool accepts:
- **Input**: 150 Psalm text files + Artist Brand Vision documents
- **Output**: Complete asset packages for each Psalm including Suno lyrics/prompts, Midjourney album art prompts, typography prompts, and YouTube metadata

## Directory Structure

```
psalmodypress-artists/
├── data/
│   ├── input/
│   │   ├── psalms/                    # Place your 150 psalm text files here
│   │   │   ├── psalm_001.txt
│   │   │   ├── psalm_002.txt
│   │   │   └── ... (through psalm_150.txt)
│   │   └── artists/                   # Artist brand visions
│   │       ├── artist_name/
│   │       │   └── brand_vision.md
│   │       └── ...
│   └── output/                        # Generated assets (auto-created)
│       └── [artist_name]/
│           └── psalm_[number]/
│               ├── suno_lyrics.txt
│               ├── suno_prompt.txt
│               ├── midjourney_prompt.txt
│               ├── typography_prompt.txt
│               ├── youtube_channel.json
│               └── youtube_video.json
├── src/
│   ├── generators/                    # Asset generation modules
│   ├── parsers/                       # Input file parsers
│   └── main.py                        # Main execution script
├── templates/                          # Prompt templates
└── config/                            # Configuration files
```

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Add Your Input Data**
   - Place 150 psalm text files in `data/input/psalms/` (plain text format)
   - Create artist directories in `data/input/artists/[artist_name]/`
   - Add `brand_vision.md` files for each artist

3. **Configure Settings**
   - Edit `config/settings.json` as needed

## Usage

### Generate Assets for Single Psalm
```bash
python src/main.py --artist "artist_name" --psalm 1
```

### Generate Assets for All 150 Psalms
```bash
python src/main.py --artist "artist_name" --all
```

### Generate for Multiple Artists
```bash
python src/main.py --all-artists --all
```

## Input File Formats

### Psalm Text Files
- **Location**: `data/input/psalms/`
- **Format**: Plain text (.txt)
- **Naming**: `psalm_001.txt` through `psalm_150.txt` (zero-padded)
- **Content**: The translated psalm text (WEB Translation or other)

### Artist Brand Vision
- **Location**: `data/input/artists/[artist_name]/brand_vision.md`
- **Format**: Markdown (.md)
- **Content**: Artist vision, style, themes, musical preferences, etc.

## Output Assets

For each Psalm + Artist combination, the following are generated:

1. **Suno Lyrics** (`suno_lyrics.txt`) - Song lyrics adapted from the psalm
2. **Suno Prompt** (`suno_prompt.txt`) - Music generation prompt for Suno AI
3. **Midjourney Prompt** (`midjourney_prompt.txt`) - Album cover art prompt
4. **Typography Prompt** (`typography_prompt.txt`) - Nano-Banana typography prompt
5. **YouTube Channel Info** (`youtube_channel.json`) - Channel title and description
6. **YouTube Video Info** (`youtube_video.json`) - Video title, description, and tags

## Sequence Tracking System

Every prompt sent to Suno and Midjourney receives a unique **5-character base-36 sequence ID** (e.g., `EO8HB`, `A1B2C`) that:

- **Uniquely identifies** each prompt in the database
- **Embeds in titles/filenames** for automatic tracking
- **Enables lookup** of original prompts from generated assets
- **Maintains audit trail** from creation through publishing

### Example Workflow

1. Generate lyrics for Psalm 23 → Get sequence ID `A1B2C`
2. Embed in Suno title: `"Psalm 23 - The Shepherd [A1B2C]"`
3. Download generated song: `psalm_23_a1b2c.mp3`
4. Extract `A1B2C` from filename → Look up original lyrics and metadata

### Database

All prompts and assets are tracked in `data/prompts.db` (SQLite):
- **60+ million unique IDs** available (36^5)
- **Full metadata** storage (genre, tempo, style, etc.)
- **Asset linking** (prompts → generated songs/images)
- **Query capabilities** for analytics and regeneration

For detailed information, see **[SEQUENCE_TRACKING.md](SEQUENCE_TRACKING.md)**

## Development

- Python 3.8+
- See `requirements.txt` for dependencies

## License

TBD
