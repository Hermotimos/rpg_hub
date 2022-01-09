from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db import models
from django.forms import Select, TextInput

from communications.models import Statement, Debate, Announcement, Thread, ThreadTag
from rpg_project.utils import formfield_for_dbfield_cached
from users.models import Profile


class ThreadAdmin(admin.ModelAdmin):
    pass


class DebateAdminForm(forms.ModelForm):
    
    class Meta:
        model = Debate
        fields = ['title', 'kind', 'known_directly', 'is_ended', 'is_exclusive']
        widgets = {}
        
    known_directly = forms.ModelMultipleChoiceField(
        queryset=Profile.living.all(),
        required=False,
        widget=FilteredSelectMultiple('Known directly', False),
    )


class AnnouncementAdminForm(forms.ModelForm):
    
    class Meta:
        model = Announcement
        fields = ['title', 'kind', 'known_directly', 'followers', 'tags']
        widgets = {
            'followers': FilteredSelectMultiple('Followers', False),
            'tags': FilteredSelectMultiple('Tags', False),
        }
    
    known_directly = forms.ModelMultipleChoiceField(
        queryset=Profile.contactables.all(),
        required=False,
        widget=FilteredSelectMultiple('Known directly', False),
    )


class ThreadTagAdminForm(forms.ModelForm):
    
    class Meta:
        model = ThreadTag
        fields = ['kind', 'author', 'title', 'color']
        widgets = {
            'color': TextInput(attrs={'type': 'color'}),
        }


class ThreadTagAdmin(admin.ModelAdmin):
    form = ThreadTagAdminForm
    list_display = ['id', 'kind', 'author', 'title', 'color']


class DebateAdmin(admin.ModelAdmin):
    form = DebateAdminForm
    list_display = ['title', 'is_ended', 'is_exclusive', 'created_at']
    list_editable = ['is_ended', 'is_exclusive']
    search_fields = ['title']
    

class AnnouncementAdmin(admin.ModelAdmin):
    form = AnnouncementAdminForm
    list_display = ['title', 'created_at']
    search_fields = ['title']
    

class StatementAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ForeignKey: {'widget': Select(attrs={'style': 'width:250px'})},
    }
    list_display = ['id', '__str__', 'author', 'thread', 'created_at']
    list_editable = ['thread', 'author']
    list_filter = ['thread__kind', 'thread']
    search_fields = ['text']
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        fields = [
            'thread',
            'author',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)
    
    
admin.site.register(Thread, ThreadAdmin)
admin.site.register(ThreadTag, ThreadTagAdmin)
admin.site.register(Debate, DebateAdmin)
admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(Statement, StatementAdmin)
