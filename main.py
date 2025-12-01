from typing import Optional
from fastapi import FastAPI, Header, HTTPException
import os
import httpx

app = FastAPI()

API_KEY = "change-moi"  # la même valeur que dans l'Action GPT

# PISTE : à configurer avec tes variables d'environnement Render
PISTE_TOKEN_URL = "https://oauth.piste.gouv.fr/api/oauth/token"  # ou sandbox-oauth si tu es en sandbox
PISTE_CLIENT_ID = os.getenv("PISTE_CLIENT_ID", "A_REMPLACER")
PISTE_CLIENT_SECRET = os.getenv("PISTE_CLIENT_SECRET", "A_REMPLACER")
PISTE_SCOPE = "openid"
PISTE_GRANT_TYPE = "client_credentials"


async def get_piste_access_token() -> str:
    async with httpx.AsyncClient() as client:
        data = {
            "grant_type": PISTE_GRANT_TYPE,
            "client_id": PISTE_CLIENT_ID,
            "client_secret": PISTE_CLIENT_SECRET,
            "scope": PISTE_SCOPE,
        }
        resp = await client.post(PISTE_TOKEN_URL, data=data)
        resp.raise_for_status()
        payload = resp.json()
        # PISTE renvoie un access_token dans sa réponse JSON[web:4][web:11]
        return payload["access_token"]


async def call_legifrance_article(code: str, article: str, date: Optional[str]) -> dict:
    # Pour l'instant, on teste juste qu'on obtient un token PISTE
    access_token = await get_piste_access_token()

    return {
        "id": "TEST-LEGIARTI",
        "code": f"Code {code}",
        "article": article,
        "date_version": date or "2025-01-01",
        "etat": "VIGUEUR",
        "texte": f"Token PISTE obtenu (tronqué) : {access_token[:12]}...",
    }


@app.post("/legifrance/article")
async def get_legifrance_article(
    code: str,
    article: str,
    date: Optional[str] = None,
    x_api_key: str = Header(None, alias="X-API-Key"),
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return await call_legifrance_article(code=code, article=article, date=date)