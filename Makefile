# Makefile for managing Docker Compose environments

# --- Development Commands ---

## Build and start the development containers
dev:
	docker compose -f docker-compose.yaml -f docker-compose.dev.yaml up --build

## Stop the development containers
dev-down:
	docker compose -f docker-compose.yaml -f docker-compose.dev.yaml down

## Get an interactive shell inside the running dev container
dev-shell:
	docker compose -f docker-compose.yaml -f docker-compose.dev.yaml exec app bash


# --- Production Commands ---

## Build and start the production containers in detached mode
prod:
	docker compose -f docker-compose.yaml -f docker-compose.prod.yaml up --build -d

## Stop the production containers
prod-down:
	docker compose -f docker-compose.yaml -f docker-compose.prod.yaml down


# --- Utility Commands ---

## Stop all containers and remove volumes (cleans the cache)
clean:
	docker compose -f docker-compose.yaml -f docker-compose.dev.yaml down -v
	docker compose -f docker-compose.yaml -f docker-compose.prod.yaml down -v

.PHONY: dev dev-down dev-shell prod prod-down clean
