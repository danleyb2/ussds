from django import template

register = template.Library()


@register.filter(name='stared_by')
def stared_by(company, user):
    # user_id = int(user.id) # get the user id

    return company.stargazer(user)
