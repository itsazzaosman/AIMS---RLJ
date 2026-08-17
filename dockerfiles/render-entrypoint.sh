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

exec python src/manage.py runserver --insecure "0.0.0.0:${PORT:-8000}"
