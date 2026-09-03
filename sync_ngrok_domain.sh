#!/bin/bash
# Re-points the local ILPD journal's ngrok DomainAlias at whatever
# hostname the currently-running ngrok tunnel has right now.
# Run this any time you (re)start ngrok.
set -e

JOURNAL_CODE="${1:-ilpd}"
CONTAINER="$(docker ps --filter "name=janeway-web" --format "{{.Names}}" | head -1)"

if [ -z "$CONTAINER" ]; then
    echo "No running janeway-web container found." >&2
    exit 1
fi

NGROK_HOST="$(curl -s http://127.0.0.1:4040/api/tunnels | python3 -c "
import json, sys
tunnels = json.load(sys.stdin)['tunnels']
https = [t['public_url'] for t in tunnels if t['public_url'].startswith('https://')]
print(https[0].replace('https://', '') if https else '')
")"

if [ -z "$NGROK_HOST" ]; then
    echo "Couldn't find a running ngrok tunnel (is it started?)." >&2
    exit 1
fi

echo "ngrok host: $NGROK_HOST"

docker exec -w /vol/janeway "$CONTAINER" python src/manage.py shell -c "
from core.models import DomainAlias
from journal.models import Journal

journal = Journal.objects.get(code='$JOURNAL_CODE')
alias, created = DomainAlias.objects.update_or_create(
    journal=journal,
    defaults={'domain': '$NGROK_HOST', 'redirect': False},
)
print(('created' if created else 'updated') + ' -> ' + alias.domain)
"
