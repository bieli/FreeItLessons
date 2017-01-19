from django.contrib import admin
from mainapp.models import Author, Module, Chapter, Content, Curiosity


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'author')
    fieldsets = [
        (None, {'fields': [('name', 'surname')]}),
    ]

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'author', None) is None:
            obj.author = request.user
            # obj.author = request.user.username
            # obj.save()
        obj.save()


class ChapterAdmin(admin.StackedInline):
    model = Chapter
    list_display = ('name', 'author')

    # def save_model(self, request, obj, form, change):
    #     if getattr(obj, 'author', None) is None:
    #         obj.author = request.user
    #     obj.save()


class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_enabled',)
    inlines = [ChapterAdmin]

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'author', None) is None:
            obj.author = request.user
        obj.save()


class ContentAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'author', None) is None:
            obj.author = request.user
        obj.save()


class CuriosityAdmin(admin.ModelAdmin):
    list_display = ('title', 'author')

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'author', None) is None:
            obj.author = request.user
        obj.save()


admin.site.register(Author)
admin.site.register(Module)
admin.site.register(Chapter)
admin.site.register(Content)
admin.site.register(Curiosity)
