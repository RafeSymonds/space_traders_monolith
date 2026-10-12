# Load tokens and settings from .env if present and pass them to every command.
-include .env
export

.PHONY: install gen dev server web build lint test

install:
	go mod download
	cd web && npm install

# Regenerate the Go client from openapi.json.
gen:
	go generate ./...

# Run the Go server and the Vite dev server together.
dev:
	$(MAKE) -j2 server web

server:
	go run ./cmd/server

web:
	cd web && npm run dev

build:
	go build -o bin/server ./cmd/server
	cd web && npm run build

lint:
	go vet ./...
	test -z "$$(gofmt -l cmd internal)"
	cd web && npm run lint

test:
	go test ./...
