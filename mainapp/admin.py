from django.contrib import admin
from mainapp.models import Author, Module, Chapter, Content, Curiosity, ContentStatus


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


class ContentStatusAdmin(admin.ModelAdmin):
    list_filter = ('status', 'user')    
    list_display = ('id', 'status', 'view_content_link', 'user', 'created_at', 'updated_at', )
    ordering = ('-updated_at',)

    def view_content_link(self, obj):
        return '<a href="/admin/mainapp/content/%d/?_to_field=id&_popup=1" target="_blank">%s</a>' % (int(obj.content.id), obj.content,)
    view_content_link.allow_tags = True
    view_content_link.short_description = 'Content edit link' # Optional


admin.site.register(Author, AuthorAdmin)
admin.site.register(Module)
admin.site.register(Chapter)
admin.site.register(Content)
admin.site.register(Curiosity, CuriosityAdmin)
admin.site.register(ContentStatus, ContentStatusAdmin)

