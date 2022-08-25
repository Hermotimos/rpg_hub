from django.conf import settings


def gcp_project_url(request):
    """
    Create custom context processor:
    # https://docs.djangoproject.com/en/4.0/ref/templates/api/#writing-your-own-context-processors
    
    Adds MY_GCP_PROJECT_URL variable accessible in all templates.
    Requires pointing to this function in settings.TEMPLATES.OPTIONS.context_processors:
     'technicalities.utils.gcp_project_url'.
     
    """
    return {
        "MY_GCP_PROJECT_URL": settings.MY_GCP_PROJECT_URL,
    }
