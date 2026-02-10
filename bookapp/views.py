from django.shortcuts import redirect, render
from django.urls import reverse_lazy
# Importamos las vistas genéricas necesarias
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView, TemplateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
# Importamos funciones para calcular estadísticas (Media, Máximo, Mínimo, Cuenta)
from django.db.models import Avg, Max, Min, Count
import json # Necesario para pasar los datos a las gráficas

from bookapp.forms import BookForm
from bookapp.models import Book

# --- VISTAS PARA CREAR Y EDITAR (Sin cambios importantes) ---

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

# --- VISTA DE LISTA (MODIFICADA: Búsqueda, Orden y Paginación) ---

class BookList(ListView):
    model = Book
    context_object_name = 'books'
    template_name = 'bookapp/list.html'
    paginate_by = 5  # Activa la paginación (5 libros por página)

    def get_queryset(self):
        # 1. Empezamos con todos los libros
        libros = Book.objects.all()

        # 2. Si hay búsqueda por título ('q'), filtramos
        busqueda = self.request.GET.get('q')
        if busqueda:
            libros = libros.filter(title__icontains=busqueda)
        
        # 3. Si hay ordenación ('sort'), ordenamos
        orden = self.request.GET.get('sort')
        if orden:
            libros = libros.order_by(orden)
            
        return libros

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pasamos los parámetros actuales a la plantilla para no perderlos al cambiar de página
        context['q'] = self.request.GET.get('q', '')
        context['sort'] = self.request.GET.get('sort', '')
        return context

# --- VISTA DE ESTADÍSTICAS (NUEVA) ---

class BookStats(TemplateView):
    template_name = 'bookapp/stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Estadísticas Simples (Máximos, Mínimos y Medias)
        # aggregate devuelve un diccionario, por eso accedemos con ['pages__avg'], etc.
        datos = Book.objects.aggregate(
            promedio_paginas=Avg('pages'),
            promedio_rating=Avg('rating')
        )
        
        context['avg_pages'] = datos['promedio_paginas']
        context['avg_rating'] = datos['promedio_rating']
        
        # Para el libro mayor/menor, ordenamos y cogemos el primero (.first())
        context['max_pages_book'] = Book.objects.order_by('-pages').first()
        context['min_pages_book'] = Book.objects.order_by('pages').first()

        # 2. Datos para el Gráfico de Barras (Rating)
        # Agrupamos por rating y contamos cuántos libros hay en cada uno
        # Resultado ejemplo: [{'rating': 4, 'total': 2}, {'rating': 5, 'total': 1}]
        datos_rating = Book.objects.values('rating').annotate(total=Count('id')).order_by('rating')
        
        labels_rating = []
        values_rating = []
        for item in datos_rating:
            labels_rating.append(f"Estrellas: {item['rating']}")
            values_rating.append(item['total'])

        # 3. Datos para el Gráfico de Tarta (Status)
        datos_status = Book.objects.values('status').annotate(total=Count('id'))
        
        labels_status = []
        values_status = []
        
        # Diccionario auxiliar para convertir 'PE' en 'Pendiente' para la gráfica
        nombres_status = dict(Book.STATUS_CHOICES) 

        for item in datos_status:
            codigo = item['status']
            nombre_legible = nombres_status.get(codigo, codigo) # Obtiene el nombre completo
            labels_status.append(nombre_legible)
            values_status.append(item['total'])

        # 4. Convertimos las listas a JSON para que JavaScript las entienda
        context['chart_rating_labels'] = json.dumps(labels_rating)
        context['chart_rating_values'] = json.dumps(values_rating)
        context['chart_status_labels'] = json.dumps(labels_status)
        context['chart_status_values'] = json.dumps(values_status)
        
        return context

# --- VISTA DE REGISTRO Y LOGIN (Sin cambios) ---

def register(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        return redirect('book_list')
    return render(request, 'bookapp/form.html', {'form': form})