from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import List, Optional
from zoneinfo import ZoneInfo

from fastapi.staticfiles import StaticFiles

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import HTMLResponse

from app.database import init_db, salvar_prato, somar_alimentos_no_intervalo
from app.schemas import AnalisePratoResponse, RelatorioDiaResponse, ResumoAlimentoDia
from vision import analisar_imagem_com_ia, consolidar_pesos

load_dotenv()

app = FastAPI(title="Kilo IA - Peso por Alimento")

TZ_SP = ZoneInfo("America/Sao_Paulo")
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
PROJECT_DIR = Path(__file__).parent.parent
INDEX_HTML_PATH = PROJECT_DIR / "templates" / "index.html"

init_db()


def agora_sp() -> datetime:
    return datetime.now(TZ_SP)


def intervalo_dia_sp_em_iso(data_str: Optional[str]) -> tuple[str, str, str]:
    if data_str:
        try:
            dia_sp = date.fromisoformat(data_str)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Data inválida. Use o formato YYYY-MM-DD (ex.: 2026-11-25).",
            )
    else:
        dia_sp = agora_sp().date()

    inicio_sp = datetime.combine(dia_sp, time.min, tzinfo=TZ_SP)
    fim_sp = datetime.combine(dia_sp, time.max, tzinfo=TZ_SP)

    return (
        dia_sp.isoformat(),
        inicio_sp.astimezone(timezone.utc).isoformat(),
        fim_sp.astimezone(timezone.utc).isoformat(),
    )


@app.get("/", response_class=HTMLResponse)
def frontend_simples() -> str:
    return INDEX_HTML_PATH.read_text(encoding="utf-8")


@app.post("/api/pratos/analisar", response_model=AnalisePratoResponse)
async def analisar_prato(
    cliente_id: str = Form(...),
    imagem: UploadFile = File(...),
    peso_balanca_gramas: Optional[float] = Form(default=None, gt=0),
):
    if imagem.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Formato de imagem não suportado. Use JPEG, PNG ou WEBP.",
        )

    image_bytes = await imagem.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Arquivo de imagem vazio.")

    itens_ia = analisar_imagem_com_ia(image_bytes, imagem.content_type)
    itens_finais = consolidar_pesos(itens_ia, peso_balanca_gramas)

    peso_total = round(sum(i.peso_gramas for i in itens_finais), 1)
    agora = agora_sp()
    prato_id = salvar_prato(cliente_id, agora, peso_total, itens_finais)

    return AnalisePratoResponse(
        prato_id=prato_id,
        cliente_id=cliente_id,
        registrado_em=agora,
        peso_total_gramas=peso_total,
        itens=itens_finais,
    )


@app.get("/api/relatorios/alimentos-dia", response_model=RelatorioDiaResponse)
def somar_alimentos_por_dia(
    data: Optional[str] = Query(
        default=None,
        description="Data no formato YYYY-MM-DD no fuso America/Sao_Paulo",
    )
):
    data_alvo, inicio_iso, fim_iso = intervalo_dia_sp_em_iso(data)
    linhas = somar_alimentos_no_intervalo(inicio_iso, fim_iso)

    alimentos: List[ResumoAlimentoDia] = []
    for linha in linhas:
        gramas = float(linha["peso_total_gramas"] or 0.0)
        alimentos.append(
            ResumoAlimentoDia(
                alimento=linha["alimento"],
                peso_total_gramas=round(gramas, 1),
                peso_total_kg=round(gramas / 1000.0, 3),
                quantidade_porcoes=int(linha["quantidade_porcoes"]),
            )
        )

    peso_geral_g = round(sum(a.peso_total_gramas for a in alimentos), 1)

    return RelatorioDiaResponse(
        data=data_alvo,
        peso_geral_gramas=peso_geral_g,
        peso_geral_kg=round(peso_geral_g / 1000.0, 3),
        alimentos=alimentos,
    )


STATIC_DIR = Path(__file__).parent / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")