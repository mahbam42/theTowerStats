# Public APIs

This page is **Developer Documentation**. It describes the supported JSON endpoints used by the app UI.

> **Note**
> theTowerStats does not provide a public, third-party API. Endpoints listed here are read-only and scoped to the authenticated player session.

## Authentication and scope

- All endpoints return data for the current session and player.
- Endpoints marked **Authenticated** require a logged-in session.
- Responses never include cross-player data.

## Endpoints

### `GET /api/search/`

**Purpose**
Return typeahead results for global search.

**Authentication**
Optional. When not authenticated, results may be empty or limited.

**Query parameters**
- `q` (string, required): The search text.

**Response**
- `query` (string): Echoes the search text.
- `results` (array): Each item includes `title`, `subtitle`, `url`, and `external`.

---

### `GET /api/battle-report/<id>/`

**Purpose**
Return a Battle Report payload for the modal viewer.

**Authentication**
Authenticated. Requests are scoped to the current player.

**Path parameters**
- `id` (integer, required): Battle Report id.

**Response**
- `ok` (boolean)
- `report` (object)
  - `id` (integer)
  - `run_number` (integer or null)
  - `raw_text` (string)
  - `battle_date` (ISO string or null)
  - `battle_date_fallback` (boolean)
  - `parsed_at` (ISO string or null)
  - `tier` (integer or null)
  - `is_tournament` (boolean)
  - `tournament_rank` (string or null)
  - `metrics` (array): Metric label/value/unit entries for the modal
- Error responses return `{ ok: false, error: "..." }` with 404 or 405 status.

---

### `GET /api/explore/autocomplete/`

**Purpose**
Return Explore DSL autocomplete tokens.

**Authentication**
Authenticated. Scoped to the current player.

**Response**
- `ok` (boolean)
- `autocomplete` (object)
  - `keywords` (array)
  - `metrics` (array)
  - `breakdowns` (array)
  - `presets` (array)
- `validation` (object): Empty when no DSL input is supplied

---

### `POST /api/explore/autocomplete/`

**Purpose**
Return Explore DSL autocomplete tokens and validate DSL input.

**Authentication**
Authenticated. Scoped to the current player.

**Body parameters**
- `dsl` (string, required): DSL text to validate.

**Response**
- `ok` (boolean)
- `autocomplete` (object)
- `validation` (object)
  - `errors` (array of strings)
  - `warnings` (array of strings)

## Stability notes

- Endpoints are intended for in-app usage only.
- Responses are read-only and player-scoped.
- Any changes will be documented here.
