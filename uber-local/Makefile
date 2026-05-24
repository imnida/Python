.PHONY: up down logs build ps test clean

# Lancer tout le stack
up:
	docker compose up --build -d

# Arrêter
down:
	docker compose down

# Rebuild forcé
build:
	docker compose build --no-cache

# Logs en direct
logs:
	docker compose logs -f

# Status des conteneurs
ps:
	docker compose ps

# Test rapide de l'API d'ingestion
test-ingest:
	curl -s -X POST http://localhost:8001/ping \
	  -H "Content-Type: application/json" \
	  -d '{"driver_id":"test-001","lat":48.8566,"lng":2.3522,"speed":30,"bearing":90}' | python3 -m json.tool

# Test du dispatch engine
test-dispatch:
	curl -s "http://localhost:8002/drivers/nearby?lat=48.8566&lng=2.3522&radius_km=5&limit=5" | python3 -m json.tool

# Stats système
stats:
	curl -s "http://localhost:8002/stats" | python3 -m json.tool
	curl -s "http://localhost:8001/health" | python3 -m json.tool

# Nettoyage complet (volumes compris)
clean:
	docker compose down -v --rmi local
