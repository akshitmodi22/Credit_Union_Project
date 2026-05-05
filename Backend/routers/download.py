# ═══════════════════════════════════════════════════════════════
# routers/download.py — Secure file download via FastAPI
# Streams files from COS to browser
# ═══════════════════════════════════════════════════════════════

import io
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from cos_client import get_cos
from config import BUCKET

router = APIRouter()


def get_content_type(key: str) -> str:
    """Determine content type from file extension."""
    if key.endswith('.xlsx'):
        return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif key.endswith('.pdf'):
        return 'application/pdf'
    elif key.endswith('.png'):
        return 'image/png'
    elif key.endswith('.csv'):
        return 'text/csv'
    elif key.endswith('.json'):
        return 'application/json'
    return 'application/octet-stream'


@router.get("/download")
def download_file(key: str):
    """
    Securely stream a file from COS to browser.
    key: COS object key e.g. reports/excel/attrition_all_2026-04-29.xlsx
    """
    try:
        cos      = get_cos()
        obj      = cos.get_object(Bucket=BUCKET, Key=key)
        content  = obj["Body"].read()
        filename = key.split("/")[-1]

        return StreamingResponse(
            io.BytesIO(content),
            media_type=get_content_type(key),
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length":       str(len(content)),
                "Cache-Control":        "no-cache",
            }
        )

    except Exception as e:
        err = str(e)
        if "NoSuchKey" in err:
            raise HTTPException(status_code=404, detail=f"File not found: {key}")
        elif "AccessDenied" in err:
            raise HTTPException(status_code=403, detail="Access denied to file")
        raise HTTPException(status_code=500, detail=f"Download error: {err}")
