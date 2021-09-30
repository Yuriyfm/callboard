"""в данном файле хранятся обработчики контекста. по принятым
в Django соглашениям, весь код, "ответственный" за формирование страниц, следует
помещать в шаблон, посредник или обработчик контекста."""

from .models import SubRubric, Rubric


def callboard_context_processor(request):
    context = {}
    context['rubrics'] = SubRubric.objects.all()
    context['keyword'] = ''
    context['all'] = ''
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            context['keyword'] = '?keyword=' + keyword
            context['all'] = context['keyword']
    if 'page' in request.GET:
        page = request.GET['page']
        if page != '1':
            if context['all']:
                context['all'] += '&page=' + page
            else:
                context['all'] += '?page=' + page
    return context

