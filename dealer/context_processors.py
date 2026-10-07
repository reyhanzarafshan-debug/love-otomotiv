from .models import DealerProfile


def dealer_nav(request):
    """Makes is_dealer available in templates when user is an approved dealer."""
    if not request.user.is_authenticated:
        return {"is_dealer": False}
    return {
        "is_dealer": DealerProfile.objects.filter(
            user=request.user, is_approved=True
        ).exists(),
    }
