.PHONY: venv install env db-up db-down db-reset db-logs pgadmin psql lint test \
	raio mercado polos carga pipeline figuras dashboard

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

# apaga o volume do banco (os dados são recarregados por `make carga`)
db-reset:
	docker compose down -v
	docker compose up -d db

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

raio:
	python -m tcc_grafos.camada_raio

mercado:
	python -m tcc_grafos.camada_mercado

# escore dos grandes polos (a RAIS vem do BigQuery na primeira vez e fica em cache)
polos:
	python -m tcc_grafos.camada_polos

carga:
	python -m tcc_grafos.db.load

pipeline: raio mercado polos carga

# figuras da monografia em docs/figuras/ (lê data/processed)
figuras:
	python -m tcc_grafos.figuras

dashboard:
	streamlit run dashboard/app.py
