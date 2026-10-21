import unicodedata
from difflib import SequenceMatcher


def similarity(first_text: str, second_text: str) -> float:
    """
    Υπολογίζει τον βαθμό ομοιότητας δύο συμβολοσειρών.

    Η επιστρεφόμενη τιμή κυμαίνεται από 0 έως 1.
    Όσο πλησιάζει το 1, τόσο περισσότερο μοιάζουν τα κείμενα.
    """

    return SequenceMatcher(
        None,
        first_text.lower(),
        second_text.lower()
    ).ratio()


def remove_accents(text: str) -> str:
    """
    Αφαιρεί τους τόνους από ελληνικούς χαρακτήρες.

    Παράδειγμα:
    'μέτριο' -> 'μετριο'
    """

    return "".join(
        character
        for character in unicodedata.normalize("NFD", text)
        if unicodedata.category(character) != "Mn"
    )


def normalize_text(value: str) -> str:
    """
    Κανονικοποιεί κείμενο για συγκρίσεις.

    Μετατρέπει σε πεζά, αφαιρεί τόνους
    και περιττά κενά από την αρχή και το τέλος.
    """

    return remove_accents(
        (value or "").strip().lower()
    )

def normalize_option(value: str) -> str:
    """
    Κανονικοποιεί επιλογές ζάχαρης και επιστρέφει
    μια ενιαία μορφή για αποθήκευση στη βάση.
    """

    normalized_value = normalize_text(
        remove_accents(value or "")
    )

    sugar_map = {
        "μετριο": "Μέτριο",
        "μετριως": "Μέτριο",
        "medium": "Μέτριο",

        "σκετο": "Σκέτο",
        "χωρις ζαχαρη": "Σκέτο",
        "no sugar": "Σκέτο",

        "γλυκο": "Γλυκό",
        "γλυκα": "Γλυκό",
        "sweet": "Γλυκό",

        "με ολιγη": "Με ολίγη",
        "ολιγη": "Με ολίγη",

        "με μαυρη": "Με μαύρη",
        "μαυρη": "Με μαύρη"
    }

    return sugar_map.get(
        normalized_value,
        value or ""
    )


def normalize_transcript(text: str) -> str:
    """
    Κανονικοποιεί το κείμενο που επιστρέφει το Whisper.

    Διορθώνει συνηθισμένα λάθη αναγνώρισης,
    αγγλικές μεταγραφές και λέξεις χωρίς τόνους.
    """

    if not text:
        return ""

    normalized_text = remove_accents(
        text.lower().strip()
    )

    replacements = {
        "φρεντο εσπρεσο": "φρέντο εσπρέσο",
        "φρεντο καπουτσινο": "φρέντο καπουτσίνο",
        "φρεντο": "φρέντο",
        "εσπρεσο": "εσπρέσο",
        "καπουτσινο": "καπουτσίνο",
        "φραπε": "φραπές",
        "ελληνικο": "ελληνικός",
        "τυροπιτα": "τυρόπιτα",
        "μπουγατσα": "μπουγάτσα",
        "ζαμπον": "ζαμπόν",
        "μετριο": "μέτριο",
        "σκετο": "σκέτο",
        "γλυκο": "γλυκό",
        "ολιγη": "ολίγη",

        "fredu cappucino": "φρέντο καπουτσίνο",
        "freddo cappuccino": "φρέντο καπουτσίνο",
        "freddo cappucino": "φρέντο καπουτσίνο",
        "fredu cappuccino": "φρέντο καπουτσίνο",
        "frento cappuccino": "φρέντο καπουτσίνο",
        "frento cappucino": "φρέντο καπουτσίνο",

        "fredu espresso": "φρέντο εσπρέσο",
        "freddo espresso": "φρέντο εσπρέσο",
        "frento espresso": "φρέντο εσπρέσο"
    }

    for wrong_text, correct_text in replacements.items():
        normalized_text = normalized_text.replace(
            wrong_text,
            correct_text
        )

    return normalized_text