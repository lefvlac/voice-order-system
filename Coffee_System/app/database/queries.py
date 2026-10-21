import json
from datetime import datetime
from typing import Any

from app.config import DEFAULT_STORE_ID
from app.database.connection import get_db


def find_store_by_vonage_number(vonage_number: str) -> int:
    """
    Επιστρέφει το store_id που αντιστοιχεί
    στον αριθμό Vonage του καταστήματος.
    """

    print("🔎 LOOKUP NUMBER:", repr(vonage_number))

    if not vonage_number:
        print("❌ EMPTY NUMBER - DEFAULT:", DEFAULT_STORE_ID)
        return DEFAULT_STORE_ID

    with get_db() as connection:

        stores = connection.execute("""
            SELECT
                id,
                name,
                vonage_number,
                active
            FROM stores
        """).fetchall()

        print("🏪 STORES IN DB:")

        for store in stores:
            print(dict(store))

        row = connection.execute("""
            SELECT id
            FROM stores
            WHERE vonage_number = ?
            AND active = 1
            LIMIT 1
        """, (vonage_number,)).fetchone()

    if row:
        print("✅ STORE FOUND:", row["id"])
        return int(row["id"])

    print("❌ STORE NOT FOUND - DEFAULT:", DEFAULT_STORE_ID)

    return DEFAULT_STORE_ID


def get_available_menu_items(store_id: int):
    """
    Επιστρέφει όλα τα διαθέσιμα προϊόντα
    του συγκεκριμένου καταστήματος.
    """

    with get_db() as connection:
        rows = connection.execute("""
            SELECT
                name,
                category,
                aliases,
                options,
                extras
            FROM menu_items
            WHERE store_id = ?
            AND available = 1
        """, (store_id,)).fetchall()

    return rows


def save_order(
    store_id: int,
    raw_text: str,
    normalized_text: str,
    items: list[dict[str, Any]],
    order_type: str,
    address: str,
    phone: str,
    retrieved_context: str
) -> None:
    """
    Αποθηκεύει μια νέα παραγγελία στη βάση.
    """

    with get_db() as connection:
        connection.execute("""
            INSERT INTO orders (
                store_id,
                created_at,
                raw_text,
                normalized_text,
                items_json,
                order_type,
                address,
                phone,
                status,
                retrieved_context
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            store_id,
            datetime.now().strftime("%H:%M:%S"),
            raw_text,
            normalized_text,
            json.dumps(items, ensure_ascii=False),
            order_type,
            address,
            phone,
            "PENDING",
            retrieved_context
        ))


def list_orders(
    store_id: int | None = None,
    limit: int = 50
) -> list[dict]:
    """
    Επιστρέφει τις πιο πρόσφατες παραγγελίες.

    Αν δοθεί store_id, επιστρέφονται μόνο
    οι παραγγελίες του συγκεκριμένου καταστήματος.
    """

    with get_db() as connection:

        if store_id is None:
            rows = connection.execute("""
                SELECT *
                FROM orders
                ORDER BY id DESC
                LIMIT ?
            """, (
                limit,
            )).fetchall()

        else:
            rows = connection.execute("""
                SELECT *
                FROM orders
                WHERE store_id = ?
                ORDER BY id DESC
                LIMIT ?
            """, (
                store_id,
                limit
            )).fetchall()

    return [
        dict(row)
        for row in rows
    ]


def mark_order_ready(order_id: int) -> bool:
    """
    Αλλάζει την κατάσταση μιας παραγγελίας σε READY.
    Επιστρέφει True αν βρέθηκε και ενημερώθηκε
    η παραγγελία.
    """

    with get_db() as connection:
        cursor = connection.execute("""
            UPDATE orders
            SET status = 'READY'
            WHERE id = ?
        """, (order_id,))

        return cursor.rowcount > 0
def delete_order(order_id: int) -> bool:
    """
    Διαγράφει μια παραγγελία.

    Επιστρέφει True αν βρέθηκε και
    διαγράφηκε η παραγγελία.
    """

    with get_db() as connection:
        cursor = connection.execute("""
            DELETE FROM orders
            WHERE id = ?
        """, (order_id,))

        return cursor.rowcount > 0

def update_order(
    order_id: int,
    items: list[dict[str, Any]],
    order_type: str,
    address: str,
    phone: str
) -> bool:
    """
    Ενημερώνει τα βασικά στοιχεία
    μιας υπάρχουσας παραγγελίας.

    Επιστρέφει True αν βρέθηκε
    και ενημερώθηκε η παραγγελία.
    """

    items_json = json.dumps(
        items,
        ensure_ascii=False
    )

    with get_db() as connection:
        cursor = connection.execute("""
            UPDATE orders
            SET
                items_json = ?,
                order_type = ?,
                address = ?,
                phone = ?
            WHERE id = ?
        """, (
            items_json,
            order_type,
            address,
            phone,
            order_id
        ))

        return cursor.rowcount > 0

def add_menu_item(
    store_id: int,
    name: str,
    category: str = "",
    aliases: str = "",
    options: str = "",
    extras: str = "",
    available: bool = True
) -> int:
    """
    Προσθέτει νέο προϊόν στο μενού καταστήματος.

    Επιστρέφει το id του νέου προϊόντος.
    """

    with get_db() as connection:
        cursor = connection.execute("""
            INSERT INTO menu_items (
                store_id,
                name,
                category,
                aliases,
                options,
                extras,
                available
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            store_id,
            name,
            category,
            aliases,
            options,
            extras,
            int(available)
        ))

        return int(cursor.lastrowid)

def get_store_menu(store_id: int) -> list[dict]:
    """
    Επιστρέφει ολόκληρο το μενού
    ενός καταστήματος.
    """

    with get_db() as connection:
        rows = connection.execute("""
            SELECT *
            FROM menu_items
            WHERE store_id = ?
            ORDER BY category, name
        """, (store_id,)).fetchall()

    return [dict(row) for row in rows]