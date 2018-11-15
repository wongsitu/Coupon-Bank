from django.conf import settings

def global_settings(request):
    return {
        'GOOGLE_TRACKING_ID': settings.GOOGLE_TRACKING_ID
    }
