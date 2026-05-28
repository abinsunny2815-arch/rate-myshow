from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary with a given key."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
