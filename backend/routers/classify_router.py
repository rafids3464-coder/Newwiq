"""WASTE IQ – Classification Router"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request
from auth import get_current_user, UserInfo
from firestore_client import query_collection
from models import APIResponse

router = APIRouter()   # ← MUST BE BEFORE ANY @router decorators


@router.post("/", response_model=APIResponse)
async def classify_waste(
    request: Request,
    file: UploadFile = File(...),
    user: UserInfo = Depends(get_current_user)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    img_bytes = await file.read()

    if len(img_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image too large (max 10MB)")

    classifier = request.app.state.classifier

    if classifier is None:
        raise HTTPException(
            status_code=503,
            detail="AI model not loaded. Backend warming up."
        )

    try:
        import firestore_client as fc_module

        result = classifier.classify_and_save(
            img_bytes=img_bytes,
            uid=user.uid,
            firestore_client=fc_module,
            image_url=None,
        )

        return APIResponse(
            success=True,
            message="Classification complete",
            data=result
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=APIResponse)
async def classification_history(
    limit: int = 50,
    user: UserInfo = Depends(get_current_user)
):
    filters = [] if user.role == "admin" else [("uid", "==", user.uid)]

    logs = query_collection(
        "waste_logs",
        filters=filters if filters else None,
    )

    logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    logs = logs[:limit]

    return APIResponse(success=True, message=f"{len(logs)} records", data=logs)


@router.get("/stats", response_model=APIResponse)
async def classification_stats(user: UserInfo = Depends(get_current_user)):
    filters = [] if user.role in ("admin", "municipal") else [("uid", "==", user.uid)]

    logs = query_collection("waste_logs", filters=filters if filters else None)

    from collections import Counter
    categories = Counter(l.get("waste_category", "Unknown") for l in logs)

    return APIResponse(
        success=True,
        message="Stats computed",
        data={
            "total_classifications": len(logs),
            "by_category": dict(categories),
        },
    )
