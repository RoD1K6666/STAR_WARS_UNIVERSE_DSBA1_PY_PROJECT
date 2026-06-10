import math
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from pathlib import Path

app = FastAPI(title="Star Wars API", version="1.0.0")

DATA_DIR = Path(__file__).parent / "archive" / "csv"


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / f"{name}.csv")


def sanitize(val):
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return None
    if isinstance(val, np.integer):
        return int(val)
    if isinstance(val, np.floating):
        return None if math.isnan(val) else float(val)
    return val


def to_records(df: pd.DataFrame) -> list:
    return [{k: sanitize(v) for k, v in row.items()} for row in df.to_dict(orient="records")]


# ── Pydantic models ──────────────────────────────────────────────────────────

class CharacterCreate(BaseModel):
    name: str
    species: Optional[str] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    hair_color: Optional[str] = None
    eye_color: Optional[str] = None
    skin_color: Optional[str] = None
    homeworld: Optional[str] = None


class StarshipCreate(BaseModel):
    name: str
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    length: Optional[float] = None
    crew: Optional[float] = None
    passengers: Optional[float] = None
    starship_class: Optional[str] = None
    MGLT: Optional[float] = None
    hyperdrive_rating: Optional[float] = None


# ── GET endpoints ────────────────────────────────────────────────────────────

@app.get("/characters")
def get_characters(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max records to return"),
    species: Optional[str] = Query(None, description="Filter by species"),
    gender: Optional[str] = Query(None, description="Filter by gender"),
):
    df = load("characters")
    if species:
        df = df[df["species"].str.lower() == species.lower()]
    if gender:
        df = df[df["gender"].str.lower() == gender.lower()]
    total = len(df)
    records = to_records(df.iloc[skip : skip + limit])
    return {"total": total, "skip": skip, "limit": limit, "data": records}


@app.get("/characters/{character_id}")
def get_character(character_id: int):
    df = load("characters")
    row = df[df["id"] == character_id]
    if row.empty:
        raise HTTPException(status_code=404, detail="Character not found")
    return to_records(row)[0]


@app.get("/starships")
def get_starships(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max records to return"),
    starship_class: Optional[str] = Query(None, description="Filter by starship class"),
):
    df = load("starships")
    if starship_class:
        df = df[df["starship_class"].str.lower() == starship_class.lower()]
    total = len(df)
    records = to_records(df.iloc[skip : skip + limit])
    return {"total": total, "skip": skip, "limit": limit, "data": records}


@app.get("/weapons")
def get_weapons(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max records to return"),
    type: Optional[str] = Query(None, description="Filter by weapon type"),
):
    df = load("weapons")
    if type:
        df = df[df["type"].str.lower() == type.lower()]
    total = len(df)
    records = to_records(df.iloc[skip : skip + limit])
    return {"total": total, "skip": skip, "limit": limit, "data": records}


@app.get("/planets")
def get_planets(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max records to return"),
):
    df = load("planets")
    total = len(df)
    records = to_records(df.iloc[skip : skip + limit])
    return {"total": total, "skip": skip, "limit": limit, "data": records}


# ── POST endpoints ───────────────────────────────────────────────────────────

@app.post("/characters", status_code=201)
def create_character(character: CharacterCreate):
    df = load("characters")
    new_id = int(df["id"].max()) + 1
    new_row = {"id": new_id, **character.model_dump()}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(DATA_DIR / "characters.csv", index=False)
    return {"id": new_id, **character.model_dump()}


@app.post("/starships", status_code=201)
def create_starship(starship: StarshipCreate):
    df = load("starships")
    new_id = int(df["id"].max()) + 1
    new_row = {"id": new_id, **starship.model_dump()}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(DATA_DIR / "starships.csv", index=False)
    return {"id": new_id, **starship.model_dump()}
