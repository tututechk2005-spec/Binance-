.PHONY: up down build restart logs migrate seed shell-api shell-db clean

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose up --build -d

restart:
	docker compose restart api worker beat

logs:
	docker compose logs -f api worker

migrate:
	docker compose exec api alembic upgrade head

seed:
	docker compose exec api python scripts/seed_db.py

shell-api:
	docker compose exec api bash

shell-db:
	docker compose exec postgres psql -U batpro -d batpro

clean:
	docker compose down -v --remove-orphans

dev-frontend:
	cd frontend && npm run dev

dev-backend:
	cd backend && uvicorn main:app --reload --port 8000

typecheck-frontend:
	cd frontend && npx tsc --noEmit

format-backend:
	cd backend && black . && isort .

test-backend:
	cd backend && pytest

install-frontend:
	cd frontend && npm install

install-backend:
	cd backend && pip install -r requirements.txt
