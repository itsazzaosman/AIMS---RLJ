# AIMS---RLJ — Janeway Local Docker Setup

This guide explains how to run the Janeway-based Rwanda Law Journal platform locally using Docker and PostgreSQL.

## 1. Requirements

Install:

* Git
* Docker
* Docker Compose

Verify the installation:

```bash
git --version
docker --version
docker compose version
```

---

## 2. Clone the Repository

Clone the repository:

```bash
git clone https://github.com/itsazzaosman/AIMS---RLJ.git
```

Go to the project directory:

```bash
cd AIMS---RLJ
```

Switch to the `master` branch and get the latest changes:

```bash
git checkout master
git pull origin master
```

---

## 3. Configure Environment Variables

Check whether the `.env` file exists:

```bash
ls -la
```

If `.env` does not exist, create it:

```bash
nano .env
```

Add the following configuration:

```env
DB_VENDOR=postgres
DB_NAME=janeway
DB_USER=janeway-web
DB_PASSWORD=janeway-web
DB_HOST=janeway-postgres
DB_PORT=5432

JANEWAY_SETTINGS_FILE=src/core/settings.py
JANEWAY_PORT=8010
PGADMIN_PORT=8011
```

Save the file.

Verify the Docker Compose configuration:

```bash
docker compose config
```

The command should complete without configuration errors.

---

## 4. Build and Start Janeway

From the project root, run:

```bash
docker compose up -d --build
```

The first build may take several minutes because Docker needs to download and install the required dependencies.

---

## 5. Check the Containers

Run:

```bash
docker compose ps
```

You should see these services running:

```text
janeway-web
janeway-postgres
janeway-pgadmin
janeway-debug-smtp
```

The `janeway-web` service should expose:

```text
0.0.0.0:8010->8000/tcp
```

---

## 6. Initialize the Database

For a new installation, run:

```bash
make install
```

Then run migrations:

```bash
make migrate
```

---

## 7. Open Janeway

Open your browser:

```text
http://localhost:8010
```

If the RLJ path is enabled, use:

```text
http://localhost:8010/RLJ/
```

---

## 8. Open pgAdmin

pgAdmin is available at:

```text
http://localhost:8011
```

Development credentials:

```text
Email: dev@janeway.systems
Password: janeway-web
```

---

## 9. Useful Commands

### Start the application

```bash
docker compose up -d
```

### Stop the application

```bash
docker compose down
```

### Check containers

```bash
docker compose ps
```

### View Janeway logs

```bash
docker compose logs -f janeway-web
```

### View PostgreSQL logs

```bash
docker compose logs -f janeway-postgres
```

### Open a shell inside the Janeway container

```bash
docker compose exec janeway-web bash
```

### Run Django commands

```bash
make command CMD="migrate"
```

### Run database migrations

```bash
make migrate
```

### Run tests

```bash
make check
```

---

## 10. Rebuild the Application

If Docker configuration or the Dockerfile has changed:

```bash
docker compose down
docker compose up -d --build
```

Do not delete the PostgreSQL data directory unless you intentionally want to start with a completely new database.

---

## 11. Troubleshooting

Check the status of all containers:

```bash
docker compose ps
```

View Janeway logs:

```bash
docker compose logs janeway-web
```

View PostgreSQL logs:

```bash
docker compose logs janeway-postgres
```

View all logs:

```bash
docker compose logs
```

---

## Quick Setup

For a fresh setup, the main commands are:

```bash
git clone https://github.com/itsazzaosman/AIMS---RLJ.git
cd AIMS---RLJ
git checkout master
git pull origin master
```

Create `.env`, then:

```bash
docker compose config
docker compose up -d --build
docker compose ps
make install
make migrate
```

Then open:

```text
http://localhost:8010
```
