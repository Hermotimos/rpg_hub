from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import Q

from debates.models import Topic, Debate, Remark
from users.models import Profile


class DebateAdminForm(forms.ModelForm):
    allowed_profiles = forms.ModelMultipleChoiceField(queryset=Profile.objects
                                                      .exclude(Q(status='dead_player') |
                                                               Q(status='dead_npc') |
                                                               Q(status='gm')),
                                                      required=False,
                                                      widget=FilteredSelectMultiple('Allowed profiles', False))

    followers = forms.ModelMultipleChoiceField(queryset=Profile.objects
                                               .exclude(Q(status='dead_player') |
                                                        Q(status='dead_npc') |
                                                        Q(status='gm')),
                                               required=False,
                                               widget=FilteredSelectMultiple('Followers', False))


class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'date_created']
    search_fields = ['title']


class DebateAdmin(admin.ModelAdmin):
    form = DebateAdminForm
    list_display = ['name', 'topic', 'is_ended', 'is_individual', 'date_created']
    search_fields = ['name']


class RemarkAdmin(admin.ModelAdmin):
    list_display = ['text_begin', 'debate', 'author', 'date_posted', 'image']
    search_fields = ['text']


admin.site.register(Topic, TopicAdmin)
admin.site.register(Debate, DebateAdmin)
admin.site.register(Remark, RemarkAdmin)
