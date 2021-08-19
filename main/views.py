from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.core.signing import BadSignature
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.http import HttpResponse, Http404
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView, TemplateView, DeleteView

from .models import AdvUser, SubRubric, Ad, Comment
from .forms import ChangeUserInfoForm, RegisterUserForm, SearchForm, AdForm, AIFormSet, UserCommentForm, \
    GuestCommentForm
from .utilities import signer


def index(request):
    ads = Ad.objects.filter(is_active=True)[:10]
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword)
        ads = ads.filter(q)
    else:
        keyword = ''
    form = SearchForm(initial={'keyword': keyword})
    paginator = Paginator(ads, 2)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {'page': page, 'ads': page.object_list, 'form': form}
    return render(request, 'main/index.html', context)


def by_rubric(request, pk):
    rubric = get_object_or_404(SubRubric, pk=pk)
    ads = Ad.objects.filter(is_active=True, rubric=pk)
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword)
        ads = ads.filter(q)
    else:
        keyword = ''
    form = SearchForm(initial={'keyword': keyword})
    paginator = Paginator(ads, 2)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {'rubric': rubric, 'page': page, 'ads': page.object_list, 'form': form}
    return render(request, 'main/by_rubric.html', context)


def detail(request, rubric_pk, pk):
    ad = get_object_or_404(Ad, pk=pk)
    ais = ad.additionalimage_set.all()
    comments = Comment.objects.filter(ad=pk, is_active=True)
    initial = {'ad': ad.pk}
    if request.user.is_authenticated:
        initial['author'] = request.user.username
        form_class = UserCommentForm
    else:
        form_class = GuestCommentForm
    form = form_class(initial=initial)
    if request.method == 'POST':
        c_form = form_class(request.POST)
        if c_form.is_valid():
            c_form.save()
            messages.add_message(request, messages.SUCCESS, 'Комментарий добавлен')
        else:
            form = c_form
            messages.add_message(request, messages.WARNING, 'Комментарий не добавлен')

    context = {'ad': ad, 'ais': ais, 'comments': comments, 'form': form}
    return render(request, 'main/detail.html', context)


def user_activate(request, sign):
    """Контоллер активации нового пользователя"""
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'main/bad_signature.html')
    user = get_object_or_404(AdvUser, username=username)
    if user.is_activated:
        template = 'main/user_is_activated.html'
    else:
        template = 'main/activation_done.html'
        user.is_active = True
        user.is_activated = True
    return render(request, template)


def other_page(request, page):
    try:
        template = get_template('main/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))


#Контроллеры просмотра редактирования и  удаления объявлений пользователя
@login_required
def profile(request):
    '''декоратор дает доступ к странице только авторизованным пользователям'''
    ads = Ad.objects.filter(author=request.user.pk)
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword)
        ads = ads.filter(q)
    else:
        keyword = ''
    form = SearchForm(initial={'keyword': keyword})
    paginator = Paginator(ads, 2)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {'page': page, 'ads': page.object_list, 'form': form}
    return render(request, 'main/profile.html', context)


@login_required
def profile_ad_detail(request, rubric_pk, pk):
    ad = get_object_or_404(Ad, pk=pk)
    ais = ad.additionalimage_set.all()
    context = {'ad': ad, 'ais': ais}
    return render(request, 'main/profile_ad_detail.html', context)


@login_required
def profile_ad_add(request):
    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES)
        if form.is_valid():
            ad = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=ad)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление добавлено')
                return redirect('main:profile')
    else:
        form = AdForm(initial={'author': request.user.pk})
        formset = AIFormSet()
    context = {'form': form, 'formset': formset}
    return render(request, 'main/profile_ad_add.html', context)


@login_required
def profile_ad_change(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES, instance=ad)
        if form.is_valid():
            ad = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=ad)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление изменено')
                return redirect('main:profile')
    else:
        form = AdForm(instance=ad)
        formset = AIFormSet(instance=ad)
    context = {'form': form, 'formset': formset}
    return render(request, 'main/profile_ad_change.html', context)


@login_required
def profile_ad_delete(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    if request.method == "POST":
        ad.delete()
        messages.add_message(request, messages.SUCCESS, 'Объявление удалено')
        return redirect('main:profile')
    else:
        context = {'ad': ad}
        return render(request, 'main/profile_ad_delete.html')


# class-based контроллеры для регистрации, редактирования личных данных и удаления профиля пользователя
class BBLoginView(LoginView):
    template_name = 'main/login.html'


class BBLogoutView(LogoutView, LoginRequiredMixin):
    '''Страница выхода должна быть доступна только зарегистрированным пользователям,
    выполнившим вход. Поэтому в число суперклассов добавили LoginRequiredMixin'''
    template_name = 'main/logout.html'

class BBPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    '''В качестве одного из суперклассов этого контроллера-класса мы указали примесь
LoginRequiredMixin, запрещающую доступ к контроллеру гостям, и примесь
SuccessMessageMixin, которая применяется для вывода всплывающих сообщений
об успешном выполнении операции.'''
    template_name = 'main/password_change.html'
    success_url = reverse_lazy('main:profile')
    success_message = "Ваш пароль был успешно изменен"


class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    """В процессе работы этот контроллер должен извлечь из модели AdvUser запись,
представляющую текущего пользователя, для чего ему нужно предварительно
получить ключ текущего пользователя. Получить его можно из объекта текущего
пользователя, хранящегося в атрибуте user объекта запроса.
В качестве одного из суперклассов этого контроллера-класса мы указали примесь
LoginRequiredMixin, запрещающую доступ к контроллеру гостям, и примесь
SuccessMessageMixin, которая применяется для вывода всплывающих сообщений
об успешном выполнении операции."""
    model = AdvUser
    template_name = 'main/change_user_info.html'
    form_class = ChangeUserInfoForm
    success_url = reverse_lazy('main:profile')
    success_message = "Ваши данные пользователя были изменены"

    def setup(self, request, *args, **kwargs):
        """Вероятно, наилучшее место для получения ключа текущего пользователя — метод
setup, наследуемый всеми контроллерами-классами от их общего суперкласса
view. Этот метод выполняется в самом начале исполнения контроллера-класса и
получает объект запроса в качестве одного из параметров. В переопределенном
методе setup () мы извлечем ключ пользователя и сохраним его в атрибуте user id."""
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        """Извлечение исправляемой записи выполняем в методе get object, который контроллер-
класс унаследовал от примеси singieobjectMixin. В переопределенном методе
сначала учитываем тот момент, что набор записей, из которого следует извлечь
искомую запись, может быть передан методу с параметром queryset, а может
быть и не передан — в этом случае набор записей следует получить вызовом метода
get queryset (). После этого непосредственно ищем запись, представляющую
текущего пользователя."""
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class RegisterUserView(CreateView):
    model = AdvUser
    template_name = 'main/register_user.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('main:register_done')


class RegisterDoneView(TemplateView):
    template_name = 'main/register_done.html'


class DeleteUserView(LoginRequiredMixin, DeleteView):
    """В переопределенном методе setup сохранили ключ текущего пользователя,
    а в переопределенном методе get object о отыскали
    по этому ключу пользователя, подлежащего удалению."""
    model = AdvUser
    template_name = 'main/delete_user.html'
    success_url = reverse_lazy('main:index')

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Пользователь удален')
        return super().post(request, *args, kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)

