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
            detail="AI model not loaded. Backend warming up. Try again in 30 seconds."
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
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")
