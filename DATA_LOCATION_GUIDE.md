# Data Location Guide for Psalmody Press Artists

## Where to Place Your Input Data

### 1. Psalm Text Files (150 Files)

**Location**: `data/input/psalms/`

**File Naming Convention**:
```
psalm_001.txt
psalm_002.txt
psalm_003.txt
...
psalm_150.txt
```

**Format**:
- Plain text files (.txt)
- UTF-8 encoding
- Zero-padded numbers (001-150)

**Content Example**:
```
Blessed is the man who doesn't walk in the counsel of the wicked,
nor stand on the path of sinners,
nor sit in the seat of scoffers;
but his delight is in Yahweh's law.
On his law he meditates day and night.
...
```

**How to Add**:
```bash
# Copy all 150 psalm files to the psalms directory
cp /path/to/your/psalms/*.txt data/input/psalms/
```

---

### 2. Artist Brand Vision Files

**Location**: `data/input/artists/[artist_name]/brand_vision.md`

**Directory Structure**:
```
data/input/artists/
├── sacred_soundscapes/
│   └── brand_vision.md
├── urban_worship/
│   └── brand_vision.md
└── acoustic_psalms/
    └── brand_vision.md
```

**Format**:
- Markdown files (.md)
- One `brand_vision.md` per artist
- Each artist gets their own subdirectory

**Required Sections in brand_vision.md**:
1. Artist Name & Identity
2. Musical Style & Genre
3. Artistic Vision & Mission
4. Visual Aesthetic
5. Target Audience
6. Themes & Messages
7. Production Preferences

**How to Add**:
```bash
# Create artist directory and add brand vision
mkdir -p data/input/artists/your_artist_name
cp /path/to/brand_vision.md data/input/artists/your_artist_name/
```

---

## Where Generated Output Will Go

**Location**: `data/output/[artist_name]/psalm_[number]/`

**Example Structure**:
```
data/output/
└── sacred_soundscapes/
    ├── psalm_001/
    │   ├── suno_lyrics.txt
    │   ├── suno_prompt.txt
    │   ├── midjourney_prompt.txt
    │   ├── typography_prompt.txt
    │   ├── youtube_channel.json
    │   └── youtube_video.json
    ├── psalm_002/
    │   └── ... (same files)
    └── ... (through psalm_150)
```

This directory is **auto-created** by the program - you don't need to create it manually.

---

## Quick Start Checklist

- [ ] Place 150 psalm text files in `data/input/psalms/`
- [ ] Create artist directory: `data/input/artists/[artist_name]/`
- [ ] Add `brand_vision.md` to the artist directory
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run the program (once implemented): `python src/main.py --artist "artist_name" --psalm 1`

---

## Full Directory Tree

```
psalmodypress-artists/
├── data/
│   ├── input/
│   │   ├── psalms/              ← PUT YOUR 150 PSALM FILES HERE
│   │   │   ├── psalm_001.txt
│   │   │   ├── psalm_002.txt
│   │   │   └── ...
│   │   └── artists/             ← PUT YOUR ARTIST BRAND VISIONS HERE
│   │       ├── artist_name_1/
│   │       │   └── brand_vision.md
│   │       └── artist_name_2/
│   │           └── brand_vision.md
│   └── output/                  ← AUTO-GENERATED OUTPUT GOES HERE
│       └── [created automatically]
├── src/
│   ├── generators/
│   ├── parsers/
│   └── main.py
├── templates/
├── config/
└── README.md
```

---

## Need Help?

See the README.md files in:
- `data/input/psalms/README.md` - Detailed psalm file format
- `data/input/artists/README.md` - Brand vision template and examples

## Next Steps

Once you've added your input data, the next phase is to implement the generation logic in the `src/` directory to process the psalms and brand visions into all the required output assets.
