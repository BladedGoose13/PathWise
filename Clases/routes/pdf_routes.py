from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import shutil
import pdfplumber

router = APIRouter(prefix="/pdf", tags=["pdf"])

UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    dest = UPLOAD_DIR / file.filename
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"ok": True, "filename": file.filename}

@router.get("/serve/{filename}")
def serve_pdf(filename: str):
    fpath = UPLOAD_DIR / filename
    if not fpath.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(fpath, media_type="application/pdf", filename=filename)

@router.get("/text/{filename}")
def extract_text(filename: str):
    fpath = UPLOAD_DIR / filename
    if not fpath.exists():
        raise HTTPException(status_code=404, detail="File not found")
    pages = []
    try:
        with pdfplumber.open(fpath) as pdf:
            for p in pdf.pages:
                pages.append(p.extract_text() or "")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text: {e}")
    return JSONResponse({"ok": True, "text": "\n\n".join(pages)})