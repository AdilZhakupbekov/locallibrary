from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseRedirect
from .models import Book, BookInstance, Author, Genre
from django.views import generic, View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
import datetime
from .forms import RenewBookModelForm, AuthorForm, ReserveBookForm
from django.contrib.auth.decorators import permission_required
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.db.models import Q


def index(request):
    num_books = Book.objects.all().count()
    num_instance = BookInstance.objects.all().count()
    num_authors = Author.objects.count()
    num_genre = Genre.objects.all().count()
    num_instance_available = BookInstance.objects.filter(status__exact='a').count()
    num_tbooks = Book.objects.exclude(title='').count()
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1



    return render(request, 'catalog/index.html', {'num_books': num_books, 'num_instance': num_instance,
                                          'num_instance_available': num_instance_available, 'num_authors': num_authors, 
                                          'num_genre': num_genre, 'num_tbooks': num_tbooks, 'num_visits': num_visits})

class BookListView(generic.ListView):
    model = Book
    paginate_by = 10
    template_name = 'catalog/book_list.html'
    context_object_name = 'book_lst'

    def get_queryset(self):
        queryset = Book.objects.all()
        q = self.request.GET.get('q')

        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(author__last_name__icontains=q) |
                Q(author__first_name__icontains=q)
            )

        return queryset
    
class BookDetailView(generic.DetailView):
    model = Book
    template_name = 'catalog/book_detail.html'


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10
    template_name = 'catalog/author_list.html'
    context_object_name = 'author_lst'

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10
    template_name = 'catalog/author_list.html'
    context_object_name = 'author_lst'

    def get_queryset(self):
        queryset = Author.objects.all()
        q = self.request.GET.get('q', '').strip()

        if q:
            parts = q.split()

            query = Q()
            for part in parts:
                query &= (
                    Q(first_name__icontains=part) |
                    Q(last_name__icontains=part)
                )

            queryset = queryset.filter(query)

        return queryset
    
class AuthorDetailView(generic.DetailView):
    model = Author
    template_name = 'catalog/author_detail.html'
    
class MyView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

class LoanedBookListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/my_books.html'
    paginate_by = 10
    context_object_name = 'borrower_lst'

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user, status__in=['o', 'r']).order_by('due_back')
    
@permission_required('catalog.can_edit')
def create_book_inline(request):
    if request.method == 'POST':
        from .forms import BookForm
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            form.save_m2m()
    return HttpResponseRedirect(reverse('my_tools'))
    
    
@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_inst = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        form = RenewBookModelForm(request.POST)

        if form.is_valid():
            book_inst.due_back = form.cleaned_data['due_back']
            book_inst.save()

            return HttpResponseRedirect(reverse('my_tools'))
        
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookModelForm(initial={'due_back': proposed_renewal_date})

    return render(request, 'catalog/book_renew.html', {
        'form': form, 
        'bookinst': book_inst,
    })
class AuthorCreate(CreateView):
    model = Author
    form_class = AuthorForm

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')

class BookCreate(CreateView):
    model = Book
    fields = '__all__'

class BookUpdate(UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'dislpay_genre', 'language']

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')

class MyToolsView(PermissionRequiredMixin, generic.ListView):
    permission_required = ('catalog.can_mark_returned', 
                           'catalog.can_edit',)
    model = BookInstance
    template_name = 'catalog/my_tools.html'
    context_object_name = 'instances'

    def get_queryset(self):
        return BookInstance.objects.select_related('book', 'borrower').filter(book__isnull=False, borrower__isnull=False).order_by('book__title')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # provide an empty AuthorForm and list of authors for inline add/delete
        context['author_form'] = AuthorForm()
        context['authors'] = Author.objects.all().order_by('last_name', 'first_name')
        # provide book form and books list for inline add/delete
        from .forms import BookForm
        context['book_form'] = BookForm()
        context['books'] = Book.objects.all().order_by('title')
        return context
    
class ReserveBook(UpdateView):
    model = BookInstance
    form_class = ReserveBookForm
    template_name = 'catalog/reserve_book.html'
    success_url = reverse_lazy('books')

    def form_valid(self, form):
        form.instance.borrower = self.request.user
        form.instance.status = 'o'
        return super().form_valid(form)
    
class DeleteBookView(DeleteView):
    model = Book
    template_name = 'catalog/book_delete.html'
    success_url = reverse_lazy('books')

class DeleteAuthorView(DeleteView):
    model = Author
    template_name = 'catalog/author_delete.html'
    success_url = reverse_lazy('authors')

class ReturnBookView(UpdateView):
    model = BookInstance
    fields = []
    template_name = 'catalog/return_book.html'
    success_url = reverse_lazy('my_books')

    def form_valid(self, form):
        form.instance.borrower = None
        form.instance.status = 'a'
        form.instance.due_back = None
        return super().form_valid(form)
    
class ReturnBookPermView(UpdateView):
    model = BookInstance
    fields = []
    template_name = 'catalog/return_book_perm.html'
    success_url = reverse_lazy('my_tools')

    def form_valid(self, form):
        form.instance.borrower = None
        form.instance.status = 'a'
        form.instance.due_back = None
        return super().form_valid(form)