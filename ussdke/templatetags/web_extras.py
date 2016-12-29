from django import template

register = template.Library()


@register.filter(name='stared_by')
def stared_by(company, user):
    # user_id = int(user.id) # get the user id
    if not user.is_authenticated():
        return 0

    return company.stargazer(user)
