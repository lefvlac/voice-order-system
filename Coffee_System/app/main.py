from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.admin import router as admin_router
from app.api.dashboard import router as dashboard_router
from app.api.vonage import router as vonage_router
from app.database.init_db import init_db
from app.database.seed import seed_demo_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Εκτελεί τις απαραίτητες ενέργειες
    κατά την εκκίνηση και τον τερματισμό
    της εφαρμογής.
    """

    init_db()
    seed_demo_data()

    print("Η βάση δεδομένων αρχικοποιήθηκε.")
    print("Το Voice Order System είναι έτοιμο.")

    yield

    print("Το Voice Order System τερματίστηκε.")


app = FastAPI(
    title="Voice Order System",
    description=(
        "Πληροφοριακό σύστημα αυτοματοποιημένης "
        "λήψης και επεξεργασίας τηλεφωνικών "
        "παραγγελιών με χρήση Speech-to-Text, "
        "LLM, RAG και Validation Layer."
    ),
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=False,
    allow_methods=[
        "*"
    ],
    allow_headers=[
        "*"
    ]
)


app.include_router(
    dashboard_router
)

app.include_router(
    vonage_router
)

app.include_router(
    admin_router
)