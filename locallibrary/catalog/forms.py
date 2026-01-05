from django import forms
import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm
from .models import BookInstance, Author

class HTML5DateInput(forms.DateInput):
    input_type = 'date'

class RenewBookModelForm(ModelForm):
    def clean_due_back(self):
       data = self.cleaned_data['due_back']

       if data < datetime.date.today():
           raise ValidationError(_('Invalid date - renewal in past'))

       if data > datetime.date.today() + datetime.timedelta(weeks=4):
           raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

       return data

    class Meta:
        model = BookInstance
        fields = ['due_back',]
        labels = { 'due_back': _('Новая дата возврата'), }
        help_texts = { 'due_back': _('Установите значение не более 4 недель (по умолчанию установлено 3 недели)'), }
        widgets = {
            'due_back': HTML5DateInput(attrs={'class': 'form-control'})
        }

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = '__all__'
        widgets = {
            'date_of_birth': HTML5DateInput(attrs={'class': 'form-control'}),
            'date_of_death': HTML5DateInput(attrs={'class': 'form-control'})
        }


class BookForm(forms.ModelForm):
    class Meta:
        model = __import__('catalog.models', fromlist=['Book']).Book
        fields = ['title', 'author', 'language', 'isbn', 'summary', 'genre']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.Select(attrs={'class': 'form-control'}),
            'language': forms.Select(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'genre': forms.SelectMultiple(attrs={'class': 'form-control'})
        }