from django import forms
from django.contrib import admin
from django.db import models

from communications.admin_filters import AnnouncementStatementAuthorFilter, \
    DebateStatementAuthorFilter
from communications.models import Statement, Debate, Announcement, Thread, \
    ThreadTag, AnnouncementStatement, DebateStatement
from rpg_project.utils import formfield_with_cache
from users.models import Profile


# -----------------------------------------------------------------------------


class ThreadTagAdminForm(forms.ModelForm):

    class Meta:
        model = ThreadTag
        exclude = []
        widgets = {'color': forms.TextInput(attrs={'type': 'color'})}


@admin.register(ThreadTag)
class ThreadTagAdmin(admin.ModelAdmin):
    form = ThreadTagAdminForm
    list_display = ['id', 'kind', 'author', 'title', 'color']


# -----------------------------------------------------------------------------


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    pass


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    fields = ['title', 'kind', 'participants', 'followers', 'tags']
    filter_horizontal = ['participants', 'followers', 'tags']
    list_display = ['title', 'created_at']
    search_fields = ['title']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        profiles = Profile.objects.exclude(status='npc').select_related('character')
        if db_field.name == "participants":
            kwargs["queryset"] = profiles
        if db_field.name == "followers":
            kwargs["queryset"] = profiles
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(Debate)
class DebateAdmin(admin.ModelAdmin):
    fields = [
        'title', 'kind', 'is_ended', 'is_exclusive', 'participants',
        'followers',
    ]
    filter_horizontal = ['participants', 'followers']
    list_display = ['title', 'is_ended', 'is_exclusive', 'created_at']
    list_editable = ['is_ended', 'is_exclusive']
    search_fields = ['title']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        profiles = Profile.objects.exclude(is_alive=False).select_related('character')
        if db_field.name == "participants":
            kwargs["queryset"] = profiles
        if db_field.name == "followers":
            kwargs["queryset"] = profiles
        return super().formfield_for_manytomany(db_field, request, **kwargs)


# -----------------------------------------------------------------------------


@admin.register(Statement)
class StatementAdmin(admin.ModelAdmin):
    filter_horizontal = ['seen_by', 'options']
    formfield_overrides = {
        models.ForeignKey: {'widget': forms.Select(attrs={'style': 'width:250px'})},
    }
    list_display = ['id', 'thread', 'author', '__str__', 'created_at']
    list_filter = ['thread__kind', 'thread']
    list_select_related = ['author__character', 'thread']
    ordering = ['-created_at']
    search_fields = ['text']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "seen_by":
            kwargs["queryset"] = Profile.objects.select_related('character')
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(AnnouncementStatement)
class AnnouncementStatementAdmin(StatementAdmin):
    list_filter = [AnnouncementStatementAuthorFilter, 'thread']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "seen_by":
            kwargs["queryset"] = Profile.objects.exclude(
                status='npc').select_related('character')
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(DebateStatement)
class DebateStatementAdmin(StatementAdmin):
    list_filter = [DebateStatementAuthorFilter, 'thread']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "seen_by":
            kwargs["queryset"] = (
                Profile.living.all() | Profile.objects.filter(status='gm')
            ).select_related('character')
        return super().formfield_for_manytomany(db_field, request, **kwargs)


# -----------------------------------------------------------------------------
