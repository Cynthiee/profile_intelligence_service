# Profile Intelligence Service

## Overview
A RESTful API that enriches names using Genderize, Agify, and Nationalize APIs, persists the processed data, and provides CRUD operations with idempotency and filtering support.

## Live API Base URL
https://YOUR-DEPLOYED-URL.railway.app

## Endpoints
- `POST /api/profiles` – Create or retrieve existing profile
- `GET /api/profiles/{id}` – Retrieve a profile by UUID
- `GET /api/profiles` – List profiles with optional filters (gender, country_id, age_group)
- `DELETE /api/profiles/{id}` – Delete a profile

## Local Setup
1. `python -m venv venv`
2. `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (macOS/Linux)
3. `pip install -r requirements.txt`
4. `uvicorn app.main:app --reload`

## Tech Stack
- FastAPI
- SQLAlchemy + Postgresql
- httpx (async HTTP client)
- UUID v7

