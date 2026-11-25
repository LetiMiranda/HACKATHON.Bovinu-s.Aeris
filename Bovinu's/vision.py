import os
from typing import List, Optional

from fastapi import HTTPException
from google import genai
from google.genai import types

from app.schemas import AnaliseVisaoIA, ItemEstimadoIA, ItemFinal

MODEL_ID = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

SINONIMOS_ALIMENTOS = {
    "arroz": "arroz branco",
    "feijao": "feijao carioca",
    "feijão": "feijao carioca",
    "peito de frango": "frango grelhado",
    "frango": "frango grelhado",
    "alface": "salada de alface",
    "salada": "salada de alface",
    "fritas": "batata frita",
}


def get_client() -> genai.Client:
    if not (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")):
        raise HTTPException(
            status_code=503,
            detail=(
                "Gemini API key is not configured. Add GEMINI_API_KEY to a .env "
                "file in the app folder, then restart the server."
            ),
        )
    return genai.Client()


def normalizar_alimento(nome: str) -> str:
    limpo = nome.strip().lower()
    return SINONIMOS_ALIMENTOS.get(limpo, limpo)


def analisar_imagem_com_ia(image_bytes: bytes, mime_type: str) -> List[ItemEstimadoIA]:
    prompt = (
        "Analise esta foto de um prato de restaurante por quilo. "
        "Liste cada alimento visível separadamente e estime o peso em gramas de cada porção. "
        "Não inclua o prato vazio ou talheres como alimento."
    )

    client = get_client()
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            prompt,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AnaliseVisaoIA,
            temperature=0.2,
        ),
    )

    parsed: Optional[AnaliseVisaoIA] = response.parsed
    if parsed is None or not parsed.itens:
        raise HTTPException(
            status_code=422,
            detail="Não foi possível identificar alimentos na imagem enviada.",
        )
    return parsed.itens


def consolidar_pesos(
    itens_ia: List[ItemEstimadoIA],
    peso_balanca: Optional[float],
) -> List[ItemFinal]:
    soma_ia = sum(item.peso_gramas_estimado for item in itens_ia)
    fator = (peso_balanca / soma_ia) if (peso_balanca and soma_ia > 0) else 1.0

    return [
        ItemFinal(
            alimento=normalizar_alimento(item.alimento),
            peso_gramas=round(item.peso_gramas_estimado * fator, 1),
            confianca=round(item.confianca, 2),
        )
        for item in itens_ia
    ]