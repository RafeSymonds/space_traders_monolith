# Space Traders Workspace

## Repositories

### 1. `space_traders/` - Python CLI Application
A space trading game CLI with automation capabilities.

**Tech Stack:** Python, cmd2, pytest, ruff

**Key Commands:**
- `ruff check` - Lint
- `ruff format` - Format
- `pytest` - Run tests

**Entry Point:** `python -m space_traders.main`

**Key Directories:**
- `src/space_traders/commands/` - CLI command implementations
- `src/space_traders/automation/` - Automation loop
- `src/space_traders/api/` - Space Traders API client
- `src/space_traders/database_operations/` - Database layer

---

### 2. `space_traders_api/` - Python FastAPI Backend
Backend API server for the space trading game (named `flock_backend`).

**Tech Stack:** Python, FastAPI, ruff, pytest

**Setup:**
```bash
./bin/install    # Install dependencies and init submodules
```

**Run:**
```bash
./bin/run local  # localhost only
./bin/run lan    # LAN-accessible (0.0.0.0:8000)
```

**Note:** This repo uses `space_traders/` as a git submodule via `libraries/space_traders/`

---

### 3. `space_traders_app/` - iOS Swift App (Flock)
SwiftUI-based iOS application for the space trading game.

**Tech Stack:** Swift, SwiftUI, SwiftFormat, Xcode

**Key Commands:**
```bash
./bin/format   # Format Swift code (requires swiftformat)
./bin/deploy   # Deploy to iOS device via ios-deploy
./bin/install  # Install iOS deployment tools
```

**Build:** Use Xcode or `xcodebuild`

---

## Code Style

- **Python:** ruff with line-length 120, target Python 3.12
- **Swift:** SwiftFormat with Swift 6.1
