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

# Press.domain (and, for a single-journal site, Journal.domain) are DB
# fields set once by install_janeway/data import and never re-read
# afterwards. Keep them in sync with JANEWAY_PRESS_DOMAIN on every
# boot, since that env var can change (e.g. after Render assigns the
# real hostname, or after restoring a data dump from elsewhere) long
# after the row was created. Journal is matched before Press in
# core.middleware, so it needs the same domain to resolve directly
# to the journal's own homepage rather than falling through to the
# press's generic one.
if [ -n "$JANEWAY_PRESS_DOMAIN" ]; then
    python src/manage.py shell -c "
from press.models import Press
from journal.models import Journal

domain = '$JANEWAY_PRESS_DOMAIN'

press = Press.objects.first()
if press and press.domain != domain:
    print(f'Updating Press.domain: {press.domain!r} -> {domain!r}')
    press.domain = domain
    press.save()

journal = Journal.objects.first()
if journal and journal.domain != domain:
    print(f'Updating Journal.domain: {journal.domain!r} -> {domain!r}')
    journal.domain = domain
    journal.save()
"
fi

exec python src/manage.py runserver --insecure "0.0.0.0:${PORT:-8000}"
