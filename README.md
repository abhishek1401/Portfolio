# User Dashboard

Full-stack user profile dashboard with a Python backend, React TypeScript frontend, file-system storage, public profile URLs, image uploads, and admin editing.

## Run Production Locally

```powershell
cd frontend
npm.cmd install
npm.cmd run build
cd ..
python server.py
```

Open:

- Default public profile: `http://127.0.0.1:8000/public`
- Public profile URL example: `http://127.0.0.1:8000/profile/avery-stone`
- Admin dashboard: `http://127.0.0.1:8000/admin`

Default admin login:

- Username: `admin`
- Password: `admin123`

## Development

Run the backend:

```powershell
python server.py
```

Run the React TypeScript dev server:

```powershell
cd frontend
npm.cmd run dev
```

Vite proxies `/api` calls to the Python backend at `http://127.0.0.1:8000`.

## Project Structure

```text
.
|-- backend/
|   `-- app/
|       |-- config.py
|       |-- defaults.py
|       |-- domain/
|       |-- services/
|       |-- storage/
|       `-- web/
|-- cfg/
|   |-- auth.json
|   |-- profile_images/
|   |-- profiles/
|   |   |-- index.json
|   |   `-- avery-stone.json
|   `-- user_dashboard.json
|-- frontend/
|   |-- public/
|   |-- src/
|   |   |-- api/
|   |   |-- components/
|   |   |-- features/
|   |   |-- types/
|   |   `-- utils/
|   |-- package.json
|   `-- vite.config.ts
`-- server.py
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the layer responsibilities.

## Storage

The app uses files under `cfg` as a simple file-system database:

- `cfg/auth.json` stores the admin username, password salt, and password hash.
- `cfg/profiles/index.json` stores profile registry metadata.
- `cfg/profiles/{slug}.json` stores one public profile per file.
- `cfg/profile_images/{slug}/` stores uploaded profile images.
- `cfg/user_dashboard.json` is kept as legacy seed data for first-time migration.

Admin changes are saved directly into each profile's JSON file.

## API

- `GET /api/public` returns the default public profile dashboard.
- `GET /api/public/profiles/{slug}` returns one public profile.
- `POST /api/admin/login` returns an admin session token.
- `GET /api/admin/profiles` returns all profile summaries for authenticated admins.
- `POST /api/admin/profiles` creates a profile.
- `GET /api/admin/profiles/{slug}` returns one profile for editing.
- `PUT /api/admin/profiles/{slug}` saves one profile.
- `DELETE /api/admin/profiles/{slug}` deletes one profile.
- `POST /api/admin/profiles/{slug}/image` uploads a profile image.
- `POST /api/admin/logout` clears the current admin session.
- `GET /api/health` checks server health.

## Change The Admin Password

Generate a new hash with the same salt:

```powershell
python -c "import hashlib; print(hashlib.sha256(('local-dashboard-salt-v1' + 'new-password').encode()).hexdigest())"
```

Then replace `passwordHash` in `cfg/auth.json`.
