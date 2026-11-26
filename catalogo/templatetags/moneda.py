from django import template

from core.currency import format_cop


register = template.Library()
register.filter("cop", format_cop)
