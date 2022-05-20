from django_filters import rest_framework as filters
from rest_framework.response import Response

from .models import Movie

from rest_framework.pagination import PageNumberPagination

class PaginationMovies(PageNumberPagination):
    """Меняет количество выводимых записей отлично от дефолтной настройки"""
    page_size = 2         # количество записей на странице
    max_page_size = 1000  # максимальное количество записей

    def get_paginated_response(self, data):
        """с помощью даннного метода можно изменять вид респонза с пагинацией"""
        # до переопределения метода
        # "count": 2,
        #   "next": null,
        #   "previous": null,
        #   "results": []
        # после переопределения метода
        # "links": {
        #     "next": null,
        #     "previous": null
        #   },
        #   "count": 2,
        #   "results": []
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data
        })


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip



class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    """
    Чтобы использовать lookup_expr='in' нужен класс BaseInFilter. lookup_expr определяет каким образом фильтровать.
    Жанры это поле М2М и в таблице связывающей фимьм - жанр используются id, а искать нужно по названию, поэтому
    потребуется CharFilter. По умолчанию фильтрация идет по id.
    """
    pass


class MovieFilter(filters.FilterSet):
    """Данный класс будет указывать поля и дополнительную логику с помощью которой фильтровать"""
    genres = CharFilterInFilter(field_name='genres__name', lookup_expr='in')
    year = filters.RangeFilter()  # диапазон дат от мин до мах

    class Meta:
        model = Movie
        fields = ['genres', 'year']