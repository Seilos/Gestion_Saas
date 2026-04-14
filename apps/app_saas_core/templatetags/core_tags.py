from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if dictionary:
        return dictionary.get(str(key))
    return None

@register.filter
def remaining_days(date):
    if not date:
        return None
    from django.utils import timezone
    delta = date - timezone.now()
    return delta.days

@register.filter
def absolute(value):
    try:
        return abs(int(value))
    except (ValueError, TypeError):
        return value
