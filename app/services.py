import httpx
import asyncio
from typing import Dict, Any


async def fetch_profile_data(name: str) -> Dict[str, Any]:
    # asyncio.gather fires all three API calls at the same time instead of one after another
    # return_exceptions=True means if one call crashes, it returns the exception as a value
    # instead of immediately stopping everything — we handle each error individually below
    async with httpx.AsyncClient() as client:
        genderize, agify, nationalize = await asyncio.gather(
            client.get(f"https://api.genderize.io?name={name}"),
            client.get(f"https://api.agify.io?name={name}"),
            client.get(f"https://api.nationalize.io?name={name}"),
            return_exceptions=True
        )

    # --- Genderize ---
    # isinstance(..., Exception) catches network errors (timeout, DNS failure, etc.)
    if isinstance(genderize, Exception) or genderize.status_code != 200:
        raise ValueError("Genderize returned an invalid response")
    g_data = genderize.json()
    # gender: null means the API couldn't determine gender for this name
    # count: 0 means there was no sample data — result is unreliable
    if g_data.get("gender") is None or g_data.get("count", 0) == 0:
        raise ValueError("Genderize returned an invalid response")

    # --- Agify ---
    if isinstance(agify, Exception) or agify.status_code != 200:
        raise ValueError("Agify returned an invalid response")
    a_data = agify.json()
    if a_data.get("age") is None:
        raise ValueError("Agify returned an invalid response")

    # --- Nationalize ---
    if isinstance(nationalize, Exception) or nationalize.status_code != 200:
        raise ValueError("Nationalize returned an invalid response")
    n_data = nationalize.json()
    countries = n_data.get("country", [])
    if not countries:
        raise ValueError("Nationalize returned an invalid response")
    # Pick the country with the highest probability from the list
    best_country = max(countries, key=lambda c: c["probability"])

    # --- Age group classification ---
    age = a_data["age"]
    if 0 <= age <= 12:
        age_group = "child"
    elif 13 <= age <= 19:
        age_group = "teenager"
    elif 20 <= age <= 59:
        age_group = "adult"
    else:
        age_group = "senior"

    return {
        "name": name,
        "gender": g_data["gender"],
        "gender_probability": g_data["probability"],
        "sample_size": g_data["count"],   # renamed from "count" as required
        "age": age,
        "age_group": age_group,
        "country_id": best_country["country_id"],
        "country_probability": best_country["probability"]
    }
