from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def split_by_newline(value):
    rows = value.split('\n')
    table = '<table class="table table-striped table-bordered">\n'
    for row in rows:
        table += f'<tr>{row}</tr>\n'
    table += '</table>'
    return mark_safe(table)



@register.filter
def split_by_comma(value):
    return value.split(',')