from django.db import models
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, permissions, viewsets

from django_filters.rest_framework import DjangoFilterBackend

from .service import get_client_ip, MovieFilter, PaginationMovies

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
# class MovieListView(generics.ListAPIView):
#     """Вывод списка фильмов с помощью generics класса"""
#     serializer_class = MovieListSerializer
#
#     filter_backends = (DjangoFilterBackend, )   # подключаем фильтры, для этого нужно установить библиотеку
#     # django-filter, добавить в Installed apps, также в settings указать default filter
#     filterset_class = MovieFilter
#     # по запросу /api/v1/movie/?year_min=1890&year_max=2000&genres=Боевик,Приключения будут выводиться фильмы
#     # попадающие под указанные параметры
#     permission_classes = [permissions.IsAuthenticated]  # теперь данную страницу могут просматривать только авториз
#     # для получения токена в postman переходим по ссылке http://127.0.0.1:8000/auth/token/login в тело запроса(body)
#     # указываем ключ - username, значение - имя пользователя, ключ password, значение пароль
#     # в ответе вернется ключ auth_token со значением токена, токен добавляется в БД.
#     # Теперь для открытия данной страницы в заголовки(headers)
#     # добавляем ключ Authorization значение Token <полученный токен>. Без токена вернется ошибка авторизации.
#     # Для разлогирования отправляем запрос на http://127.0.0.1:8000/auth/token/logout
#     # добавляем ключ Authorization значение Token <полученный токен>. и данный токен удаляется из БД.
#
#     def get_queryset(self):
#         """В данном случае используем метод get_queryset вместо атрибута queryset т.к. нужно добраться до
#         self.request иначе можно было бы спокойно использовать queryset"""
#         movies = Movie.objects.filter(draft=False).annotate(
#             rating_user=models.Count("ratings", filter=models.Q(ratings__ip=get_client_ip(self.request)))
#         ).annotate(
#             middle_star=models.Avg('ratings__star')
#         )
#         return movies




# переписываем вывод фильмов с помощью viewsets
class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    """Вывод списка фильмов и полного фильма с помощью viewset класса"""
    # ReadOnlyModelViewSet - позволяет выводить и список записей и отдельную запись

    filter_backends = (DjangoFilterBackend,)    # аналогично использованию
    filterset_class = MovieFilter               # в generics классе
    permission_classes = [permissions.IsAuthenticated]
    #pagination_class = PaginationMovies

    # а вот serializer_class был разный в MovieListView и MovieDetailView поэтому переопределяем метод
    def get_serializer_class(self):
        if self.action == 'list':    # action это http-запросы
            return MovieListSerializer
        elif self.action == 'retrieve':
            return MovieDetailSerializer

    def get_queryset(self):
        """В данном случае используем метод get_queryset вместо атрибута queryset т.к. нужно добраться до
        self.request иначе можно было бы спокойно использовать queryset"""
        # get_queryset используется аналогично как в в generics классе
        movies = Movie.objects.filter(draft=False).annotate(
            rating_user=models.Count("ratings", filter=models.Q(ratings__ip=get_client_ip(self.request)))
        ).annotate(
            middle_star=models.Avg('ratings__star')
        )
        return movies




# class MovieDetailView(APIView):
#     """Вывод фильма"""
#     def get(self, request, pk):
#         movie = Movie.objects.get(id=pk, draft=False)
#         serializer = MovieDetailSerializer(movie)
#         return Response(serializer.data)

class MovieDetailView(generics.RetrieveAPIView):
    """Вывод фильма"""
    queryset = Movie.objects.filter(draft=False)  # вместо метода get и id=pk здесь используем queryset и метод filter,
    # а класс RetrieveAPIView будет сам находить по pk нужную запись
    serializer_class = MovieDetailSerializer


# class ReviewCreateView(APIView):
#     """Добавление отзыва к фильму"""
#     def post(self, request):
#         review = ReviewCreateSerializer(data=request.data)
#         if review.is_valid():
#             review.save()
#         return Response(status=201)


# class ReviewCreateView(generics.CreateAPIView):
#     """Добавление отзыва к фильму c помощью generics"""
#     serializer_class = ReviewCreateSerializer   # в таком варианте джанго предлагаем ввод отзыва 2-мя способами:
#     # raw data - как и раньше чистым json, html form - в виде формы


class ReviewCreateViewSet(viewsets.ModelViewSet):
    """Добавление отзыва к фильму c помощью viewsets"""
    # класс ModelViewSet позволяет сразу делать добавление одной записи, вывод списка, обновление и удаление записи,
    # но так как в данном случае нам не нужно изменять или удалять отзывы, то не переопределяем метод
    # get_serializer_class, а просто используем один сериализатор
    serializer_class = ReviewCreateSerializer


# class AddStarRatingView(APIView):
#     """Добавление рейтинга фильму"""
#
#     def post(self, request):
#         serializer = CreateRatingSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(ip=get_client_ip(request))
#             return Response(status=201)
#         else:
#             return Response(status=400)

# class AddStarRatingView(generics.CreateAPIView):
#     """Добавление рейтинга фильму c помощью generics"""
#     serializer_class = CreateRatingSerializer
#
#     def perform_create(self, serializer):
#         """для того чтобы передать сериализатору ip используем этот метод. Данный метод позволяет передавать в
#          метод save сериализатора дополнительные параметры"""
#         serializer.save(ip=get_client_ip(self.request))


class AddStarRatingViewSet(viewsets.ModelViewSet):
    """Добавление рейтинга фильму c помощью viewsets"""
    # весь код остается аналогичным generics классу
    serializer_class = CreateRatingSerializer

    def perform_create(self, serializer):
        """для того чтобы передать сериализатору ip используем этот метод. Данный метод позволяет передавать в
         метод save сериализатора дополнительные параметры"""
        serializer.save(ip=get_client_ip(self.request))


# class ActorsListView(generics.ListAPIView):
#     """Вывод списка Актеров"""
#     queryset = Actor.objects.all()
#     serializer_class = ActorsListSerializer
#
#
# class ActorDetailView(generics.RetrieveAPIView):
#     """Вывод данных об актере/режиссере"""
#     queryset = Actor.objects.all()
#     serializer_class = ActorDetailSerializer


class ActorViewSet(viewsets.ReadOnlyModelViewSet):
    """Вывод списка Актеров и данных об актере"""
    queryset = Actor.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return ActorsListSerializer
        elif self.action == 'retrieve':
            return ActorDetailSerializer


