from django.apps import AppConfig


class MoviesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'movies'
    verbose_name = 'Фильм'  #Чтобы в админке приложение называлось не movies, а Фильмы
