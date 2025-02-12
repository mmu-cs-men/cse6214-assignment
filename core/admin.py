from django.contrib import admin
from django.utils import timezone
from admincharts.admin import AdminChartMixin
from admincharts.utils import months_between_dates
from decimal import Decimal
from core.models import *

# Change admin site title
admin.site.site_header = "booklab administration"
admin.site.site_title = "booklab administration"
admin.site.index_title = "booklab administration"

admin.site.register(UpgradeRequest)
admin.site.register(User)
admin.site.register(OrderAssignment)
admin.site.register(Review)
admin.site.register(Shop)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(DeliveryIssue)


@admin.register(Order)
class OrderAdmin(AdminChartMixin, admin.ModelAdmin):
    list_chart_type = "line"
    list_chart_options = {"aspectRatio": 6}

    def get_list_chart_data(self, queryset):
        if not queryset:
            return {}

        # Get the earliest order date
        earliest = min(order.placed_at for order in queryset)
        labels = []
        order_counts = []

        # Create a label and count for each month between earliest and now
        for month in months_between_dates(earliest, timezone.now()):
            labels.append(month.strftime("%b %Y"))
            monthly_count = sum(
                1
                for order in queryset
                if order.placed_at.year == month.year
                and order.placed_at.month == month.month
            )
            order_counts.append(monthly_count)

        return {
            "labels": labels,
            "datasets": [
                {
                    "label": "Orders per Month",
                    "data": order_counts,
                    "backgroundColor": "#79aec8",
                },
            ],
        }


@admin.register(OrderItem)
class OrderItemAdmin(AdminChartMixin, admin.ModelAdmin):
    list_chart_type = "bar"
    list_chart_options = {"aspectRatio": 6}

    def get_list_chart_data(self, queryset):
        if not queryset:
            return {}
        # Use the order's placed_at date for aggregation
        earliest = min(oi.order.placed_at for oi in queryset)
        labels = []
        revenue = []
        for month in months_between_dates(earliest, timezone.now()):
            labels.append(month.strftime("%b %Y"))
            monthly_revenue = sum(
                (
                    oi.purchase_price * oi.quantity * Decimal("0.20")
                )  # Taking 20% of the total purchase price
                for oi in queryset
                if oi.order.placed_at.year == month.year
                and oi.order.placed_at.month == month.month
            )
            revenue.append(float(monthly_revenue))
        return {
            "labels": labels,
            "datasets": [
                {
                    "label": "Revenue per Month",
                    "data": revenue,
                    "backgroundColor": "#36A2EB",
                },
            ],
        }


@admin.register(BookListing)
class BookListingAdmin(AdminChartMixin, admin.ModelAdmin):
    list_chart_type = "pie"
    list_chart_options = {"aspectRatio": 6}

    def get_list_chart_data(self, queryset):
        if not queryset:
            return {}
        condition_counts = {}
        for listing in queryset:
            condition = listing.condition
            condition_counts[condition] = condition_counts.get(condition, 0) + 1
        labels = list(condition_counts.keys())
        counts = list(condition_counts.values())
        colors = ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"]
        return {
            "labels": labels,
            "datasets": [
                {
                    "label": "Book Listings by Condition",
                    "data": counts,
                    "backgroundColor": colors[: len(counts)],
                },
            ],
        }
