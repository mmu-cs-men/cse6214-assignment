from django import template

register = template.Library()


@register.filter
def replace_underscores(value):
    """Replaces underscores with spaces in status text"""
    if isinstance(value, str):
        return value.replace("_", " ")
    return value


@register.filter
def mul(value, arg):
    """Multiplies the given value by an argument and returns the result as a float."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ""


@register.filter
def div(value, arg):
    """Divides the given value by an argument and returns the result as a float."""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return ""
