from clients.models import Client
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import User, Group
from django.db import models
from hotels.models import Country, City, Hotel, RoomType, FeedingType
from ordered_model.models import OrderedModel
from stuff.models import Organization


class Agreement(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, db_column='organization',
                                     verbose_name='Организация')
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='agent', blank=True,
                              null=True,
                              verbose_name='Агент')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, db_column='client', verbose_name='Клиент')
    country = models.ForeignKey(Country, on_delete=models.CASCADE, db_column='country', verbose_name='Страна',
                                default=1)
    cities = models.ManyToManyField(City, through='TourPoint', verbose_name='Города')
    creation_date = models.DateTimeField('Дата заключения', auto_now_add=True)
    trip_start = models.DateField('Дата начала поездки')
    trip_end = models.DateField('Дата конца поездки')

    def __str__(self):
        template = 'Предварительное соглашение №{0.id}'
        return template.format(self)

    class Meta:
        verbose_name = 'Предварительное Соглашение'
        verbose_name_plural = 'Предварительные Соглашения'


class TourPoint(OrderedModel):
    agreement = models.ForeignKey(Agreement, on_delete=models.CASCADE, db_column='agreement',
                                  verbose_name='Предварительно соглашение')
    city = models.ForeignKey(City, on_delete=models.CASCADE, db_column='city', verbose_name='Отель')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, db_column='hotel', verbose_name='Отель', blank=True,
                              null=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, db_column='room_type', verbose_name='Тип комнаты',
                                  blank=True, null=True)
    feeding_type = models.ForeignKey(FeedingType, on_delete=models.CASCADE, db_column='feeding_type',
                                     verbose_name='Тип питания', blank=True, null=True)
    order = models.PositiveIntegerField('Порядок')
    start_date = models.DateTimeField('Дата заселения', blank=True, null=True)
    end_date = models.DateTimeField('Дата выселения', blank=True, null=True)

    order_with_respect_to = 'agreement'
    order_field_name = 'order'

    class Meta:
        ordering = ('order',)


class Bill(models.Model):
    creation_date = models.DateTimeField('Дата выписки', auto_now_add=True)
    cost = models.DecimalField('Стоимость', max_digits=10, decimal_places=2)
    payed = models.IntegerField('Оплачено')
    payment_date = models.DateTimeField('Дата платежа', blank=True, null=True)

    def __str__(self):
        template = 'Чек №{0.id}'
        return template.format(self)

    class Meta:
        verbose_name = 'Чек'
        verbose_name_plural = 'Чеки'


class Currency(models.Model):
    name = models.CharField('Наименование', max_length=45)
    code = models.CharField('Код', max_length=3)
    rate = models.DecimalField('Курс', max_digits=5, decimal_places=2)
    update_date = models.DateTimeField('Дата последнего изменения', auto_now=True)

    def __str__(self):
        template = '{0.name}'
        return template.format(self)

    class Meta:
        verbose_name = 'Валюта'
        verbose_name_plural = 'Валюты'


class Contract(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, db_column='currency', verbose_name='Валюта')
    creation_date = models.DateTimeField('Дата создания', auto_now_add=True)
    cost = models.DecimalField('Стоимость', max_digits=9, decimal_places=2)

    def __str__(self):
        template = 'Договор №{0.id} от {0.creation_date}'
        return template.format(self)

    class Meta:
        verbose_name = 'Договор'
        verbose_name_plural = 'Договоры'


class Tourist(models.Model):
    contract = models.OneToOneField(Contract, models.CASCADE, db_column='contract', primary_key=True,
                                    verbose_name='Договор')
    client = models.ForeignKey(Client, models.CASCADE, db_column='client', verbose_name='Клиент')

    class Meta:
        unique_together = (('contract', 'client'),)
        verbose_name = 'Турист'
        verbose_name_plural = 'Туристы'


class ProcessStatus(models.Model):
    name = models.CharField('Название', max_length=45)
    description = models.CharField('Описание', max_length=255, blank=True, null=True)

    def __str__(self):
        template = '{0.name}'
        return template.format(self)

    class Meta:
        verbose_name = 'Статус Процесса'
        verbose_name_plural = 'Статусы Процесса'


class BusinessProcess(models.Model):
    agreement = models.ForeignKey(Agreement, on_delete=models.CASCADE, db_column='agreement',
                                  verbose_name="Предварительное соглашение")
    status = models.ForeignKey(ProcessStatus, models.CASCADE, db_column='status', verbose_name="Статус")
    contract = models.ForeignKey(Contract, models.CASCADE, db_column='contract', blank=True, null=True,
                                 verbose_name="Договор")
    bill = models.ForeignKey(Bill, models.CASCADE, db_column='bill', blank=True, null=True, verbose_name="Чек")
    name = models.CharField('Название', max_length=45)
    creation_date = models.DateTimeField('Дата создания', auto_now_add=True)
    update_date = models.DateTimeField('Дата последнего изменения', auto_now=True)

    def __str__(self):
        template = 'Бизнес процесс {0.name}'
        return template.format(self)

    class Meta:
        unique_together = (('id', 'agreement', 'status'),)
        verbose_name = 'Бизнес процесс'
        verbose_name_plural = 'Бизнес процессы'
