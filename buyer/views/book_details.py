from django.shortcuts import get_object_or_404, render

from core.models import BookListing


def book_details_page(request, book_id):
    book = get_object_or_404(BookListing, id=book_id)
    return render(request, 'buyer/book_details.html', {'book': book})
