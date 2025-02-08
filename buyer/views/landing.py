from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from core.models import User
from core.models.book_listing import BookListing
from core.utils.decorators import allowed_roles


@login_required
@allowed_roles(["buyer"])
def landing_page(request):
    """
    Renders the Buyer Landing Page with all available books.

    This view retrieves all books that are not bought and displays them in a grid format.

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :return: Rendered landing page with books context.
    :rtype: django.http.HttpResponse
    """
    # Get the logged-in user based on email authentication
    current_user = request.user

    authenticated_user = User.objects.get(email=current_user.email)

    search_query = request.GET.get("q", "").strip()  # Get search term from URL

    # Filter books to only show those that are NOT bought
    if search_query:
        books = BookListing.objects.filter(title__icontains=search_query, bought=False)
    else:
        books = BookListing.objects.filter(bought=False)

    return render(request, "buyer/landing.html", {"books": books})
