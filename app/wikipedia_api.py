import requests
from fastapi import APIRouter

router = APIRouter()

@router.get("/edukasi/{topik}")
def get_summary(topik: str):
    url = f"https://id.wikipedia.org/api/rest_v1/page/summary/{topik}"
    r = requests.get(url)
    if r.status_code != 200:
        return {"error": "Gagal ambil data dari Wikipedia."}
    data = r.json()
    return {
        "title": data.get("title"),
        "extract": data.get("extract"),
        "url": data.get("content_urls", {}).get("desktop", {}).get("page")
    }

