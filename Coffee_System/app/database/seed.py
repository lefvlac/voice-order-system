from app.database.connection import get_db


def seed_demo_data() -> None:
    """
    Εισάγει δοκιμαστικά καταστήματα και προϊόντα,
    χωρίς να δημιουργεί διπλοεγγραφές.
    """

    coffee_items = [
    (
        "Φρέντο Εσπρέσο",
        "Καφές",
        "φρέντο, φρέντο εσπρέσο, freddo espresso",
        "Σκέτο, Μέτριο, Γλυκό, Με ολίγη, Με μαύρη",
        "Λίγο πάγο, Χωρίς πάγο, Μονό, Διπλό"
    ),
    (
        "Καπουτσίνο",
        "Καφές",
        "καπουτσίνο, cappuccino",
        "Σκέτο, Μέτριο, Γλυκό, Με ολίγη, Με μαύρη",
        "Κανέλα, Σοκολάτα, Μονό, Διπλό"
    ),
    (
        "Ελληνικός",
        "Καφές",
        "ελληνικός, ελληνικο",
        "Σκέτο, Μέτριο, Γλυκό, Με ολίγη",
        "Μονό, Διπλό"
    ),
    (
        "Φραπές",
        "Καφές",
        "φραπές, frappe",
        "Σκέτο, Μέτριο, Γλυκό, Με ολίγη, Με μαύρη",
        "Λίγο πάγο, Χωρίς πάγο"
    ),
    (
        "Σοκολάτα ζεστή",
        "Ρόφημα",
        "σοκολάτα ζεστή, ζεστή σοκολάτα",
        "",
        "Κανέλα"
    ),
    (
        "Τοστ",
        "Snack",
        "τοστ, tost",
        "",
        "Τυρί, Ζαμπόν-Τυρί"
    ),
    (
        "Τυρόπιτα",
        "Snack",
        "τυρόπιτα, τυροπιτα",
        "",
        ""
    )
]

    pizza_items = [
        (
            "Πίτσα Μαργαρίτα",
            "Pizza",
            "πίτσα μαργαρίτα, μαργαρίτα",
            "Κανονική, Μεγάλη",
            "Έξτρα τυρί, Χωρίς κρεμμύδι"
        ),
        (
            "Πίτσα Πεπερόνι",
            "Pizza",
            "πίτσα πεπερόνι, πεπερόνι",
            "Κανονική, Μεγάλη",
            "Έξτρα τυρί"
        ),
        (
            "Club Sandwich",
            "Snack",
            "club, club sandwich, κλαμπ",
            "",
            "Πατάτες, Χωρίς μαγιονέζα"
        )
    ]

    with get_db() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT OR IGNORE INTO stores (
                id,
                name,
                vonage_number,
                active
            )
            VALUES (?, ?, ?, ?)
        """, (
            1,
            "Demo Coffee Store",
            "302621200665",
            1
        ))

        cursor.execute("""
            INSERT OR IGNORE INTO stores (
                id,
                name,
                vonage_number,
                active
            )
            VALUES (?, ?, ?, ?)
        """, (
            2,
            "Demo Pizza Store",
            "302313082005",
            1
        ))
         # Ενημέρωση των αριθμών Vonage
        # σε περίπτωση που τα stores υπάρχουν ήδη.
        cursor.execute("""
            UPDATE stores
            SET vonage_number = ?
            WHERE id = ?
        """, (
            "302621200665",
            1
        ))

        cursor.execute("""
            UPDATE stores
            SET vonage_number = ?
            WHERE id = ?
        """, (
            "302313082005",
            2
        ))
        cursor.execute("""
            UPDATE menu_items
            SET
                aliases = ?,
                options = ?,
                extras = ?
            WHERE store_id = ?
            AND name = ?
        """, (
            "καπουτσίνο, cappuccino",
            "Σκέτο, Μέτριο, Γλυκό, Με ολίγη, Με μαύρη",
            "Κανέλα, Σοκολάτα, Μονό, Διπλό",
            1,
            "Καπουτσίνο"
        ))
        cursor.execute("""
            UPDATE menu_items
            SET
                aliases = ?,
                extras = ?
            WHERE store_id = ?
            AND name = ?
        """, (
            "σοκολάτα ζεστή, ζεστή σοκολάτα",
            "Κανέλα",
            1,
            "Σοκολάτα ζεστή"
        ))
        
            
        

        for item in coffee_items:
            cursor.execute("""
                INSERT INTO menu_items (
                    store_id,
                    name,
                    category,
                    aliases,
                    options,
                    extras,
                    available
                )
                SELECT ?, ?, ?, ?, ?, ?, 1
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM menu_items
                    WHERE store_id = ?
                    AND name = ?
                )
            """, (
                1,
                item[0],
                item[1],
                item[2],
                item[3],
                item[4],
                1,
                item[0]
            ))

        for item in pizza_items:
            cursor.execute("""
                INSERT INTO menu_items (
                    store_id,
                    name,
                    category,
                    aliases,
                    options,
                    extras,
                    available
                )
                SELECT ?, ?, ?, ?, ?, ?, 1
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM menu_items
                    WHERE store_id = ?
                    AND name = ?
                )
            """, (
                2,
                item[0],
                item[1],
                item[2],
                item[3],
                item[4],
                2,
                item[0]
            ))

    print("Τα δοκιμαστικά δεδομένα εισήχθησαν επιτυχώς.")