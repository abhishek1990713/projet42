async def upload_json(
    request: Request,
    x_correlation_id: str = Header(...),
    x_application_id: str = Header(...),
    x_soeid: str = Header(...),
    x_authorization_coin: str = Header(...),
    db: Session = Depends(get_db)
):
    # Validate Content-Type manually if you want
    if request.headers.get("Content-Type", "").lower() != "application/json":
        raise HTTPException(
            status_code=415,
            detail="Content-Type must be application/json"
        )

    content_json = await request.json()
    ...

