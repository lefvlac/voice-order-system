import sqlite3
from contextlib import contextmanager
from typing import Iterator

from app.config import DB_PATH


@contextmanager
def get_db() -> Iterator[sqlite3.Connection]:
    """
    Δημιουργεί σύνδεση με τη βάση SQLite
    και τη διαχειρίζεται με ασφάλεια.
    """

    connection = sqlite3.connect(
        DB_PATH,
        timeout=10
    )

    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()