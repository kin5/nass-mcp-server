.PHONY: build run requirements

-include .env

DOT_ENV := $(shell ls .env 2>/dev/null)
VENV := $(shell ls -d .venv* 2>/dev/null)

setup_venv:
ifndef VENV
	@echo "No virtual environment found, creating one..."
	uv venv
endif
	@echo "Installing dependencies..."

setup_dotenv:
ifndef DOT_ENV
	@echo "No .env file found, copying from .env.example..."
	cp -n .env.example .env
endif

setup: setup_venv setup_dotenv
	uv pip install -r requirements.txt

requirements:
	uv export --no-hashes --format requirements-txt > requirements.txt

build: setup_dotenv
	docker build -t nass-mcp .

run: build
	docker run -p ${NASS_MCP_PORT}:${NASS_MCP_PORT} nass-mcp