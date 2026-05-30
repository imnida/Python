.PHONY: all install add add-dev run test lint clean \
        up-rpi down-rpi logs-rpi build-rpi ps-rpi

# Vérifie si uv est installé
UV := $(shell command -v uv 2> /dev/null)

check_uv:
ifndef UV
	$(error "uv n'est pas installé !")
endif

install:
	uv sync

add:
	@test -n "$(lib)" || (echo "Usage: make add lib=pandas" && exit 1)
	uv add $(lib)

add-dev:
	@test -n "$(lib)" || (echo "Usage: make add-dev lib=pytest" && exit 1)
	uv add --dev $(lib)

run:
	uv run src/main.py

test:
	uv run pytest tests/

lint:
	uv run ruff check --fix .

clean:
	rm -rf .venv
	rm -rf build dist
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache

# =============================================================================
# Raspberry Pi 5 — stack complète (ARM64)
# Prérequis: cp .env.example .env && renseigner les variables
# =============================================================================

# Démarrer tous les services sur le RPi
up-rpi:
	docker compose -f docker-compose.rpi.yaml up -d

# Arrêter tous les services
down-rpi:
	docker compose -f docker-compose.rpi.yaml down

# Suivre les logs de tous les services
logs-rpi:
	docker compose -f docker-compose.rpi.yaml logs -f

# Builder les images localement sur le RPi (si pas de GHCR)
build-rpi:
	docker compose -f docker-compose.rpi.yaml build

# Voir l'état des conteneurs
ps-rpi:
	docker compose -f docker-compose.rpi.yaml ps