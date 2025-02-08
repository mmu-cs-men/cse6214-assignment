from django import template

register = template.Library()


@register.filter
def replace_underscores(value):
    """Replaces underscores with spaces in status text"""
    if isinstance(value, str):
        return value.replace("_", " ")
    return value
