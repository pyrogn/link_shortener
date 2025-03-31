from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional
import string
import random
from datetime import datetime

app = FastAPI(title="Link Shortener API")


class LinkCreate(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None


class LinkResponse(BaseModel):
    short_code: str
    original_url: HttpUrl
    created_at: datetime
    expires_at: Optional[datetime] = None
    clicks: int = 0
    last_accessed: Optional[datetime] = None


source_url = str
short_code = str
links_db: dict[short_code, LinkResponse] = {}
original_url_index: dict[source_url, short_code] = {}


def generate_short_code(length: int = 6) -> str:
    """Генерация короткого кода для сокращенной ссылки."""
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


@app.get("/")
async def root():
    return {"message": "Welcome to Link Shortener API"}


@app.post("/links/shorten", response_model=LinkResponse)
async def create_short_link(link_data: LinkCreate):
    if link_data.original_url in original_url_index:
        return links_db[original_url_index[link_data.original_url]]

    if link_data.custom_alias:
        if link_data.custom_alias in links_db:
            raise HTTPException(status_code=400, detail="Custom alias already in use")
        short_code = link_data.custom_alias
    else:
        while True:
            short_code = generate_short_code()
            if short_code not in links_db:
                break

    link = LinkResponse(
        short_code=short_code,
        original_url=link_data.original_url,
        created_at=datetime.now(),
        expires_at=link_data.expires_at,
        clicks=0,
        last_accessed=None,
    )

    links_db[short_code] = link
    original_url_index[link_data.original_url] = short_code

    return link


@app.get("/links/search", response_model=Optional[LinkResponse])
async def search_by_original_url(original_url: str = Query(...)):
    if original_url in original_url_index:
        short_code = original_url_index[original_url]
        return links_db[short_code]

    # проверка нормализации урла из параметров и из БД для улучшения поиска
    try:
        normalized_url = HttpUrl(original_url)
        str_normalized_url = str(normalized_url)

        if str_normalized_url in original_url_index:
            short_code = original_url_index[str_normalized_url]
            return links_db[short_code]

        for url in original_url_index:
            if str(HttpUrl(url)) == str_normalized_url:
                short_code = original_url_index[url]
                return links_db[short_code]
    except Exception:
        pass

    raise HTTPException(status_code=404, detail="Link not found")


@app.get("/{short_code}")
async def redirect_to_original(short_code: str, request: Request):
    if short_code not in links_db:
        raise HTTPException(status_code=404, detail="Link not found")

    link = links_db[short_code]

    if link.expires_at and datetime.now() > link.expires_at:
        del original_url_index[link.original_url]
        del links_db[short_code]
        raise HTTPException(status_code=404, detail="Link has expired")

    link.clicks += 1
    link.last_accessed = datetime.now()

    return RedirectResponse(url=str(link.original_url))


@app.get("/links/{short_code}", response_model=LinkResponse)
async def get_link_info(short_code: str):
    if short_code not in links_db:
        raise HTTPException(status_code=404, detail="Link not found")

    link = links_db[short_code]

    if link.expires_at and datetime.now() > link.expires_at:
        del original_url_index[link.original_url]
        del links_db[short_code]
        raise HTTPException(status_code=404, detail="Link has expired")

    return link


@app.put("/links/{short_code}", response_model=LinkResponse)
async def update_link(short_code: str, link_data: LinkCreate):
    if short_code not in links_db:
        raise HTTPException(status_code=404, detail="Link not found")

    link = links_db[short_code]

    del original_url_index[link.original_url]

    link.original_url = link_data.original_url
    if link_data.expires_at:
        link.expires_at = link_data.expires_at

    original_url_index[link_data.original_url] = short_code

    return link


@app.delete("/links/{short_code}")
async def delete_link(short_code: str):
    if short_code not in links_db:
        raise HTTPException(status_code=404, detail="Link not found")

    link = links_db[short_code]

    del original_url_index[link.original_url]
    del links_db[short_code]

    return {"message": "Link deleted successfully"}
