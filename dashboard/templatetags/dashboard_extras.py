from django import template

register = template.Library()


@register.filter
def dashattr(obj, path):
    """Resolve a dotted attribute path on ``obj`` for the generic list table.

    Calls any callables found along the way (so ``get_type_display`` works).
    Returns "" for missing attributes.
    """
    for part in path.split("."):
        if obj is None:
            return ""
        obj = getattr(obj, part, "")
        if callable(obj):
            obj = obj()
    return obj
