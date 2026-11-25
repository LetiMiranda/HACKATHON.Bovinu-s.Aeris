from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class ItemEstimadoIA(BaseModel):
    alimento: str = Field(
        description="Nome do alimento em português minúsculo, ex.: arroz branco, frango grelhado"
    )
    peso_gramas_estimado: float = Field(
        ge=0, description="Estimativa visual do peso da porção em gramas"
    )
    confianca: float = Field(
        ge=0, le=1, description="Nível de confiança da identificação entre 0 e 1"
    )


class AnaliseVisaoIA(BaseModel):
    itens: List[ItemEstimadoIA]


class ItemFinal(BaseModel):
    alimento: str
    peso_gramas: float
    confianca: float


class AnalisePratoResponse(BaseModel):
    prato_id: int
    cliente_id: str
    registrado_em: datetime
    peso_total_gramas: float
    itens: List[ItemFinal]


class ResumoAlimentoDia(BaseModel):
    alimento: str
    peso_total_gramas: float
    peso_total_kg: float
    quantidade_porcoes: int


class RelatorioDiaResponse(BaseModel):
    data: str
    peso_geral_gramas: float
    peso_geral_kg: float
    alimentos: List[ResumoAlimentoDia]