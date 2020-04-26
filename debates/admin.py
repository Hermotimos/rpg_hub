from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple, \
    RelatedFieldWidgetWrapper
from django.db.models import Q
from django.db.models.fields import reverse_related

from debates.models import Topic, Debate, Remark
from history.models import ChronicleEvent
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
    
    # chronicle_event = forms.ModelChoiceField(queryset=ChronicleEvent.objects.all(), required=False)
    #
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # rel = ManyToOneRel(self.instance.location.model, 'id')
    #     self.fields['chronicle_event'].widget = RelatedFieldWidgetWrapper(
    #         widget=self.fields['chronicle_event'].widget,
    #         rel=reverse_related.OneToOneRel,
    #         admin_site=admin
    #     )
    
    
class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'date_created']
    search_fields = ['title']


class DebateAdmin(admin.ModelAdmin):
    form = DebateAdminForm
    list_display = ['name', 'topic', 'is_ended', 'is_individual', 'chronicle_event']
    list_filter = ['topic']
    search_fields = ['name']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('chronicle_event')
        return qs


class RemarkAdmin(admin.ModelAdmin):
    list_display = ['text_begin', 'debate', 'author', 'date_posted', 'image']
    list_filter = ['debate']
    search_fields = ['text']


admin.site.register(Topic, TopicAdmin)
admin.site.register(Debate, DebateAdmin)
admin.site.register(Remark, RemarkAdmin)
