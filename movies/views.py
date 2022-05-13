from django.db import models
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics

from .service import get_client_ip

from .models import Movie, Actor
from .serializers import (
    MovieListSerializer,
    MovieDetailSerializer,
    ReviewCreateSerializer,
    CreateRatingSerializer,
    ActorsListSerializer,
    ActorDetailSerializer,
)


# class MovieListView(APIView):
#     """Вывод списка фильмов"""
#     # def get(self, request):
#     #     movies = Movie.objects.filter(draft=False)
#     #     serializer = MovieListSerializer(movies, many=True)  # many=True говорит о том что записей несколько
#     #     return Response(serializer.data)
#     # def get до реализации вывода рейтинга
#
#     def get(self, request):
#         """с помощью метода annotate в модель Movie будет добавлено поле с названием rating_user(произвальное),
#          которое будет Bool значением, если пользователь устанавливал рейтинг то True, иначе False
#          Case это условное выражение, обрабатываются непосредственно СУБД и внутри себя предполагает:
#           When - условие,
#           then - результат при таком условии
#           default - если условия не выполнились
#           output_field - тип поля"""
#         # movies = Movie.objects.filter(draft=False).annotate(                # если в таком варианте добавлять поле
#         #     rating_user=models.Case(                                        # rating_user, то при наличии рейтингов
#         #         models.When(ratings__ip=get_client_ip(request), then=True), # от пользователей с другим ip будут
#         #         default=False,                                              # выводиться дубли записей
#         #         output_field=models.BooleanField()
#         #     ),
#         # )
#         movies = Movie.objects.filter(draft=False).annotate(
#             rating_user=models.Count("ratings", filter=models.Q(ratings__ip=get_client_ip(request)))
#         ).annotate(
#             #middle_star=models.Sum(models.F('ratings__star')) / models.Count(models.F('ratings'))
#             middle_star=models.Avg('ratings__star')
#         )
#         # для добавление нескольких полей методы annotate можно вызывать друг за другом
#         # в данном варианте с помощью метода Count считаем количество рейтингов связанных с фильмом и отфильтровываем
#         # те рейтинги которые не совпадают с нашим ip, так получаем rating_user
#         # для поля middle_star считаем сумму звезд всех рейтингов, чтобы можно было оперировать результатом как числом
#         # оборачиваем его функциональным методом F, также Count считает количество рейтингов и также оборачивается F
#         # полученный цифры делим и получаем среднее значение
#         # не забыть что добавленные поля нужно также добавить в сериализаторе MovieListSerializer
#
#         serializer = MovieListSerializer(movies, many=True)  # many=True говорит о том что записей несколько
#         return Response(serializer.data)

# Переписываем класс MovieListView с помощью generics класса
class MovieListView(generics.ListAPIView):
    """Вывод списка фильмов с помощью generics класса"""
    serializer_class = MovieListSerializer

    def get_queryset(self):
        """В данном случае используем метод get_queryset вместо атрибута queryset т.к. нужно добраться до
        self.request иначе можно было бы спокойно использовать queryset"""
        movies = Movie.objects.filter(draft=False).annotate(
            rating_user=models.Count("ratings", filter=models.Q(ratings__ip=get_client_ip(self.request)))
        ).annotate(
            middle_star=models.Avg('ratings__star')
        )
        return movies

class MovieDetailView(APIView):
    """Вывод фильма"""
    def get(self, request, pk):
        movie = Movie.objects.get(id=pk, draft=False)
        serializer = MovieDetailSerializer(movie)
        return Response(serializer.data)


class ReviewCreateView(APIView):
    """Добавление отзыва к фильму"""
    def post(self, request):
        review = ReviewCreateSerializer(data=request.data)
        if review.is_valid():
            review.save()
        return Response(status=201)


class AddStarRatingView(APIView):
    """Добавление рейтинга фильму"""

    def post(self, request):
        serializer = CreateRatingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ip=get_client_ip(request))
            return Response(status=201)
        else:
            return Response(status=400)


class ActorsListView(generics.ListAPIView):
    """Вывод списка Актеров"""
    queryset = Actor.objects.all()
    serializer_class = ActorsListSerializer


class ActorDetailView(generics.RetrieveAPIView):
    """Вывод данных об актере/режиссере"""
    queryset = Actor.objects.all()
    serializer_class = ActorDetailSerializer

