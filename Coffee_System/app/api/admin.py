from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.database.queries import (
    add_menu_item,
    delete_order,
    get_store_menu,
    list_orders,
    mark_order_ready,
    update_order
)


router = APIRouter(
    prefix="/api",
    tags=["Admin"]
)


class OrderUpdateRequest(BaseModel):
    """
    Δεδομένα που επιτρέπεται να αλλάξουν
    σε μια υπάρχουσα παραγγελία.
    """

    items: list[dict[str, Any]]
    order_type: str = "TAKE AWAY"
    address: str = ""
    phone: str = ""


class MenuItemCreateRequest(BaseModel):
    """
    Δεδομένα νέου προϊόντος μενού.
    """

    store_id: int = Field(
        ...,
        gt=0
    )

    name: str = Field(
        ...,
        min_length=1
    )

    category: str = ""
    aliases: str = ""
    options: str = ""
    extras: str = ""
    available: bool = True


@router.get("/orders")
def get_orders(
    store_id: int | None = None
):
    """
    Επιστρέφει τις παραγγελίες για το Staff Dashboard.

    Αν δοθεί store_id, επιστρέφονται μόνο
    οι παραγγελίες του συγκεκριμένου καταστήματος.
    """

    try:
        orders = list_orders(
            store_id=store_id
        )

        return {
            "status": "success",
            "orders": orders
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Αποτυχία ανάκτησης παραγγελιών: "
                f"{error}"
            )
        ) from error


@router.patch("/orders/{order_id}/ready")
def set_order_ready(
    order_id: int
):
    """
    Χαρακτηρίζει μια παραγγελία ως έτοιμη.
    """

    try:
        updated = mark_order_ready(
            order_id
        )

        if not updated:
            raise HTTPException(
                status_code=404,
                detail="Η παραγγελία δεν βρέθηκε."
            )

        return {
            "status": "success",
            "message": (
                "Η παραγγελία χαρακτηρίστηκε "
                "ως έτοιμη."
            )
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Αποτυχία ενημέρωσης παραγγελίας: "
                f"{error}"
            )
        ) from error


@router.put("/orders/{order_id}")
def edit_order(
    order_id: int,
    payload: OrderUpdateRequest
):
    """
    Ενημερώνει τα βασικά στοιχεία
    μιας υπάρχουσας παραγγελίας.
    """

    try:
        updated = update_order(
            order_id=order_id,
            items=payload.items,
            order_type=payload.order_type,
            address=payload.address,
            phone=payload.phone
        )

        if not updated:
            raise HTTPException(
                status_code=404,
                detail="Η παραγγελία δεν βρέθηκε."
            )

        return {
            "status": "success",
            "message": (
                "Η παραγγελία ενημερώθηκε "
                "επιτυχώς."
            )
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Αποτυχία επεξεργασίας "
                f"παραγγελίας: {error}"
            )
        ) from error


@router.delete("/orders/{order_id}")
def remove_order(
    order_id: int
):
    """
    Διαγράφει μια παραγγελία από τη βάση.
    """

    try:
        deleted = delete_order(
            order_id
        )

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Η παραγγελία δεν βρέθηκε."
            )

        return {
            "status": "success",
            "message": (
                "Η παραγγελία διαγράφηκε "
                "επιτυχώς."
            )
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Αποτυχία διαγραφής παραγγελίας: "
                f"{error}"
            )
        ) from error


@router.get("/stores/{store_id}/menu")
def get_menu(
    store_id: int
):
    """
    Επιστρέφει το πλήρες μενού
    ενός συγκεκριμένου καταστήματος.
    """

    try:
        menu_items = get_store_menu(
            store_id
        )

        return {
            "status": "success",
            "store_id": store_id,
            "menu_items": menu_items
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Αποτυχία ανάκτησης μενού: "
                f"{error}"
            )
        ) from error


@router.post(
    "/menu-items",
    status_code=201
)
def create_menu_item(
    payload: MenuItemCreateRequest
):
    """
    Προσθέτει νέο προϊόν στο μενού
    ενός καταστήματος.
    """

    try:
        menu_item_id = add_menu_item(
            store_id=payload.store_id,
            name=payload.name.strip(),
            category=payload.category.strip(),
            aliases=payload.aliases.strip(),
            options=payload.options.strip(),
            extras=payload.extras.strip(),
            available=payload.available
        )

        return {
            "status": "success",
            "message": (
                "Το προϊόν προστέθηκε "
                "επιτυχώς στο μενού."
            ),
            "menu_item_id": menu_item_id
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Αποτυχία προσθήκης προϊόντος: "
                f"{error}"
            )
        ) from error