# Space Traders Workspace

## Repositories

### 1. `space_traders/` - Python FastAPI Backend
FastAPI service that wraps the Space Traders OpenAPI and provides game automation.

**Tech Stack:** Python, FastAPI, ruff, pytest

**Setup:**
```bash
cd space_traders
./bin/install    # Install dependencies
```

**Run:**
```bash
./bin/run local  # localhost only
./bin/run lan    # LAN-accessible (0.0.0.0:8000)
```

**Key Structure:**
- `app/` - FastAPI application
- `space_traders_api/` - Generated OpenAPI Python client
- `bin/` - Scripts (install, run)

---

### 2. `ui/` - React TypeScript Frontend
React SPA that interfaces with the FastAPI backend.

**Tech Stack:** TypeScript, React, Vite, ruff

**Setup:**
```bash
cd ui
npm install
```

**Run:**
```bash
npm run dev     # Development server
npm run build   # Production build
```

**Key Structure:**
- `src/api/` - Generated TypeScript API client from OpenAPI spec
- `src/` - React components and pages

---

## Code Style

- **Python:** ruff with line-length 120, target Python 3.12
- **TypeScript:** ESLint + Prettier (default Vite config)

## OpenAPI Spec

The OpenAPI spec is stored at `openapi.json` and was fetched from `https://api.spacetraders.io/v2/documentation/json`.
