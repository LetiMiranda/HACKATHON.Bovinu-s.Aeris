from datetime import datetime
from pathlib import Path
import sqlite3
from typing import List

from app.schemas import ItemFinal

DB_PATH = Path("data/pratos_peso.db")


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pratos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id TEXT NOT NULL,
            registrado_em TEXT NOT NULL,
            peso_total_gramas REAL NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS itens_prato (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prato_id INTEGER NOT NULL,
            alimento TEXT NOT NULL,
            peso_gramas REAL NOT NULL,
            confianca REAL NOT NULL,
            FOREIGN KEY (prato_id) REFERENCES pratos(id)
        )
    """)
    conn.commit()
    conn.close()


def salvar_prato(
    cliente_id: str,
    registrado_em: datetime,
    peso_total: float,
    itens: List[ItemFinal],
) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO pratos (cliente_id, registrado_em, peso_total_gramas)
        VALUES (?, ?, ?)
        """,
        (cliente_id, registrado_em.isoformat(), peso_total),
    )
    prato_id = cur.lastrowid

    for item in itens:
        cur.execute(
            """
            INSERT INTO itens_prato (prato_id, alimento, peso_gramas, confianca)
            VALUES (?, ?, ?, ?)
            """,
            (prato_id, item.alimento, item.peso_gramas, item.confianca),
        )

    conn.commit()
    conn.close()
    return int(prato_id)


def somar_alimentos_no_intervalo(inicio_iso: str, fim_iso: str) -> List[sqlite3.Row]:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            i.alimento AS alimento,
            ROUND(SUM(i.peso_gramas), 1) AS peso_total_gramas,
            COUNT(i.id) AS quantidade_porcoes
        FROM itens_prato i
        INNER JOIN pratos p ON p.id = i.prato_id
        WHERE p.registrado_em BETWEEN ? AND ?
        GROUP BY i.alimento
        ORDER BY peso_total_gramas DESC
        """,
        (inicio_iso, fim_iso),
    )
    linhas = cur.fetchall()
    conn.close()
    return linhas