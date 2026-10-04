def current_org(request):
    return {
        "current_org": getattr(request, "organization", None),
        "current_membership": getattr(request, "membership", None),
    }
