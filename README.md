# Chess Bot (Dialogflow + Stockfish)

Flask webhook that lets a Dialogflow agent play chess against Stockfish. Game state is stored in MySQL (Cloud SQL) keyed by the Dialogflow session URL.

## Features

- Dialogflow webhook endpoint for chess actions
- Stockfish-backed move generation
- Persistent games in MySQL
- Cloud Run deployment script

## Project Layout

- `main.py`: Flask app + Dialogflow webhook handlers
- `chess_engine.py`: Chess and Stockfish helpers
- `entities/`: Dialogflow entity definitions
- `sql_commands/db_script.sql`: database/table notes
- `Dockerfile`, `deploy.sh`: Cloud Run container + deploy commands
- `stockfish_20011801_x64`: bundled Stockfish binary

## Requirements

- Python 3.8
- MySQL (Cloud SQL)

Install deps:

```bash
pip install -r requirements.txt
```

## Configuration

The app expects Cloud SQL via a Unix socket. Set these environment variables:

- `DB_USER`
- `DB_PASS`
- `DB_NAME`
- `CLOUD_SQL_CONN` (e.g. `PROJECT:REGION:INSTANCE`)
- `DB_SOCKET_DIR` (optional, default `/cloudsql`)
- `PORT` (for gunicorn, e.g. `8080`)

## API

### POST `/api/v1/assistant`

Dialogflow webhook handler. The request must include:

- `queryResult.action`
- `queryResult.parameters`
- `session`

Supported actions:

- `CreateGame`: starts a new game
- `MakeMove`: applies a user move, then plays Stockfish response
- `RevertMove`: reverts last two plies
- `ResignGame`: deletes the session row
- `ShowValidMoves`: lists legal moves

Parameters used:

- `Color`: `white` | `black` | `random`
- `Level`: 1-10 (Stockfish strength)
- `ChessPiece`: `N`, `B`, `R`, `Q`, `K` or empty for pawn
- `Moves`: move tokens (single square or [from,to])
- `Specialmoves`: `short_castle` | `long_castle`

Responses are Dialogflow `fulfillmentText` strings.

## Database

The `game` table stores:

- `session_url`
- `board` (pickled chess.Board)
- `player_color`
- `engine_level`

See `sql_commands/db_script.sql` for a starter schema.

## Deployment (Cloud Run)

Build and deploy using the included script:

```bash
./deploy.sh
```

This script expects Google Cloud credentials, a Cloud Run service, and Cloud SQL instance/secrets wired as shown in `deploy.sh`.
