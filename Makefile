.PHONY: venv install env db-up db-down db-logs pgadmin psql lint test dashboard

venv:
	python3 -m venv .venv
	@echo "Ative com: source .venv/bin/activate"

install:
	pip install -r requirements.txt
	pip install -e .

env:
	cp -n .env.example .env

db-up:
	docker compose up -d db

db-down:
	docker compose down

db-logs:
	docker compose logs -f db

pgadmin:
	docker compose --profile tools up -d pgadmin

psql:
	docker compose exec db psql -U $${POSTGRES_USER:-tcc_user} -d $${POSTGRES_DB:-tcc_grafos}

lint:
	ruff check src tests dashboard

test:
	pytest

dashboard:
	streamlit run dashboard/app.py
