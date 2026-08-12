from cms.models import Page
from django.contrib.contenttypes.models import ContentType
from journal.models import Journal

j = Journal.objects.first()
if j:
    ct = ContentType.objects.get_for_model(j)
    Page.objects.get_or_create(
        content_type=ct,
        object_id=j.id,
        name='privacy',
        defaults={
            'display_name': 'Privacy Policy',
            'content': '<p>This is the privacy policy.</p>'
        }
    )
    print('Privacy Policy page created for Journal.')
else:
    print('No journal found.')
