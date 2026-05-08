# Architecture

This project uses a layered full-stack structure so the UI, HTTP routing, business rules, media handling, and persistence are not mixed together.

## Backend

```text
backend/app/
|-- config.py                 # Paths, host, port, and runtime settings
|-- defaults.py               # Seed data for cfg files
|-- domain/
|   `-- dashboard.py          # Dashboard validation and sanitization
|-- services/
|   |-- auth_service.py       # Admin login, logout, session validation
|   |-- media_service.py      # Uploaded profile image storage
|   `-- profile_service.py    # Profile CRUD and cfg file registry
|-- storage/
|   `-- json_store.py         # File-system JSON persistence adapter
`-- web/
    |-- http_handler.py       # HTTP API routes and response handling
    `-- static_files.py       # Safe static asset serving
```

`server.py` is intentionally small. It only starts the composed backend application.

## Frontend

```text
frontend/src/
|-- api/                      # Typed API client
|-- components/               # Shared presentational components
|-- features/
|   |-- admin/                # Admin login and editor workflow
|   `-- public/               # Public dashboard experience
|-- types/                    # TypeScript domain types
|-- utils/                    # Shared helper functions
|-- App.tsx
|-- main.tsx
`-- styles.css
```

The frontend source language is TypeScript and TSX. Vite builds the production bundle into `frontend/dist`, which the Python backend serves.

## Access Model

- Public access can read `GET /api/public` and `GET /api/public/profiles/{slug}`.
- Public profile URLs use `/profile/{slug}`.
- Public pages do not link to the admin portal.
- Admin access starts with `POST /api/admin/login`.
- Admin-only routes require a bearer token in the `Authorization` header.
- Admin edits are validated by the backend before saving to `cfg/profiles/{slug}.json`.
- Uploaded profile images are saved under `cfg/profile_images/{slug}/` and served from `/media/profile-images/{slug}/{filename}`.

## Data Flow

```text
React TypeScript UI
  -> typed fetch client
  -> Python HTTP handler
  -> service layer
  -> JSON storage adapter
  -> cfg/profiles/*.json
```

Uploaded images follow a separate file path:

```text
Admin image upload
  -> multipart/form-data API
  -> media service
  -> cfg/profile_images/{slug}/
```
