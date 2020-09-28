from django_filters import rest_framework as filters

from .models import Titles


class TitlesFilter(filters.FilterSet):
    category = filters.CharFilter(field_name='category__slug',
                                  lookup_expr='icontains')
    genre = filters.CharFilter(field_name='genre__slug',
                               lookup_expr='icontains')
    year = filters.CharFilter(field_name='year', lookup_expr='icontains')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Titles
        fields = ['category', 'genre', 'year', 'name']
