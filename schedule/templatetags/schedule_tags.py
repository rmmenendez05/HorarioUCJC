from django import template

register = template.Library()


@register.filter
def dict_get(d, key):
    if not isinstance(d, dict):
        return []
    return d.get(key, [])
