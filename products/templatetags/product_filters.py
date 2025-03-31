from django import template

register = template.Library()

@register.filter(name='get_attribute')
def get_attribute(queryset, attribute):
    """Extract attribute values from queryset items"""
    return [getattr(item, attribute) for item in queryset]

@register.filter(name='contains')
def contains(users_list, user):
    """Check if user is in the list"""
    return user in users_list
