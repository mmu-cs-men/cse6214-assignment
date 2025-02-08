from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard(request):
    """
    Dummy Seller Dashboard view.
    This placeholder view displays a message that the dashboard is under construction.
    """
    return render(request, "seller/dashboard.html")
