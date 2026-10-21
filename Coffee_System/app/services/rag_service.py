from app.database.queries import get_available_menu_items
from app.utils.text import similarity


def get_menu_context(
    store_id: int,
    transcript: str
) -> str:
    """
    Ανακτά από τη βάση τα προϊόντα του καταστήματος
    που σχετίζονται περισσότερο με το κείμενο της παραγγελίας.

    Το αποτέλεσμα επιστρέφεται σε μορφή κειμένου,
    ώστε να χρησιμοποιηθεί ως context στο LLM.
    """

    menu_items = get_available_menu_items(store_id)

    transcript_lower = transcript.lower()

    scored_items = []

    for item in menu_items:
        searchable_text = " ".join([
            item["name"] or "",
            item["aliases"] or "",
            item["category"] or ""
        ]).lower()

        similarity_score = similarity(
            transcript_lower,
            searchable_text
        )

        keyword_bonus = 0.0

        searchable_parts = searchable_text.split(",")

        for part in searchable_parts:
            keyword = part.strip()

            if keyword and keyword in transcript_lower:
                keyword_bonus += 0.25

        final_score = similarity_score + keyword_bonus

        scored_items.append(
            (
                final_score,
                item
            )
        )

    scored_items.sort(
        key=lambda result: result[0],
        reverse=True
    )

    top_items = scored_items[:6]

    context_lines = []

    for score, item in top_items:
        context_line = (
            f"- Προϊόν: {item['name']}"
        )

        if item["category"]:
            context_line += (
                f" | Κατηγορία: {item['category']}"
            )

        if item["aliases"]:
            context_line += (
                f" | Aliases: {item['aliases']}"
            )

        if item["options"]:
            context_line += (
                f" | Επιλογές: {item['options']}"
            )

        if item["extras"]:
            context_line += (
                f" | Extras: {item['extras']}"
            )

        context_lines.append(context_line)

    retrieved_context = "\n".join(context_lines)

    return retrieved_context