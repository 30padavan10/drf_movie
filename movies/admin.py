from django import forms
from django.contrib import admin

from django.utils.safestring import mark_safe

from .models import Actor, Category, Genre, Movie, Review, Rating, Rating_star, MovieShots

from ckeditor_uploader.widgets import CKEditorUploadingWidget


class MovieAdminForm(forms.ModelForm):
    description = forms.CharField(label='Описание', widget=CKEditorUploadingWidget()) # когда у нас 1 язык

    class Meta:
        model = Movie
        fields = '__all__'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):    # для мультиязычности наследуемся не от admin.ModelAdmin
    """Категории админки"""
    list_display = ("id", "name", "url")  # ссылкой является первое поле, чтобы изменить - указать list_display_links
    list_display_links = ("name",)

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """Рейтинг"""
    list_display = ("star", "movie", "ip")

@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    #list_display = ("name", "age", "image")  # поле image отображается как ссылка на картинку, а не картинка
    list_display = ("name", "age", "get_image")
    readonly_fields = ("get_image",)  # добавляет поле get_image на страницу редактирования объекта

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="50" heigth="60"')
        # mark_safe выводит изображение не как строку, а как тэг

    get_image.short_description = "Изображение"  # меняет название столбца с get_image на Изображение


#admin.site.register(Actor)
# admin.site.register(Category, CategoryAdmin) меняется на @admin.register(Category)

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "url")

#admin.site.register(Genre)


class ReviewInline(admin.StackedInline):  # TabularInline - суть таже, оформление другое
    model = Review
    extra = 1
    readonly_fields = ("name", "email")


class MoviesShotsInline(admin.TabularInline):
    model = MovieShots
    extra = 1
    readonly_fields = ("get_image",)  # добавляет поле get_image на страницу редактирования объекта

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="110" heigth="100"')
        # mark_safe выводит изображение не как строку, а как тэг

    get_image.short_description = "Изображение"

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "url", "draft")
    list_filter = ("category", "year")  # добавляет фильтр по данным полям
    search_fields = ("title", "category__name")  # поиск по полям
    save_on_top = True
    save_as = True  # добавляется кнопка сохранить как новый объект, т.е. позволяет использовать какой-либо объект
    # как шаблон
    list_editable = ("draft",)  # позволяет редактировать draft из списка фильмов
    inlines = [ReviewInline, MoviesShotsInline]
    readonly_fields = ("get_image",)
    form = MovieAdminForm
    actions = ['publish', 'unpublish']  # добавляют действие которое можно выполнять со всеми выбранными записями

    #fields = (("actors", "directors", "genres"),)  # выводит указанные поля в строку, но при этом остальные поля
    # если есть недоступны для редактирования
    fieldsets = (  # также как и fields позволяет группировать поля
        (None, {
            "fields": (("title", "tagline"),)
            }
        ),
        (None, {
            "fields": ("description", ("poster", "get_image"))
            }
         ),
        (None, {
            "fields": (("year", "country"),)
        }
         ),
        (None, {
            "fields": (("actors", "directors", "genres"),)
        }
         ),
        ("Касса", {
            "classes": ("collapse",),                            # Позволяет группу сворачивать, обязательно нужно
                                                                 # название
            "fields": (("world_premiere", "budjet", "fees_in_usa"),)
        }
         ),
        ("Опции", {                                             # "Опции" добавляет заголовок для полей
            "fields": (("fees_in_world", "category", "url"),)
        }
         ),
    )

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.poster.url} width="110" heigth="100"')
        # в данной модели поле ImageField называется poster, поэтому обращаемся к obj.poster
        # а в модели MovieShots поле ImageField называется image, поэтому там obj.image

    def unpublish(self, request, queryset):
        """Снять с публикации"""
        row_update = queryset.update(draft=True)
        if row_update == '1':
            message_bit = "1 запись была обновлена"
        else:
            message_bit = f"{row_update} записей были обновлены"
        self.message_user(request, f"{message_bit}")

    def publish(self, request, queryset):
        """Опубликовано"""
        row_update = queryset.update(draft=False)
        if row_update == 1:
            message_bit = "1 запись была обновлена"
        else:
            message_bit = f"{row_update} записей были обновлены"
        self.message_user(request, f"{message_bit}")

    publish.short_description = "Опубликовать"
    publish.allowed_permission = ('change',)  # чтобы применять action у пользователя должны быть права на измен записи

    unpublish.short_description = "Снять с публикации"
    unpublish.allowed_permission = ('change',)

    get_image.short_description = "Постер"





#admin.site.register(Movie)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "parent", "movie", "id")
    readonly_fields = ("name", "email")  # закрыть поля от редактирования в админке
    inlines = [ReviewInline]  # требует класс ReviewInline, нужен чтобы при редактировании отзыва
                              # показывались остальные отзывы к этому фильму

#admin.site.register(Review)

#admin.site.register(Rating)
admin.site.register(Rating_star)

@admin.register(MovieShots)
class MovieShotsAdmin(admin.ModelAdmin):
    list_display = ("title", "movie", "get_image")
    readonly_fields = ("get_image",)  # добавляет поле get_image на страницу редактирования объекта

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="50" heigth="60"')
        # mark_safe выводит изображение не как строку, а как тэг

    get_image.short_description = "Изображение"

#admin.site.register(MovieShots)

admin.site.site_title = "Django Movies"   # добавляем Django Movies в название вкладки
admin.site.site_header = "Django Movies"  # меняем заголовок админки