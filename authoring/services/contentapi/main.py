from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from pathlib import Path

DEFAULT_CONTENT_TEMPLATE = "<div><p>This is content for ID {}</p>" \
    "<p>Math: \\( \\frac{{1}}{{2}} \\)</p></div>"


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


@app.get("/contents/{content_id}.json", response_model=ContentData)
async def create_event(content_id):
    maybe_html_data = Path(HTML_DATA_PATH) / f"{content_id}.html"
    if maybe_html_data.exists():
        content = maybe_html_data.read_text(encoding="utf-8")
    else:
        content = DEFAULT_CONTENT_TEMPLATE.format(content_id)
    content_item = ContentItem(variant="main", html=content)
    data = ContentData(id=content_id, content=[content_item])
    return data
