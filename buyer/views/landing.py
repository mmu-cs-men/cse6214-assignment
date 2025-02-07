from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from core.models.book_listing import BookListing


@login_required
def landing_page(request):
    """
    Renders the Buyer Landing Page with all available books.

    This view retrieves all books listed for sale and displays them in a grid format.

    :param request: The HTTP request object.
    :type request: django.http.HttpRequest
    :return: Rendered landing page with books context.
    :rtype: django.http.HttpResponse
    """
    # Get the logged-in user
    current_user = request.user

    # Retrieve all books from the database
    books = BookListing.objects.all()

    context = {
        "books": books
    }

    return render(request, "buyer/landing.html", context)
