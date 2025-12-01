from typing import Optional
from fastapi import FastAPI, Header, HTTPException
import os
import httpx

app = FastAPI()

API_KEY = "change-moi"  # la même valeur que dans l'Action GPT

# PISTE : à configurer avec tes variables d'environnement Render
PISTE_TOKEN_URL = "https://sandbox-oauth.piste.gouv.fr/api/oauth/token"  # ou sandbox-oauth si tu es en sandbox
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

async def ping_legifrance(access_token: str) -> dict:
    # Endpoint de test : on utilise simplement la racine avec une requête GET.
    # On veut juste vérifier que l'API répond avec le token Bearer.
    url = "https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        # On nève pas encore les erreurs pour les voir dans le texte renvoyé
        return {
            "status_code": resp.status_code,
            "body": resp.text[:200],  # on tronque pour rester léger
        }

async def call_legifrance_article(code: str, article: str, date: Optional[str]) -> dict:
    access_token = await get_piste_access_token()

    # Pour l'instant, on ignore code / article / date et on teste un article de démo
    # avec un identifiant LEGIARTI connu (issu de la doc / de tes tests manuels).
    url = "https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/consult/getArticle"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {
        "id": "LEGIARTI000006419282"  # identifiant d'article à tester
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, json=payload)

    # On renvoie tout ce qu'on peut pour voir ce qui se passe côté Légifrance
    status = resp.status_code
    text = resp.text[:400]

    return {
        "id": "LEGIARTI000006419282",
        "code": f"Code {code}",
        "article": article,
        "date_version": date or "2025-01-01",
        "etat": f"HTTP {status}",
        "texte": f"Réponse Légifrance (tronquée) : {text}",
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