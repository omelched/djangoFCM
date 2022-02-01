from django.conf import settings
from pyhcm import HCMNotification

hms_app = HCMNotification(
    client_id=settings.DJANGOFCM_HMS_CLIENT_ID,
    client_secret=settings.DJANGOFCM_HMS_SECRET,
    project_id=settings.DJANGOFCM_HMS_PROJECT_ID,
)
