from pathlib import Path

import requests
from openai import OpenAI

from app.config import (
    OPENAI_API_KEY,
    RECORDINGS_DIR,
    VONAGE_API_KEY,
    VONAGE_API_SECRET
)
from app.database.queries import (
    find_store_by_vonage_number,
    get_available_menu_items,
    save_order
)
from app.services.gpt_service import parse_order
from app.utils.text import normalize_transcript


def build_whisper_prompt(store_id: int) -> str:
    """
    Δημιουργεί δυναμικό prompt για το Whisper
    με βάση το διαθέσιμο μενού του καταστήματος.

    Περιλαμβάνει:
    - ονομασίες προϊόντων,
    - aliases,
    - διαθέσιμες επιλογές,
    - extras,
    - γενικούς όρους παραγγελίας.
    """

    menu_items = get_available_menu_items(
        store_id
    )

    terms = []

    for item in menu_items:

        # Επίσημη ονομασία προϊόντος
        if item["name"]:
            terms.append(
                item["name"]
            )

        # Aliases προϊόντος
        aliases = item["aliases"] or ""

        for alias in aliases.split(","):
            alias = alias.strip()

            if alias:
                terms.append(
                    alias
                )

        # Επιλογές προϊόντος
        options = item["options"] or ""

        for option in options.split(","):
            option = option.strip()

            if option:
                terms.append(
                    option
                )

        # Extras προϊόντος
        extras = item["extras"] or ""

        for extra in extras.split(","):
            extra = extra.strip()

            if extra:
                terms.append(
                    extra
                )

    # Γενικές λέξεις που χρησιμοποιούνται
    # στις τηλεφωνικές παραγγελίες.
    terms.extend([
        "delivery",
        "take away",
        "takeaway",
        "για το σπίτι",
        "παράδοση",
        "διεύθυνση"
    ])

    # Αφαίρεση διπλοεγγραφών,
    # διατηρώντας τη σειρά.
    unique_terms = list(
        dict.fromkeys(terms)
    )

    return ", ".join(
        unique_terms
    )


async def handle_call(
    recording_url: str,
    customer_phone: str = "Unknown",
    called_number: str = ""
) -> None:
    """
    Επεξεργάζεται την ηχογράφηση μιας τηλεφωνικής κλήσης.

    Η διαδικασία περιλαμβάνει:
    1. Εντοπισμό του καταστήματος.
    2. Δημιουργία δυναμικού Whisper prompt
       από το μενού του καταστήματος.
    3. Λήψη της ηχογράφησης από τη Vonage.
    4. Μετατροπή ομιλίας σε κείμενο μέσω Whisper.
    5. Κανονικοποίηση του κειμένου.
    6. Ανάλυση της παραγγελίας μέσω GPT και RAG.
    7. Αποθήκευση της παραγγελίας στη βάση.
    """

    store_id = find_store_by_vonage_number(
        called_number
    )

    whisper_prompt = build_whisper_prompt(
        store_id
    )

    RECORDINGS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    recording_path: Path = (
        RECORDINGS_DIR / "temp_order.wav"
    )

    try:
        response = requests.get(
            recording_url,
            params={
                "api_key": VONAGE_API_KEY,
                "api_secret": VONAGE_API_SECRET
            },
            timeout=30
        )

        if response.status_code != 200:
            print(
                "Αποτυχία λήψης ηχογράφησης. "
                f"Status code: {response.status_code}"
            )
            return

        recording_path.write_bytes(
            response.content
        )

        if not OPENAI_API_KEY:
            raise RuntimeError(
                "Δεν έχει οριστεί OPENAI_API_KEY "
                "στο αρχείο .env"
            )

        client = OpenAI(
            api_key=OPENAI_API_KEY
        )

        with recording_path.open("rb") as audio_file:
            transcript = (
                client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="el",
                    prompt=whisper_prompt
                )
            )

        raw_text = transcript.text

        normalized_text = normalize_transcript(
            raw_text
        )

        parsed_result = parse_order(
            text=normalized_text,
            store_id=store_id
        )

        order_data = parsed_result[
            "order_data"
        ]

        retrieved_context = parsed_result[
            "retrieved_context"
        ]

        items = order_data.get(
            "items",
            []
        )

        print(
            "📝 RAW TEXT:",
            raw_text
        )

        print(
            "🧹 NORMALIZED TEXT:",
            normalized_text
        )

        print(
            "🤖 ORDER DATA:",
            order_data
        )

        print(
            "📍 ADDRESS:",
            order_data.get("address")
        )

        print(
            "🚚 ORDER TYPE:",
            order_data.get("order_type")
        )

        if (
            order_data.get("status") == "REJECTED"
            or not items
        ):
            print(
                "Η παραγγελία απορρίφθηκε "
                "και δεν αποθηκεύτηκε."
            )
            return

        save_order(
            store_id=store_id,
            raw_text=raw_text,
            normalized_text=normalized_text,
            items=items,
            order_type=order_data.get(
                "order_type",
                "TAKE AWAY"
            ),
            address=order_data.get(
                "address",
                ""
            ),
            phone=customer_phone,
            retrieved_context=retrieved_context
        )

        print(
            "Η παραγγελία καταχωρήθηκε επιτυχώς "
            f"για το κατάστημα {store_id}."
        )

    except requests.RequestException as error:
        print(
            "Παρουσιάστηκε σφάλμα κατά τη λήψη "
            f"της ηχογράφησης: {error}"
        )

    except Exception as error:
        print(
            "Παρουσιάστηκε κρίσιμο σφάλμα "
            f"στη handle_call(): {error}"
        )

    finally:
        if recording_path.exists():
            recording_path.unlink()