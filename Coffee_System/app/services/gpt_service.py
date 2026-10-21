import json
import re

from openai import OpenAI

from app.config import OPENAI_API_KEY
from app.services.rag_service import get_menu_context
from app.services.validation_service import validate_order_items


def parse_order(
    text: str,
    store_id: int = 1
) -> dict:
    """
    Μετατρέπει το κείμενο της παραγγελίας
    σε δομημένα δεδομένα JSON.

    Η συνάρτηση:
    1. Ανακτά σχετικό menu context μέσω RAG.
    2. Στέλνει το κείμενο και το context στο LLM.
    3. Μετατρέπει την απάντηση σε Python dictionary.
    4. Ελέγχει τα προϊόντα μέσω του Validation Layer.
    """

    if not OPENAI_API_KEY:
        raise RuntimeError(
            "Δεν έχει οριστεί OPENAI_API_KEY στο αρχείο .env"
        )

    client = OpenAI(
        api_key=OPENAI_API_KEY
    )

    menu_context = get_menu_context(
        store_id=store_id,
        transcript=text
    )
    print("🔎 RAG CONTEXT:")
    print(menu_context)

    system_prompt = f"""
Είσαι το υποσύστημα κατανόησης παραγγελιών
ενός πληροφοριακού συστήματος εστίασης.

Λαμβάνεις κείμενο που προέρχεται από
απομαγνητοφώνηση τηλεφωνικής παραγγελίας.

ΑΝΑΚΤΗΜΕΝΟ ΜΕΝΟΥ ΚΑΤΑΣΤΗΜΑΤΟΣ:

{menu_context}

ΟΔΗΓΙΕΣ:

1. Αναγνώρισε μόνο προϊόντα που ο πελάτης ζητά ξεκάθαρα
   και τα οποία αντιστοιχούν σε όνομα ή alias
   του ανακτημένου μενού.

2. ΜΗΝ αντικαθιστάς ένα άγνωστο προϊόν με το πλησιέστερο
   διαθέσιμο προϊόν του μενού.

3. Αν αυτό που ζητά ο πελάτης δεν αντιστοιχεί πραγματικά
   σε κανένα όνομα ή alias του ανακτημένου μενού,
   ΜΗΝ επιλέξεις κάποιο παρόμοιο προϊόν.

4. Σε περίπτωση που κανένα προϊόν δεν μπορεί να αναγνωριστεί
   με βεβαιότητα, επέστρεψε:

   "items": []

5. Χρησιμοποίησε ακριβώς την ονομασία του προϊόντος
   όπως εμφανίζεται στο ανακτημένο μενού.

6. Αν δεν αναφέρεται ποσότητα,
   χρησιμοποίησε qty ίσο με 1.

7. Στο πεδίο options καταγράφονται βασικές επιλογές
   που χαρακτηρίζουν το προϊόν, όπως:
   - επιλογή ζάχαρης,
   - μέγεθος,
   - τύπος ή άλλη διαθέσιμη επιλογή
     που εμφανίζεται στο ανακτημένο μενού.

8. Στο πεδίο extras καταγράφονται πρόσθετα υλικά
   ή τροποποιήσεις, όπως:
   - κανέλα,
   - σοκολάτα,
   - λίγο πάγο,
   - χωρίς πάγο,
   - έξτρα τυρί,
   - χωρίς μαγιονέζα,
   εφόσον εμφανίζονται ως διαθέσιμα extras
   στο ανακτημένο μενού.

9. Τα options και extras πρέπει πάντα
   να επιστρέφονται ως λίστες.

10. Αν δεν υπάρχει option ή extra,
    επέστρεψε κενή λίστα [].

11. Μην αγνοείς option ή extra που αναφέρεται
    ξεκάθαρα από τον πελάτη και υπάρχει
    στο ανακτημένο μενού.

12. Αν μια πληροφορία εμφανίζεται στο ανακτημένο μενού
    ως επιλογή, βάλε την στο options.
    Αν εμφανίζεται ως extra, βάλε την στο extras.

13. Αν αναφέρεται διεύθυνση,
    το order_type πρέπει να είναι DELIVERY.

14. Αν δεν αναφέρεται διεύθυνση,
    το order_type πρέπει να είναι TAKE AWAY.

15. Μην επινοείς προϊόντα, options ή extras
    και μην κάνεις αυθαίρετες σημασιολογικές αντικαταστάσεις.

16. Επέστρεψε αποκλειστικά έγκυρο JSON,
    χωρίς επεξηγήσεις ή Markdown.

ΠΑΡΑΔΕΙΓΜΑ 1:

Παραγγελία:
"Ένα καπουτσίνο μέτριο με κανέλα"

Αποτέλεσμα:
{{
    "items": [
        {{
            "product": "Καπουτσίνο",
            "qty": 1,
            "options": ["Μέτριο"],
            "extras": ["Κανέλα"]
        }}
    ],
    "order_type": "TAKE AWAY",
    "address": ""
}}

ΠΑΡΑΔΕΙΓΜΑ 2:

Παραγγελία:
"Έναν φρέντο εσπρέσο γλυκό με λίγο πάγο"

Αποτέλεσμα:
{{
    "items": [
        {{
            "product": "Φρέντο Εσπρέσο",
            "qty": 1,
            "options": ["Γλυκό"],
            "extras": ["Λίγο πάγο"]
        }}
    ],
    "order_type": "TAKE AWAY",
    "address": ""
}}

ΠΑΡΑΔΕΙΓΜΑ 3:

Παραγγελία:
"Μία μεγάλη πίτσα μαργαρίτα με έξτρα τυρί"

Αποτέλεσμα:
{{
    "items": [
        {{
            "product": "Πίτσα Μαργαρίτα",
            "qty": 1,
            "options": ["Μεγάλη"],
            "extras": ["Έξτρα τυρί"]
        }}
    ],
    "order_type": "TAKE AWAY",
    "address": ""
}}

Η μορφή της απάντησης πρέπει να είναι:

{{
    "items": [
        {{
            "product": "Όνομα προϊόντος",
            "qty": 1,
            "options": [],
            "extras": []
        }}
    ],
    "order_type": "TAKE AWAY",
    "address": ""
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": (
                        "Μετέτρεψε την παρακάτω "
                        "παραγγελία σε JSON:\n\n"
                        f"{text}"
                    )
                }
            ],
            temperature=0
        )

        response_content = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        if response_content.startswith("```"):
            response_content = re.sub(
                r"```json|```",
                "",
                response_content
            ).strip()

        order_data = json.loads(
            response_content
        )

        validated_order = validate_order_items(
            order_data=order_data,
            retrieved_context=menu_context,
            transcript=text
        )

        return {
            "order_data": validated_order,
            "retrieved_context": menu_context
        }

    except json.JSONDecodeError as error:
        return {
            "order_data": {
                "items": [],
                "order_type": "TAKE AWAY",
                "address": "",
                "status": "REJECTED",
                "error": (
                    "Η απάντηση του μοντέλου "
                    "δεν ήταν έγκυρο JSON: "
                    f"{error}"
                )
            },
            "retrieved_context": menu_context
        }

    except Exception as error:
        return {
            "order_data": {
                "items": [],
                "order_type": "TAKE AWAY",
                "address": "",
                "status": "REJECTED",
                "error": str(error)
            },
            "retrieved_context": menu_context
        }