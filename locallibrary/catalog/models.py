from django.db import models
from django.urls import reverse
import uuid
from django.contrib.auth.models import User
from datetime import date

class Genre(models.Model):
    name = models.CharField(max_length=200, help_text="Добавьте название жанра")
    # задаем шаблон таблицы name с ограничением в 200 элементов и текстом на полее вводе "Добавьте название жанра"

    def __str__(self):
        return self.name
    # данная функция позволит нам узнать наименование таблицы

class Book(models.Model):
    title = models.CharField(max_length=200)
    # объявление столбца таблицы с ограничем в 200 символов, charfield существует для обработки небольших текстовых данных

    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    # объявление столбца таблицы, первый аргумент это название столбца, on_delete объявляет о том что изначальное значение
    # стобца может иметь значение null а null с положительным значением позволяет сохрянять null значения в стобце
    # ForeighkEY берет айди элекмент и присваивает данный айди к элементу, это позволит благодаря одному лишь значению получить эффективную сортировку
    # например можно забить автора Лев Толстой, с привязкой к книгам война и мир и прочие, и благодаря лишь поиску по автору
    # позволит вывести все книги данного автора
    
    summary = models.TextField(max_length=1000, help_text='Введите краткое содержание')
    # новый аргумент help_text позволяет ввести подсказку о данном поле, textfield существует для обработки больших объёмов данных

    isbn = models.CharField('ISBN', max_length=13, help_text='Введите 13-значный ISBN код')

    genre = models.ManyToManyField(Genre, help_text='Выберите жанр')

    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("book_detail", kwargs={'pk': self.pk})
    
    def dislpay_genre(self):
        return ', '.join([genre.name for genre in self.genre.all()[:3]])
    
    dislpay_genre.short_description = 'Genre'
    
class BookInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Присвоение уникального значения в виде числа')
    # primarykey позволяет решать, уникально ли данное значение или нет

    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)

    imprint = models.CharField(max_length=200)

    due_back = models.DateField(null=True, blank=True)
    # blank позволяет решать можно ли оставлять после пустым или же нет, сам же метод DateField используется для значений
    # в виде даты

    LOAN_STATUS = (
        ('m', 'Обслуживание'),
        ('o', 'В использовании'),
        ('a', 'Доступна'),
        ('r', 'Зарезервирована'),
    )

    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='a', help_text='Наличие книги')
    # default позволяет установить значение которое установлено по умолчанию
    # choices работает с предопределенным списком/кортежем и на основе него он будет принимать аргументы, то есть мы
    # задаем список допустимых значений которые могут быть описына в данном столбце обратите внимание на LOAN_STATUS
    # в нем мы определили 4 кортежа, первое значение каждого кортежа 1 буква, второе расшифровка данной буквы, именно
    # эти буквы исключительно будет принимать данный столбец, кстати при определнии данных кортежей стоит учитывать,
    # слева значения которые принимает сам фреймворк, а справа то что возвращает, не перепутай

    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

    class Meta:
        ordering = ['due_back']
        # данная переменная с значением строчной переменной позволяет задать тип сортировки, если добавить в начало ' - '
        # это позволяте произвести сортировку по убыванию
        permissions = (("can_mark_returned", "Set book as returned"),
                       ('can_edit', 'редактирование'),
                       )

    def __str__(self):
        book_title = self.book.title if self.book else "—"
        return f'{self.id} | {book_title}'
        
class Author(models.Model):

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    def get_absolute_url(self):
        return reverse('author_detail', kwargs={'pk':self.pk})
    
    def __str__(self):
        return f'{self.last_name}, {self.first_name}'
    
    class Meta:
        ordering = ['last_name']
    
class Language(models.Model):
    lang = models.CharField(max_length=50, unique=True, help_text='Введите язык книги')

    def get_absolute_url(self):
        return reverse('language-detail', args=[str(self.id)])
    
    def __str__(self):
        return self.lang
    
    

    
    
