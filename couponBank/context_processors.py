from django.conf import settings

def global_settings(request):
    return {
        'GOOGLE_TRACKING_ID': settings.GOOGLE_TRACKING_ID,
        'GOOGLE_MAPS_API': settings.GOOGLE_MAPS_API
    }
