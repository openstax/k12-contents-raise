from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Union
from pathlib import Path
import os, json


HTML_DATA_PATH = "/content/html"
JSON_DATA_PATH = "/content/json"


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


ResponseModel = Union[
    ContentData,
    Dict[str, str],
]


@app.get("/contents/{version_id}/{content_id}.json",
         response_model=ResponseModel)
@app.get("/contents/{content_id}.json", response_model=ResponseModel)
async def get_content(content_id):
    maybe_variant = os.getenv("CONTENT_VARIANT")
    maybe_variant_data = None

    maybe_html_data = Path(HTML_DATA_PATH) / f"{content_id}.html"
    if Path(f"{JSON_DATA_PATH}/{content_id}.json").is_file():
        with open(f"{JSON_DATA_PATH}/{content_id}.json") as f:
            file_content = json.load(f)
        return file_content

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