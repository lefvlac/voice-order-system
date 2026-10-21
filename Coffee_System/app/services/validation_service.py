from app.utils.text import normalize_text


def normalize_list(value) -> list[str]:
    """
    Μετατρέπει options/extras σε λίστα συμβολοσειρών.

    Υποστηρίζει τόσο λίστες όσο και απλές
    συμβολοσειρές για μεγαλύτερη ανθεκτικότητα.
    """

    if isinstance(value, list):
        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    if isinstance(value, str):
        value = value.strip()

        if not value:
            return []

        return [value]

    return []


def validate_order_items(
    order_data: dict,
    retrieved_context: str,
    transcript: str
) -> dict:
    """
    Ελέγχει ότι:
    1. Το προϊόν υπάρχει στο retrieved menu.
    2. Αναγνωρίζεται είτε από την επίσημη ονομασία
       είτε από κάποιο alias.
    3. Το προϊόν ή κάποιο alias του εμφανίζεται
       πραγματικά στο κείμενο της παραγγελίας.

    Τα options και extras διατηρούνται
    σε γενική μορφή λίστας ώστε η εφαρμογή
    να υποστηρίζει διαφορετικούς τύπους καταστημάτων.
    """

    normalized_transcript = normalize_text(
        transcript
    )

    valid_products = {}

    for line in retrieved_context.splitlines():

        if not line.startswith("- Προϊόν:"):
            continue

        parts = line.split("|")

        product_name = (
            parts[0]
            .replace("- Προϊόν:", "")
            .strip()
        )

        aliases = []

        for part in parts:
            part = part.strip()

            if part.startswith("Aliases:"):
                aliases_text = (
                    part
                    .replace("Aliases:", "")
                    .strip()
                )

                aliases = [
                    alias.strip()
                    for alias in aliases_text.split(",")
                    if alias.strip()
                ]

        product_info = {
            "name": product_name,
            "aliases": aliases
        }

        valid_products[
            normalize_text(product_name)
        ] = product_info

        for alias in aliases:
            valid_products[
                normalize_text(alias)
            ] = product_info

    validated_items = []

    for item in order_data.get("items", []):

        product = item.get(
            "product",
            ""
        ).strip()

        normalized_product = normalize_text(
            product
        )

        if normalized_product not in valid_products:
            continue

        product_info = valid_products[
            normalized_product
        ]

        product_name = product_info["name"]
        aliases = product_info["aliases"]

        possible_matches = [
            product_name,
            *aliases
        ]

        product_was_mentioned = any(
            normalize_text(match)
            in normalized_transcript
            for match in possible_matches
            if match
        )

        if not product_was_mentioned:
            print(
                "⛔ Validation rejected product:",
                product_name
            )
            continue

        item["product"] = product_name

        quantity = item.get(
            "qty",
            1
        )

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            quantity = 1

        item["qty"] = max(
            quantity,
            1
        )

        item["options"] = normalize_list(
            item.get(
                "options",
                []
            )
        )

        item["extras"] = normalize_list(
            item.get(
                "extras",
                []
            )
        )

        validated_items.append(
            item
        )

    order_data["items"] = validated_items

    if not validated_items:

        order_data["items"] = [
            {
                "product": (
                    "ΑΠΟΡΡΙΦΘΗΚΕ: "
                    "Δεν βρέθηκε έγκυρο προϊόν "
                    "στην παραγγελία"
                ),
                "qty": 0,
                "options": [],
                "extras": []
            }
        ]

        order_data["status"] = "REJECTED"

    return order_data