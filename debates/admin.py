from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db import models
from django.db.models import Q
from django.forms import Select

from debates.models import Topic, Debate, Remark
from rpg_project.utils import formfield_for_dbfield_cached
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
    list_display = ['id', 'title', 'order_no', 'created_at']
    list_editable = ['title',  'order_no']
    search_fields = ['title']


class DebateAdmin(admin.ModelAdmin):
    form = DebateAdminForm
    list_display = ['title', 'topic', 'is_ended', 'is_exclusive']
    list_editable = ['topic', 'is_ended', 'is_exclusive']
    list_filter = ['topic']
    search_fields = ['title']
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        fields = [
            'topic',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)
    

class RemarkAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ForeignKey: {'widget': Select(attrs={'style': 'width:350px'})},
    }
    list_display = ['__str__', 'debate', 'created_at', 'author', 'image']
    list_editable = ['debate', 'author', 'image']
    list_filter = ['debate']
    search_fields = ['text']
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        fields = [
            'debate',
            'author',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)


admin.site.register(Topic, TopicAdmin)
admin.site.register(Debate, DebateAdmin)
admin.site.register(Remark, RemarkAdmin)
