from django import template

register = template.Library()

@register.filter
def bootstrap_alert_class(message_tag):
    """Maps Django message tags to Bootstrap alert classes"""
    tag_map = {
        'debug': 'info',
        'info': 'info',
        'success': 'success',
        'warning': 'warning',
        'error': 'danger'
    }
    return f"alert-{tag_map.get(message_tag, 'info')}"