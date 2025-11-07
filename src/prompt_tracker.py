"""
Prompt Tracking Database Manager

Central system for registering prompts with unique sequence IDs and
tracking generated assets from Suno and Midjourney.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any
from contextlib import contextmanager

from sequence_generator import SequenceGenerator


class PromptTracker:
    """
    Manages the prompt tracking database.
    Thread-safe singleton for universal access across the application.
    """

    _instance = None
    _db_path = None

    def __new__(cls, db_path: str = None):
        """Singleton pattern - only one instance of PromptTracker."""
        if cls._instance is None:
            cls._instance = super(PromptTracker, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path: str = None):
        """
        Initialize the PromptTracker.

        Args:
            db_path: Path to SQLite database file. Only used on first initialization.
        """
        if self._initialized:
            return

        if db_path is None:
            # Default to data/prompts.db
            db_path = Path(__file__).parent.parent / "data" / "prompts.db"

        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

        self._initialize_database()
        self._initialized = True

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _initialize_database(self):
        """Create database tables if they don't exist."""
        schema_path = Path(__file__).parent / "database_schema.sql"

        with open(schema_path, 'r') as f:
            schema_sql = f.read()

        with self._get_connection() as conn:
            conn.executescript(schema_sql)

    def _get_next_sequence_id(self, conn: sqlite3.Connection) -> tuple[int, str]:
        """
        Get the next available sequence ID.

        Args:
            conn: Active database connection

        Returns:
            Tuple of (sequence_number, sequence_id)
        """
        cursor = conn.execute("SELECT current_value FROM sequence_counter WHERE id = 1")
        row = cursor.fetchone()
        current_value = row[0]

        next_num, next_seq = SequenceGenerator.get_next_sequence(current_value)

        # Update the counter
        conn.execute(
            "UPDATE sequence_counter SET current_value = ?, last_updated = ? WHERE id = 1",
            (next_num, datetime.now())
        )

        return next_num, next_seq

    def register_prompt(
        self,
        prompt_type: str,
        psalm_number: int,
        artist_name: str,
        prompt_text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Register a new prompt and get a unique sequence ID.

        Args:
            prompt_type: Type of prompt ('suno_lyrics', 'suno_music', 'midjourney', 'typography')
            psalm_number: Psalm number (1-150)
            artist_name: Artist identifier
            prompt_text: The actual prompt text
            metadata: Optional additional metadata as dict

        Returns:
            Unique 5-character sequence ID (e.g., 'EO8HB')
        """
        if not 1 <= psalm_number <= 150:
            raise ValueError(f"Psalm number must be between 1 and 150, got {psalm_number}")

        valid_types = ['suno_lyrics', 'suno_music', 'midjourney', 'typography']
        if prompt_type not in valid_types:
            raise ValueError(f"Invalid prompt_type. Must be one of: {valid_types}")

        metadata_json = json.dumps(metadata) if metadata else None

        with self._get_connection() as conn:
            _, sequence_id = self._get_next_sequence_id(conn)

            conn.execute(
                """
                INSERT INTO prompts (sequence_id, prompt_type, psalm_number, artist_name, prompt_text, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (sequence_id, prompt_type, psalm_number, artist_name, prompt_text, metadata_json)
            )

        return sequence_id

    def get_prompt(self, sequence_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve prompt information by sequence ID.

        Args:
            sequence_id: 5-character sequence ID

        Returns:
            Dictionary with prompt information or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM prompts WHERE sequence_id = ?",
                (sequence_id.upper(),)
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return {
                'sequence_id': row['sequence_id'],
                'prompt_type': row['prompt_type'],
                'psalm_number': row['psalm_number'],
                'artist_name': row['artist_name'],
                'prompt_text': row['prompt_text'],
                'created_at': row['created_at'],
                'metadata': json.loads(row['metadata']) if row['metadata'] else None
            }

    def register_asset(
        self,
        sequence_id: str,
        asset_type: str,
        original_filename: str,
        our_filename: str,
        file_path: str,
        service_metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Register a generated asset (song or image) from Suno/Midjourney.

        Args:
            sequence_id: The sequence ID that generated this asset
            asset_type: 'suno_song' or 'midjourney_image'
            original_filename: Original filename from the service
            our_filename: Our renamed filename
            file_path: Path where the file is stored
            service_metadata: Optional service-specific metadata

        Returns:
            Asset ID from database
        """
        valid_types = ['suno_song', 'midjourney_image']
        if asset_type not in valid_types:
            raise ValueError(f"Invalid asset_type. Must be one of: {valid_types}")

        metadata_json = json.dumps(service_metadata) if service_metadata else None

        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO generated_assets
                (sequence_id, asset_type, original_filename, our_filename, file_path, service_metadata)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (sequence_id.upper(), asset_type, original_filename, our_filename, file_path, metadata_json)
            )
            return cursor.lastrowid

    def get_prompts_by_psalm(self, psalm_number: int, artist_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all prompts for a specific psalm.

        Args:
            psalm_number: Psalm number (1-150)
            artist_name: Optional filter by artist

        Returns:
            List of prompt dictionaries
        """
        with self._get_connection() as conn:
            if artist_name:
                cursor = conn.execute(
                    "SELECT * FROM prompts WHERE psalm_number = ? AND artist_name = ? ORDER BY created_at",
                    (psalm_number, artist_name)
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM prompts WHERE psalm_number = ? ORDER BY created_at",
                    (psalm_number,)
                )

            return [dict(row) for row in cursor.fetchall()]

    def get_assets_by_sequence(self, sequence_id: str) -> List[Dict[str, Any]]:
        """
        Get all assets generated from a specific prompt.

        Args:
            sequence_id: Sequence ID

        Returns:
            List of asset dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM generated_assets WHERE sequence_id = ?",
                (sequence_id.upper(),)
            )
            return [dict(row) for row in cursor.fetchall()]

    def lookup_by_filename(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Look up a prompt by the filename of a generated asset.

        Args:
            filename: Original or our filename

        Returns:
            Dictionary with prompt and asset info, or None
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT p.*, g.original_filename, g.our_filename, g.file_path, g.asset_type
                FROM prompts p
                JOIN generated_assets g ON p.sequence_id = g.sequence_id
                WHERE g.original_filename = ? OR g.our_filename = ?
                """,
                (filename, filename)
            )
            row = cursor.fetchone()

            return dict(row) if row else None

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics.

        Returns:
            Dictionary with various statistics
        """
        with self._get_connection() as conn:
            stats = {}

            # Current sequence number
            cursor = conn.execute("SELECT current_value FROM sequence_counter WHERE id = 1")
            stats['current_sequence'] = cursor.fetchone()[0]
            stats['current_sequence_id'] = SequenceGenerator.number_to_sequence(stats['current_sequence'])

            # Total prompts
            cursor = conn.execute("SELECT COUNT(*) FROM prompts")
            stats['total_prompts'] = cursor.fetchone()[0]

            # Prompts by type
            cursor = conn.execute("SELECT prompt_type, COUNT(*) as count FROM prompts GROUP BY prompt_type")
            stats['prompts_by_type'] = {row['prompt_type']: row['count'] for row in cursor.fetchall()}

            # Total assets
            cursor = conn.execute("SELECT COUNT(*) FROM generated_assets")
            stats['total_assets'] = cursor.fetchone()[0]

            # Assets by type
            cursor = conn.execute("SELECT asset_type, COUNT(*) as count FROM generated_assets GROUP BY asset_type")
            stats['assets_by_type'] = {row['asset_type']: row['count'] for row in cursor.fetchall()}

            return stats


# Global singleton instance
_tracker_instance = None


def get_tracker(db_path: str = None) -> PromptTracker:
    """
    Get the global PromptTracker instance.

    Args:
        db_path: Database path (only used on first call)

    Returns:
        PromptTracker singleton instance
    """
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = PromptTracker(db_path)
    return _tracker_instance


if __name__ == "__main__":
    # Test the prompt tracker
    print("Prompt Tracker Test\n")

    # Initialize with test database
    tracker = get_tracker("test_prompts.db")

    # Register some test prompts
    print("Registering test prompts...")

    seq1 = tracker.register_prompt(
        prompt_type="suno_lyrics",
        psalm_number=23,
        artist_name="sacred_soundscapes",
        prompt_text="The Lord is my shepherd, I shall not want...",
        metadata={"genre": "ambient worship", "tempo": "slow"}
    )
    print(f"  Registered Suno lyrics prompt: {seq1}")

    seq2 = tracker.register_prompt(
        prompt_type="midjourney",
        psalm_number=23,
        artist_name="sacred_soundscapes",
        prompt_text="Peaceful shepherd in green pastures, golden hour lighting...",
        metadata={"aspect_ratio": "1:1", "style": "photorealistic"}
    )
    print(f"  Registered Midjourney prompt: {seq2}")

    # Retrieve prompt
    print(f"\nRetrieving prompt {seq1}...")
    prompt = tracker.get_prompt(seq1)
    print(f"  Prompt type: {prompt['prompt_type']}")
    print(f"  Psalm: {prompt['psalm_number']}")
    print(f"  Artist: {prompt['artist_name']}")

    # Register an asset
    print(f"\nRegistering asset for {seq2}...")
    asset_id = tracker.register_asset(
        sequence_id=seq2,
        asset_type="midjourney_image",
        original_filename="midjourney_xyz_abc123.png",
        our_filename=f"psalm_023_{seq2}_album_cover.png",
        file_path=f"data/output/sacred_soundscapes/psalm_023/{seq2}_album_cover.png",
        service_metadata={"midjourney_job_id": "abc123"}
    )
    print(f"  Asset registered with ID: {asset_id}")

    # Get statistics
    print("\nDatabase Statistics:")
    stats = tracker.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n✓ Test complete!")
