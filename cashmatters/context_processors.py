from blog.models import WhyCashMattersPage


def why_cash_page(request):
    """Add the WhyCashMattersPage to all template contexts"""
    page = WhyCashMattersPage.objects.live().filter(slug='why-cash').first()
    return {
        'why_cash_page': page,
    }
