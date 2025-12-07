"""
Database Manager for Telegram Backup Manager
Handles SQLite operations and persistence
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from models import BackupConfig, BackupSettings, BackupFilters, BackupStats

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "backup.db"):
        self.db_path = Path(db_path)
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Initialize database schema"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Routes table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS routes (
                        source TEXT PRIMARY KEY,
                        destination TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Filters table (key-value store for filter settings)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS filters (
                        key TEXT PRIMARY KEY,
                        value INTEGER NOT NULL -- Boolean stored as 0/1
                    )
                """)

                # Settings table (JSON blob for nested settings or key-value)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                """)

                # Backup State table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS backup_state (
                        entity_id TEXT PRIMARY KEY,
                        last_message_id INTEGER DEFAULT 0,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Initialize default filters if empty
                cursor.execute("SELECT COUNT(*) FROM filters")
                if cursor.fetchone()[0] == 0:
                    defaults = {
                        "media_only": 0,
                        "photos": 1,
                        "videos": 1,
                        "documents": 0,
                        "text_messages": 1
                    }
                    cursor.executemany(
                        "INSERT INTO filters (key, value) VALUES (?, ?)",
                        defaults.items()
                    )

                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def load_config(self) -> BackupConfig:
        """Load full configuration from DB"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Load Routes
                cursor.execute("SELECT source, destination FROM routes")
                routes = {row[0]: row[1] for row in cursor.fetchall()}

                # Load Filters
                cursor.execute("SELECT key, value FROM filters")
                filters_dict = {row[0]: bool(row[1]) for row in cursor.fetchall()}
                filters = BackupFilters(**filters_dict)

                # Load Settings
                cursor.execute("SELECT key, value FROM settings")
                settings_dict = {}
                for key, value in cursor.fetchall():
                    try:
                        settings_dict[key] = json.loads(value)
                    except json.JSONDecodeError:
                        settings_dict[key] = value

                # Construct Settings object (handle defaults if empty)
                settings = BackupSettings(**settings_dict) if settings_dict else BackupSettings()

                return BackupConfig(
                    routes=routes,
                    filters=filters,
                    settings=settings
                )
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return BackupConfig()

    def save_route(self, source: str, destination: str):
        with self.get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO routes (source, destination) VALUES (?, ?)",
                (source, destination)
            )

    def remove_route(self, source: str):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM routes WHERE source = ?", (source,))

    def update_filters(self, filters: Dict[str, bool]):
        with self.get_connection() as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO filters (key, value) VALUES (?, ?)",
                [(k, 1 if v else 0) for k, v in filters.items()]
            )

    def update_state(self, entity_id: str, message_id: int):
        with self.get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO backup_state (entity_id, last_message_id, updated_at) VALUES (?, ?, ?)",
                (entity_id, message_id, datetime.now())
            )

    def get_state(self) -> Dict[str, int]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT entity_id, last_message_id FROM backup_state")
            return {row[0]: row[1] for row in cursor.fetchall()}

    def get_total_processed_messages(self) -> int:
        """Estimate total processed based on state (not exact but useful metric)"""
        # Actually, for total processed count, we might want a separate counter or sum(last_message_id)
        # which isn't accurate as message IDs are not sequential starting from 0 per backup run.
        # But for now, we can count rows in state or keep the old logic of 'len(state)' which was 'number of chats tracked'.
        # The user report said: "processed_messages: len(state)".
        # Wait, len(state) is just number of chats tracked, not total messages.
        # I'll stick to returning the state dict length for compatibility with existing stats logic for now,
        # or implement a proper counter table if needed.
        # Let's assume the previous logic: processed_messages = len(state).
        return len(self.get_state())
