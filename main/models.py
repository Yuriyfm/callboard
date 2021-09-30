from django.db import models
from django.contrib.auth.models import AbstractUser
from main.utilities import get_timestamp_path


class AdvUser(AbstractUser):
    is_activated = models.BooleanField(default=True, db_index=True,
                                       verbose_name='Прошел активацию')
    send_messages = models.BooleanField(default=True,
                                        verbose_name='Присылать оповещения о новых комментариях')

    def delete(self, *args, **kwargs): # при удалении пользователя, функция удалит все его записи
        for ad in self.ad_set.all():
            ad.delete()
        super().delete(*args, **kwargs)

    class Meta(AbstractUser.Meta):
        pass


class Rubric(models.Model): #модель для всех рубрик
    name = models.CharField(max_length=20, db_index=True, unique=True, verbose_name='Название')
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name='Порядок')
    super_rubric = models.ForeignKey('SuperRubric', on_delete=models.PROTECT, null=True, blank=True,
                                     verbose_name='Надрубрика')


class SuperRubricManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=True)


class SuperRubric(Rubric): #проски-модель. Только надрубрики.
    objects = SuperRubricManager()

    def __str__(self):
        return self.name

    class Meta:
        proxy = True
        ordering = ('order', 'name')
        verbose_name = "Надрубрика"
        verbose_name_plural = "Надрубрики"


class SubRubricManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=False)


class SubRubric(Rubric):
    objects = SubRubricManager()

    def __str__(self):
        return f'{self.super_rubric.name} - {self.name}'

    class Meta:
        proxy = True
        ordering = ('super_rubric__order', 'super_rubric__name', 'order', 'name')
        verbose_name = "Подрубрика"
        verbose_name_plural = "Подрубрики"


class Ad(models.Model):
    rubric = models.ForeignKey(SubRubric, on_delete=models.PROTECT, verbose_name='Рубрика')
    title = models.CharField(max_length=40, verbose_name="Товар")
    content = models.TextField(verbose_name="Описание")
    price = models.FloatField(default=0, verbose_name='Цена')
    contacts = models.TextField(verbose_name='Контакты')
    image = models.ImageField(blank=True, upload_to=get_timestamp_path, verbose_name='Изображение')
    author = models.ForeignKey(AdvUser, on_delete=models.CASCADE, verbose_name='Автор объявления')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Выводить в списке?')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано')

    def delete(self, *args, **kwargs):
        '''В переопределенном методе delete () перед удалением текущей записи мы перебираем
        и вызовом метода delete () удаляем все связанные дополнительные иллюстрации.
        При вызове метода delete () возникает сигнал post delete, обрабатываемый
        приложением django cieanup, которое в ответ удалит все файлы, хранящиеся
        в удаленной записи.'''
        for ai in self.additionalimage_set.all():
            ai.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Объявления'
        verbose_name = 'Объявление'
        ordering = ['-created_at']


class AdditionalImage(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, verbose_name='Объявление')
    image = models.ImageField(upload_to=get_timestamp_path, verbose_name='Изображение')

    class Meta:
        verbose_name = "Дополнительная иллюстрация"
        verbose_name_plural = 'Дополнительные иллюстрации'


class Comment(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, verbose_name='Объявление')
    author = models.CharField(max_length=30, verbose_name="Имя автора")
    content = models.TextField(verbose_name='Содержание')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name="Выводить на экран?")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликован')

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['created_at']
