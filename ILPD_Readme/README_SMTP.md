
cat << 'EOF' > ~/AIMS---RLJ/README_SMTP.md
# Janeway cPanel SMTP Integration Guide

This guide explains how email delivery is configured, how Docker manages SMTP credentials, and how to test or troubleshoot email delivery for **Janeway** hosted with cPanel.

---

## 1. System Architecture & Email Flow

When Janeway triggers an email (e.g., password resets, submission updates, peer-review invitations):

1. **Django Mail Backend:** Intercepts the request and formats the email using `django.core.mail`.
2. **TLS Handshake:** Connects to cPanel's Exim mail server (`journal.insozi.rw`) over **Port 587** using **STARTTLS**.
3. **Authentication:** Authenticates with the full email username (`journal@journal.insozi.rw`) and its password.
4. **Delivery:** cPanel queues and sends the message to the recipient's mail provider.

---

## 2. Environment Variables Configuration (`.env`)

Email settings are injected into the Docker container dynamically via the project's root `.env` file.

**File Location:** `~/AIMS---RLJ/.env`

```env
# Email Backend & Server Configuration
JANEWAY_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
JANEWAY_EMAIL_HOST=journal.insozi.rw
JANEWAY_EMAIL_PORT=587

# Authentication Credentials
JANEWAY_EMAIL_HOST_USER=journal@journal.insozi.rw
JANEWAY_EMAIL_HOST_PASSWORD='Aims@2026'

# Security & Protocols
JANEWAY_EMAIL_USE_SSL=False
JANEWAY_EMAIL_USE_TLS=True

# Default Sender Identity
DEFAULT_FROM_EMAIL=journal@journal.insozi.rw

```

> **Important:** If your password contains special characters (e.g., `@`, `#`, `!`, `$`), wrap it in single quotes (`'...'`) so Bash/Docker interprets it correctly.

---

## 3. Docker Service Injection (`docker-compose.yml`)

The `docker-compose.yml` file passes these `.env` variables directly to the `janeway-web` container runtime.

**File Location:** `~/AIMS---RLJ/docker-compose.yml`

```yaml
services:
  janeway-web:
    # ... container definitions ...
    environment:
      - DB_VENDOR
      - DB_HOST
      - DB_PORT
      - DB_PASSWORD
      - DB_USER
      - DB_NAME
      - PYTHONDONTWRITEBYTECODE=yes
      - JANEWAY_SETTINGS_MODULE
      - JANEWAY_SETTINGS_FILE
      - NOSE_INCLUDE_EXE=1
      - JANEWAY_EMAIL_BACKEND
      - JANEWAY_EMAIL_HOST
      - JANEWAY_EMAIL_PORT
      - JANEWAY_EMAIL_HOST_USER
      - JANEWAY_EMAIL_HOST_PASSWORD
      - JANEWAY_EMAIL_USE_SSL
      - JANEWAY_EMAIL_USE_TLS
      - DEFAULT_FROM_EMAIL

```

---

## 4. Janeway Global Settings Mapping

Janeway reads the environment variables into Django settings inside `janeway_global_settings.py`.

**File Location:** `~/AIMS---RLJ/src/core/janeway_global_settings.py`

```python
EMAIL_BACKEND = os.environ.get("JANEWAY_EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = os.environ.get("JANEWAY_EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("JANEWAY_EMAIL_PORT", 587))
EMAIL_HOST_USER = os.environ.get("JANEWAY_EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("JANEWAY_EMAIL_HOST_PASSWORD", "")
EMAIL_USE_SSL = os.environ.get("JANEWAY_EMAIL_USE_SSL", "False") == "True"
EMAIL_USE_TLS = os.environ.get("JANEWAY_EMAIL_USE_TLS", "True") == "True"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

```

---

## 5. How to Test & Verify Email Delivery

### Method 1: One-Line CLI Test Command

Run this command directly in your server terminal:

```bash
docker exec -it aims---rlj-janeway-web-1 python src/manage.py shell -c "
from django.core.mail import send_mail

result = send_mail(
    'Janeway Production SMTP Test',
    'Hello! This is a live test email sent from Janeway via cPanel SMTP.',
    'journal@journal.insozi.rw',
    ['test@insozi.rw'],
    fail_silently=False,
)
print('Email Sent Status:', result)
"

```

* **Output `1`:** Success! The email was handed off to cPanel and delivered.
* **Traceback / Error:** Check credentials or network connectivity.

---

### Method 2: Interactive Django Shell

1. Enter the container's Django shell:
```bash
docker exec -it aims---rlj-janeway-web-1 python src/manage.py shell

```


2. Execute the test snippet:
```python
from django.core.mail import send_mail

send_mail(
    'Janeway System Check',
    'SMTP configuration verified successfully.',
    'journal@journal.insozi.rw',
    ['test@insozi.rw'],
    fail_silently=False,
)

```



---

## 6. Maintenance & Deployment Steps

If you ever change the SMTP password or server settings in the future:

1. Open `.env` and update the values:
```bash
nano ~/AIMS---RLJ/.env

```


2. Restart the Docker container to apply changes:
```bash
docker compose down && docker compose up -d

```


3. Run the one-line test command to confirm delivery.
EOF

cd ~/AIMS---RLJ
git add README_SMTP.md docker-compose.yml src/core/janeway_global_settings.py
git commit -m "docs: add cPanel SMTP integration guide and updated mail configuration"
git push origin docker-deployment

```

```