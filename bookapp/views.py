from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView, TemplateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Avg, Max, Min, Count
import json

from bookapp.forms import BookForm
from bookapp.models import Book


class BookCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'bookapp.add_book'
    model = Book
    form_class = BookForm
    template_name = 'bookapp/form.html'
    success_url = reverse_lazy('book_list')

class BookUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'bookapp.change_book'
    model = Book
    form_class = BookForm
    template_name = 'bookapp/form.html'
    success_url = reverse_lazy('book_list')

class BookDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'bookapp.delete_book'
    model = Book
    template_name = 'bookapp/confirm_delete.html'
    success_url = reverse_lazy('book_list')

class BookDetail(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'bookapp/detail.html'
    context_object_name = 'book'

class BookList(ListView):
    model = Book
    context_object_name = 'books'
    template_name = 'bookapp/list.html'
    paginate_by = 5

    def get_queryset(self):

        libros = Book.objects.all()

        busqueda = self.request.GET.get('q')
        if busqueda:
            libros = libros.filter(title__icontains=busqueda)
        
        orden = self.request.GET.get('sort')
        if orden:
            libros = libros.order_by(orden)
            
        return libros

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['sort'] = self.request.GET.get('sort', '')
        return context


class BookStats(TemplateView):
    template_name = 'bookapp/stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        

        datos = Book.objects.aggregate(
            promedio_paginas=Avg('pages'),
            promedio_rating=Avg('rating')
        )
        
        context['avg_pages'] = datos['promedio_paginas']
        context['avg_rating'] = datos['promedio_rating']
        
        context['max_pages_book'] = Book.objects.order_by('-pages').first()
        context['min_pages_book'] = Book.objects.order_by('pages').first()


        datos_rating = Book.objects.values('rating').annotate(total=Count('id')).order_by('rating')
        
        labels_rating = []
        values_rating = []
        for item in datos_rating:
            labels_rating.append(f"Estrellas: {item['rating']}")
            values_rating.append(item['total'])

        datos_status = Book.objects.values('status').annotate(total=Count('id'))
        
        labels_status = []
        values_status = []
        nombres_status = dict(Book.STATUS_CHOICES) 

        for item in datos_status:
            codigo = item['status']
            nombre_legible = nombres_status.get(codigo, codigo)
            labels_status.append(nombre_legible)
            values_status.append(item['total'])

        context['chart_rating_labels'] = json.dumps(labels_rating)
        context['chart_rating_values'] = json.dumps(values_rating)
        context['chart_status_labels'] = json.dumps(labels_status)
        context['chart_status_values'] = json.dumps(values_status)
        
        return context

def register(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        return redirect('book_list')
    return render(request, 'bookapp/form.html', {'form': form})