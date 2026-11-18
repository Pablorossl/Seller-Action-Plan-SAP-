def no_client_ip(request):
    """Los bloqueos usan username; no almacenar IP ni confiar en X-Forwarded-For."""
    return None


def session_exception_handler(exc, context):
    from rest_framework.exceptions import NotAuthenticated
    from rest_framework.views import exception_handler

    response = exception_handler(exc, context)
    if response is not None and isinstance(exc, NotAuthenticated):
        response["X-SAP-Session"] = "expired"
    return response
