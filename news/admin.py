from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import Q

from news.models import News, NewsAnswer, Survey, SurveyOption, SurveyAnswer
from users.models import Profile


class NewsAdminForm(forms.ModelForm):
    allowed_profiles = forms.ModelMultipleChoiceField(queryset=Profile.objects
                                                      .exclude(Q(character_status='dead_player') |
                                                               Q(character_status='dead_npc') |
                                                               Q(character_status='gm')),
                                                      widget=FilteredSelectMultiple('Allowed profiles', False),
                                                      required=False)

    followers = forms.ModelMultipleChoiceField(queryset=Profile.objects
                                               .exclude(Q(character_status='dead_player') |
                                                        Q(character_status='dead_npc') |
                                                        Q(character_status='gm')),
                                               widget=FilteredSelectMultiple('Followers', False),
                                               required=False)


class SurveyAdminForm(forms.ModelForm):
    addressees = forms.ModelMultipleChoiceField(queryset=Profile.objects
                                                .exclude(Q(character_status='dead_player') |
                                                         Q(character_status='dead_npc') |
                                                         Q(character_status='gm')),
                                                required=False,
                                                widget=FilteredSelectMultiple('Addressees', False))


class NewsAdmin(admin.ModelAdmin):
    form = NewsAdminForm
    list_display = ['id', 'author', 'title', 'date_posted', 'image']
    list_editable = ['title', 'image']
    readonly_fields = ['seen_by']
    search_fields = ['title']


class NewsAnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'news_title', 'author', 'get_caption', 'date_posted']
    readonly_fields = ['seen_by']
    search_fields = ['text']

    def news_title(self, obj):
        return obj.news.title

    def get_caption(self, obj):
        return obj.text[:100] + '...' if len(str(obj.text)) > 100 else obj.text


class SurveyOptionInline(admin.TabularInline):
    model = SurveyOption
    extra = 4
    readonly_fields = ['yes_voters', 'no_voters']


class SurveyAdmin(admin.ModelAdmin):
    form = SurveyAdminForm
    inlines = [SurveyOptionInline, ]
    list_display = ['title', 'author', 'text', 'image']
    readonly_fields = ['seen_by']
    search_fields = ['title', 'text']


class SurveyAnswerAdmin(admin.ModelAdmin):
    readonly_fields = ['seen_by']


class SurveyOptionAdmin(admin.ModelAdmin):
    list_display = ['survey', 'author', 'option_text']
    list_editable = ['option_text']
    readonly_fields = ['yes_voters', 'no_voters']
    search_fields = ['option_text']


admin.site.register(News, NewsAdmin)
admin.site.register(NewsAnswer, NewsAnswerAdmin)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(SurveyOption, SurveyOptionAdmin)
admin.site.register(SurveyAnswer, SurveyAnswerAdmin)
