from django.shortcuts import render


def landing_page(request):
    """
    Temporary placeholder for the Buyer Landing page.
    This view does nothing and will be replaced later.
    """
    return render(request, "buyer/landing.html")
