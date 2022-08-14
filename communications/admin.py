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
        if db_field.name == "participants":
            kwargs["queryset"] = Profile.objects.exclude(status='npc')
        if db_field.name == "followers":
            kwargs["queryset"] = Profile.objects.exclude(status='npc')
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
        if db_field.name == "participants":
            kwargs["queryset"] = Profile.living.all()
        if db_field.name == "followers":
            kwargs["queryset"] = Profile.living.all()
        return super().formfield_for_manytomany(db_field, request, **kwargs)


# -----------------------------------------------------------------------------


@admin.register(Statement)
class StatementAdmin(admin.ModelAdmin):
    filter_horizontal = ['seen_by', 'options']
    formfield_overrides = {
        models.ForeignKey: {'widget': forms.Select(attrs={'style': 'width:250px'})},
    }
    list_display = ['id', '__str__', 'author', 'thread', 'created_at']
    list_editable = ['thread', 'author']
    list_filter = ['thread__kind', 'thread']
    ordering = ['-created_at']
    search_fields = ['text']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        for field in [
            'thread',
            'author',
        ]:
            if db_field.name == field:
                formfield = formfield_with_cache(field, formfield, request)
        return formfield


@admin.register(AnnouncementStatement)
class AnnouncementStatementAdmin(StatementAdmin):
    list_filter = [AnnouncementStatementAuthorFilter, 'thread']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "seen_by":
            kwargs["queryset"] = Profile.objects.exclude(status='npc')
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(DebateStatement)
class DebateStatementAdmin(StatementAdmin):
    list_filter = [DebateStatementAuthorFilter, 'thread']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "seen_by":
            kwargs["queryset"] = Profile.living.all() | Profile.objects.filter(status='gm')
        return super().formfield_for_manytomany(db_field, request, **kwargs)


# -----------------------------------------------------------------------------
