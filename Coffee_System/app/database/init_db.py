import sqlite3

from app.database.connection import get_db


def init_db() -> None:
    """
    Δημιουργεί τους βασικούς πίνακες της εφαρμογής
    και προσθέτει τυχόν στήλες που λείπουν από παλιότερη βάση.
    """

    with get_db() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store_id INTEGER DEFAULT 1,
                created_at TEXT,
                raw_text TEXT,
                normalized_text TEXT,
                items_json TEXT,
                order_type TEXT,
                address TEXT,
                phone TEXT,
                status TEXT DEFAULT 'PENDING',
                retrieved_context TEXT
            )
        """)

        migration_statements = [
            "ALTER TABLE orders ADD COLUMN store_id INTEGER DEFAULT 1",
            "ALTER TABLE orders ADD COLUMN retrieved_context TEXT",
            "ALTER TABLE orders ADD COLUMN normalized_text TEXT"
        ]

        for statement in migration_statements:
            try:
                cursor.execute(statement)

            except sqlite3.OperationalError:
                pass

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                vonage_number TEXT UNIQUE,
                active INTEGER DEFAULT 1
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                category TEXT,
                aliases TEXT,
                options TEXT,
                extras TEXT,
                available INTEGER DEFAULT 1,
                FOREIGN KEY (store_id) REFERENCES stores(id)
            )
        """)

    print("Η βάση δεδομένων αρχικοποιήθηκε επιτυχώς.")