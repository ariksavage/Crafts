from django.contrib import admin

from .models import Photo, Project, Tag


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1


class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "made_on", "featured")
    search_fields = ("title", "description", "materials", "tags__name")
    list_filter = ("featured", "tags", "made_on")
    prepopulated_fields = {"slug": ("title",)}  # noqa: RUF012
    inlines = (PhotoInline,)


class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}  # noqa: RUF012


admin.site.register(Tag, TagAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Photo)
