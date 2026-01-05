from django.contrib import admin
from .models import Author, Genre, Book, BookInstance, Language
# в обязательном порядке импортируем внедренные модели

admin.site.register(Genre) # регистрация модели
admin.site.register(Language)

# сейчас мы разберем два способа регистрации админ панели для соотвествующей модели
# первый способ №1
# class AuthorAdmin(admin.ModelAdmin): #создание класса админ панели для модели Автор 1.1
#    pass
# admin.site.register(Author, AuthorAdmin) # регистрация модели админ панели для модели Автор 1.2


# второй способ №2
# @admin.register(Book) #регистрируем модель Book через декоратор 2.1
# class BookAdmin(admin.ModelAdmin): #создаем соответсвующий класс админ панели модели Book 2.2
#    pass                          



class BookInstanceInline(admin.TabularInline): # класс позволяющий определить вид отображения таблицы и внедрения её в иной модуль
    model = BookInstance                       # данный класс наследуется от TabularInline вид отображение, в данном случае
                                               # в горизональном виде, также имеется и второй вид отображаения передающийся из
                                               # StackedInline позволяющий отобразить данные в вертикальном формате
                                               # исползьует атрибут model который принимает модель которая будет подтвержена изменению
                                               # и внедрению в данном случае BookInstance 

class BookInline(admin.TabularInline):
    model = Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'dislpay_genre', 'language',)
    inlines = [BookInstanceInline] # данный атрибут принимает внутрь себя класс содержащий в себе модель для внедрения её 
                                   # внутрь колонок

@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book','status','due_back','id', 'borrower')
    list_filter = ('status', 'due_back') # также используя list_filter мы можем внедрить в ветку, в данном случае BookInstance
                                         # фильтр, с применением тех колонок, которые мы хотим

    fieldsets = (                                                         # создание секций полей, это кортеж принимающий в себя
                (None, {'fields': ('book', 'imprint', 'id')}),            # кортеж в котором первое значение идет наименование
                ('Availability', {'fields': ('status', 'due_back', 'borrower')}),     # секции может быть None или же именовать любым именем
    )                                                                     # второе значение словарь, с обязательным ключом
                                                                          # fields значениями данного ключа выступают колонки на наш выбор

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', # благодаря list_display у нас есть возможность измененить
                    'date_of_death',)                           # отображение на админ сайте в ветке Автора, при этом мы может решать
                                                                # что именно будет отображаться, добавляя колонки по желанию
                                                                # важно помнить что при попытке внедрения колонки с типом ManyToMany
                                                                # произойдет ошибка т.к. данный тип не годен для использования в данной
                                                                # функции, поэтому если вы желаете внедрить колонку с таким типом
                                                                # следует заняться переопредлением данного типа заранее

    fields = ('last_name', 'first_name', ('date_of_birth', 'date_of_death')) # настройка отображения на дисплее при добавлении значения, 
                                                                             # мы можем перечислят в каком порядке 
                                                                             # будет построена таблица
                                                                             # если мы обернули колонки в кортеж
                                                                             # отображение выбранных колонок производится
                                                                             # в рамках одноой строки
    inlines = [BookInline]