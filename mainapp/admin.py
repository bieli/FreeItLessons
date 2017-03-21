from django.contrib import admin
from mainapp.models import Author, Module, Chapter, \
                           Content, Curiosity, ContentStatus, Faq, Task, TaskSolution
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'author', 'is_public_mentor')
    fieldsets = [
        (None, {'fields': [('name', 'surname', 'blog_link', 'is_public_mentor')]}),
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
    class Media:
        #from django.conf import settings
        #media_url = getattr(settings, 'MEDIA_URL', '/media')
        js = [ 'https://www.gstatic.com/charts/loader.js', '/static/admin/js/content_status_stats.js' ]

@admin.register(Faq)
class SortableFaqAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('question',)


class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_visible', 'level', 'points',)


class TaskSolutionAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'user', 'suggestions_count', 'is_finished', 'is_surrender')


admin.site.register(Author, AuthorAdmin)
admin.site.register(Module)
admin.site.register(Chapter)
admin.site.register(Content)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskSolution, TaskSolutionAdmin)
admin.site.register(Curiosity, CuriosityAdmin)
admin.site.register(ContentStatus, ContentStatusAdmin)
#admin.site.register(Faq, FaqAdmin)

