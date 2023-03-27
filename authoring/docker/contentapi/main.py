from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from pathlib import Path
import os


HTML_DATA_PATH = "/html"


app = FastAPI(
    title="RAISE Content API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"]
)


class ContentItem(BaseModel):
    variant: str
    html: str


class ContentData(BaseModel):
    id: str
    content: List[ContentItem]


@app.get("/contents/{version_id}/{content_id}.json", response_model=ContentData)
@app.get("/contents/{content_id}.json", response_model=ContentData)
async def get_content(content_id):
    maybe_variant = os.getenv("CONTENT_VARIANT")
    maybe_variant_data = None

    maybe_html_data = Path(HTML_DATA_PATH) / f"{content_id}.html"

    if maybe_variant:
        maybe_variant_data = Path(HTML_DATA_PATH) / f"{content_id}/{maybe_variant}.html"

    if maybe_variant_data and maybe_variant_data.exists():
        content = maybe_variant_data.read_text(encoding="utf-8")
    elif maybe_html_data.exists():
        content = maybe_html_data.read_text(encoding="utf-8")
    else:
        raise HTTPException(status_code=404, detail="Item not found")
    content_item = ContentItem(variant="main", html=content)
    data = ContentData(id=content_id, content=[content_item])
    return data
