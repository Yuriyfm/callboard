from django.contrib import admin
import datetime

from .forms import SubRubricForm
from .models import AdvUser, SuperRubric, SubRubric, AdditionalImage, Ad
from .utilities import send_activation_notification


def send_activation_notifications(modeladmin, request, queryset):
    for rec in queryset:
        if not rec.is_activated:
            send_activation_notification(rec)
    modeladmin.message_user(request, 'Письма с напоминаниями отправлены')
send_activation_notification.short_description = 'Отправка писем с напоминанием о необходимости активации'


class NonactivatedFilter(admin.SimpleListFilter):
    title = 'Активированные и неактивированные профили'
    parameter_name = 'actstate'

    def lookups(self, request, model_admin):
        return (
            ('activated', 'Прошли'),
            ('threedays', 'Не прошли, зарегистрированы более 3 дней'),
            ('week', 'Не прошли, зарегистрированы более недели'),
        )

    def queryset(self, request, queryset):
        val = self.value()
        if val == 'activated':
            return queryset.filter(is_active=True, is_activated=True)
        elif val == 'threedays':
            d = datetime.date.today() - datetime.timedelta(days=3)
            return queryset.filter(is_active=False, is_activated=False, date_joined_date_it=d)


class AdvUserAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_activated', 'date_joined') #__str__ - указывает выводить строковое представление записи как указано в методе модели.
    search_fields = ('username', 'email', 'first_name', 'last_name') #поля для фильтрации
    list_filter = (NonactivatedFilter,) #фильтрация пользователей не активировавшихся за 3 дня и неделю
    fields = (('username', 'email'), ('first_name', 'last_name'),
              ('send_messages', 'is_active', 'is_activated'),
              ('is_staff', 'is_superuser'),
              'groups', 'user_permissions',
              ('last_login', 'date_joined'))
    readonly_fields = ('last_login', 'date_joined')
    actions = (send_activation_notification,) #рассылка напоминаний неактивировавшимся пользователям


class SubRubricInline(admin.TabularInline): # с помощью TabularInline две связанные модели можно поместить на одну
    # страницу для редактирования
    model = SubRubric


class SuperRubricAdmin(admin.ModelAdmin):
    exclude = ('super_rubric',) # убирает поле выбора надрубрики из формы создания надрубрик
    inlines = (SubRubricInline,) #inlines добавляет поля модели SubRubric через TabularInline


class SubRubricAdmin(admin.ModelAdmin):
    form = SubRubricForm


class AdditionalImageInline(admin.TabularInline):
    model = AdditionalImage


class AdAdmin(admin.ModelAdmin):
    list_display = ('rubric', 'title', 'author', 'created_at')
    fields = (('rubric', 'author'), 'title', 'content', 'price', #'rubric' и 'author' вывели в одну строку для удобства.
              'contacts', 'image', 'is_active')
    inlines = (AdditionalImageInline,)


admin.site.register(AdvUser, AdvUserAdmin)
admin.site.register(SuperRubric, SuperRubricAdmin)
admin.site.register(SubRubric, SubRubricAdmin)
admin.site.register(Ad, AdAdmin)
