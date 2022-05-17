from rest_framework import serializers

from .models import Movie, Review, Rating, Actor


# сериализаторы нужны чтобы преобразовывать типы данных питон в тип данных json и наоборот
# сериализаторы очень похожи на формы джанго, поэтому можно к ним относиться как к формам.


class FilterReviewListSerializer(serializers.ListSerializer):
    """Фильтр отзывов, только parent"""
    def to_representation(self, data):   # data это наш queryset
        # если у этого сериалайзера вывести self.parent, то будет MovieDetailSerializer(<Movie: Терминатор>) со
        # всеми полями
        data = data.filter(parent=None)  # фильтруем queryset
        return super().to_representation(data)



class RecursiveSerializer(serializers.Serializer):
    """Вывод рекурсивно children"""
    def to_representation(self, value):  # value - экземпляр модели Review
        # self.parent - RecursiveSerializer(many=True)
        # self.parent.parent - ReviewSerializer():
                    #     name = CharField(label='Имя', max_length=100)
                    #     text = CharField(label='Сообщение', max_length=5000, style={'base_template': 'textarea.html'})
                    #     children = RecursiveSerializer(many=True):
        # self.parent.parent.__class__ - <class 'movies.serializers.ReviewSerializer'>
        serializer = self.parent.parent.__class__(value, context=self.context)
        # serializer -  ReviewSerializer( < Review: Mini - Терминатор >, context = {}):
                        # name = CharField(label='Имя', max_length=100)
                        # text = CharField(label='Сообщение', max_length=5000, style={'base_template': 'textarea.html'})
                        # children = RecursiveSerializer(many=True):
        #  serializer.data - {'name': 'Mini', 'text': 'You like?', 'children': []}
        return serializer.data


class ActorsListSerializer(serializers.ModelSerializer):
    """Вывод списка актеров и режиссеров"""
    class Meta:
        model = Actor
        fields = ("id", "name", "image")


class ActorDetailSerializer(serializers.ModelSerializer):
    """Вывод данных об актере и режиссере"""
    class Meta:
        model = Actor
        fields = "__all__"


class MovieListSerializer(serializers.ModelSerializer):
    """Список фильмов"""
    rating_user = serializers.BooleanField()  # в MovieListView добавили к модели Movie поле rating_user здесь можно
    # его сериализовать вместе с остальными полями
    #middle_star = serializers.IntegerField() # вариант для целых значений когда Sum делим на Count
    middle_star = serializers.FloatField()    # вариант для дробных значений когда Avg

    class Meta:
        model = Movie
        fields = ("id", "title", "tagline", "category", "rating_user", "middle_star") # в таком варианте для category отображается id, а не название



class ReviewCreateSerializer(serializers.ModelSerializer):
    """Добавление отзыва"""

    class Meta:
        model = Review
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    """Вывод отзывов"""
    children = RecursiveSerializer(many=True)

    class Meta:
        list_serializer_class = FilterReviewListSerializer # без данного фильтра дочерние отзывы будут дублироваться,
        # т.е. отображаться и как дочерние и как родительские
        model = Review
        fields = ("name", "text", "children")  # для вывода отзывов со сдвигом от родителя - вместо "parent"
        # используем "children". Чтобы обратиться к "children" в поле parent модели Review должен быть
        # related_name="children"


class MovieDetailSerializer(serializers.ModelSerializer):
    """Полный фильм"""
    category = serializers.SlugRelatedField(slug_field="name", read_only=True)  # slug_field="name" указывает какое
    # поле выводить вместо id, оно будет выводиться только одно, read_only=True - поле только для чтения

    # directors = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)
    directors = ActorDetailSerializer(read_only=True, many=True)
    # actors = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)
    actors = ActorsListSerializer(read_only=True, many=True)
    # меняем сериализатор с serializers.SlugRelatedField на ActorDetailSerializer, то выводятся
    # все данные актеров, если же меняем на ActorsListSerializer, то выводятся поля указанные в ActorsListSerializer



    genres = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)
    ################# без реализации ниже отзывы не выводятся
    #reviews = ReviewCreateSerializer(many=True)  # без related_name="reviews" в поле movie модели Review отзывы
    # не отображаются и вываливается ошибка, т.к. related_name позволяет обращаться из связующей таблицы по этому имени
    # (из таблицы Movie в Review)

    reviews = ReviewSerializer(many=True)


    class Meta:
        model = Movie
        exclude = ("draft",)  # чтобы не прописывать много полей fields можно исключить конкретные


class CreateRatingSerializer(serializers.ModelSerializer):
    """Добавление рейтинга пользователей"""
    class Meta:
        model = Rating
        fields = ("star", "movie")

    def create(self, validated_data):
        # rating = Rating.objects.update_or_create(
        #     ip=validated_data.get('ip', None),
        #     movie=validated_data.get('movie', None),
        #     defaults={'star': validated_data.get('star')}
        # )
        # При отправке json {"star":2, "movie":1} метод update_or_create возвращает кортеж (объект,
        # True/False - создалась или обновилась запись) (<Rating: 2 - Терминатор>, False) данный вариант работает
        # когда используем APIView и метод post
        # но при использовании CreateAPIView возниканиет ошибка связанная с кортежем, поэтому разделим кортеж на
        # переменные
        rating, _ = Rating.objects.update_or_create(
            ip=validated_data.get('ip', None),
            movie=validated_data.get('movie', None),
            defaults={'star': validated_data.get('star')}
        )
        return rating