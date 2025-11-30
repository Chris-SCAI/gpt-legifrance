from typing import Optional
from fastapi import FastAPI, Header, HTTPException

app = FastAPI()

API_KEY = "change-moi"  # on mettra la même valeur dans l’Action GPT

@app.post("/legifrance/article")
async def get_legifrance_article(
    code: str,
    article: str,
    date: Optional[str] = None,
    x_api_key: str = Header(None, alias="X-API-Key")
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Réponse de test, sans appel Legifrance pour l'instant
    return {
        "id": "TEST-LEGIARTI",
        "code": f"Code {code}",
        "article": article,
        "date_version": date or "2025-01-01",
        "etat": "VIGUEUR",
        "texte": "Ceci est un texte d’exemple renvoyé par le serveur (pas encore Légifrance)."
    }