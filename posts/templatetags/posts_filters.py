from django import template


register = template.Library()


@register.filter
def ending(count):
	if count % 10 == 1 and count % 100 != 11:
		end = '0'
	elif 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
		end = '1'
	else:
		end = '2'
	return end
