# NUVARA GREENS

Angular storefront plus a FastAPI/PostgreSQL API for products, enquiries, orders, and subscriptions.

## Run locally

1. Copy `backend/.env.example` to `backend/.env`, then supply your Supabase password and WhatsApp number.
2. In `backend`, create a virtual environment, install dependencies with `pip install -r requirements.txt`, then run `uvicorn app.main:app --reload --port 8000`.
3. In `frontend`, install dependencies with `npm install`, then run `npm start`.
4. Open `http://localhost:4200`.

On a first run the API creates its tables and seeds the original six products. Add Alembic migrations before a production release so schema changes are tracked explicitly.

The browser only communicates with the FastAPI API. The database URL stays in the backend environment file and must never be exposed in Angular.
