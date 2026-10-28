def no_client_ip(request):
    """Los bloqueos usan username; no almacenar IP ni confiar en X-Forwarded-For."""
    return None
