from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db import models
from django.db.models import Q
from django.forms import Select

from debates.models import Topic, Debate, Remark
from users.models import Profile


class DebateAdminForm(forms.ModelForm):
    known_directly = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.exclude(
            Q(status='dead_player') | Q(status='dead_npc') | Q(status='gm')
        ),
        required=False,
        widget=FilteredSelectMultiple('Known directly', False),
    )
    followers = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.exclude(
            Q(status='dead_player') | Q(status='dead_npc') | Q(status='gm')
        ),
        required=False,
        widget=FilteredSelectMultiple('Followers', False),
    )
    
    
class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
    search_fields = ['title']


class DebateAdmin(admin.ModelAdmin):
    form = DebateAdminForm
    list_display = ['name', 'topic', 'is_ended', 'is_individual']
    list_editable = ['topic', 'is_ended', 'is_individual']
    list_filter = ['topic']
    search_fields = ['name']
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        # https://blog.ionelmc.ro/2012/01/19/tweaks-for-making-django-admin-faster/
        request = kwargs['request']
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        fields = [
            'topic',
        ]
        for field in fields:
            if db_field.name == field:
                choices = getattr(request, f'_{field}_choices_cache', None)
                if choices is None:
                    choices = list(formfield.choices)
                    setattr(request, f'_{field}_choices_cache', choices)
                formfield.choices = choices
        return formfield


class RemarkAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'debate', 'created_at', 'author', 'image']
    list_editable = ['debate', 'author', 'image']
    list_filter = ['debate']
    search_fields = ['text']
    
    formfield_overrides = {
        models.ForeignKey: {'widget': Select(attrs={'style': 'width:350px'})},
    }

    def formfield_for_dbfield(self, db_field, **kwargs):
        # https://blog.ionelmc.ro/2012/01/19/tweaks-for-making-django-admin-faster/
        request = kwargs['request']
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        fields = [
            'debate',
            'author',
        ]
        for field in fields:
            if db_field.name == field:
                choices = getattr(request, f'_{field}_choices_cache', None)
                if choices is None:
                    choices = list(formfield.choices)
                    setattr(request, f'_{field}_choices_cache', choices)
                formfield.choices = choices
        return formfield
        
    
admin.site.register(Topic, TopicAdmin)
admin.site.register(Debate, DebateAdmin)
admin.site.register(Remark, RemarkAdmin)
