from django import template

register = template.Library()

@register.filter
def average_stars(reviews):
    total_stars = sum(review.stars for review in reviews)
    if len(reviews) == 0:
        return 0
    return total_stars / len(reviews)

@register.filter
def cart_total(cart):
    return sum(float(item['price']) for item in cart.values())