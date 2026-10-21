import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


DB_PATH = os.getenv(
    "DB_PATH",
    str(BASE_DIR / "orders.db")
)

RECORDINGS_DIR = BASE_DIR / "recordings"


OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY",
    ""
)

VONAGE_API_KEY = os.getenv(
    "VONAGE_API_KEY",
    ""
)

VONAGE_API_SECRET = os.getenv(
    "VONAGE_API_SECRET",
    ""
)

VONAGE_APP_ID = os.getenv(
    "VONAGE_APP_ID",
    ""
)

VONAGE_PRIVATE_KEY_PATH = os.getenv(
    "VONAGE_PRIVATE_KEY_PATH",
    str(BASE_DIR / "private.key")
)

VONAGE_EVENT_URL = os.getenv(
    "VONAGE_EVENT_URL",
    "https://example.ngrok-free.app/vonage-event"
)

DEFAULT_STORE_ID = int(
    os.getenv("DEFAULT_STORE_ID", "1")
)