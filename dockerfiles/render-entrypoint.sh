#!/bin/bash
set -e

python src/manage.py migrate --noinput

if ! python src/manage.py shell -c "
from journal.models import Journal
import sys
sys.exit(0 if Journal.objects.exists() else 1)
"; then
    echo "No journal found, running first-time install_janeway..."
    python src/manage.py install_janeway --use-defaults
fi

# Press.domain is a DB field set once by install_janeway and never
# re-read afterwards. Keep it in sync with JANEWAY_PRESS_DOMAIN on
# every boot, since that env var can change (e.g. after Render
# assigns the real hostname) long after the initial install.
if [ -n "$JANEWAY_PRESS_DOMAIN" ]; then
    python src/manage.py shell -c "
from press.models import Press
domain = '$JANEWAY_PRESS_DOMAIN'
press = Press.objects.first()
if press and press.domain != domain:
    print(f'Updating Press.domain: {press.domain!r} -> {domain!r}')
    press.domain = domain
    press.save()
"
fi

exec python src/manage.py runserver --insecure "0.0.0.0:${PORT:-8000}"
