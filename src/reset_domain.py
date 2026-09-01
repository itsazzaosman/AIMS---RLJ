from django.contrib.sites.models import Site
from core.models import Press

new_domain = 'localhost:8000'

for site in Site.objects.all():
    site.domain = new_domain
    site.save()

for press in Press.objects.all():
    press.domain = new_domain
    press.save()

print('Updated site and press domain to', new_domain)
