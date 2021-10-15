from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple

from news.models import Topic, News, NewsAnswer, Survey, SurveyOption, SurveyAnswer
from rpg_project.utils import formfield_for_dbfield_cached
from users.models import Profile


class NewsAdminForm(forms.ModelForm):
    allowed_profiles = forms.ModelMultipleChoiceField(
        queryset=Profile.contactables.all(),
        required=False,
        widget=FilteredSelectMultiple('Allowed profiles', False),
    )

    followers = forms.ModelMultipleChoiceField(
        queryset=Profile.contactables.all(),
        required=False,
        widget=FilteredSelectMultiple('Followers', False),
    )


class SurveyAdminForm(forms.ModelForm):
    addressees = forms.ModelMultipleChoiceField(
        queryset=Profile.contactables.all(),
        required=False,
        widget=FilteredSelectMultiple('Addressees', False),
    )


class TopicAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'order_no', 'created_at']
    list_editable = ['title', 'order_no']
    search_fields = ['title']
    
    
class NewsAdmin(admin.ModelAdmin):
    form = NewsAdminForm
    list_display = ['title', 'topic', 'created_at']
    list_editable = ['topic']
    ordering = ['-created_at']
    search_fields = ['title']

    def formfield_for_dbfield(self, db_field, **kwargs):
        fields = [
            'topic',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)


class NewsAnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'news_title', 'author', 'get_caption', 'created_at']
    ordering = ['-created_at']
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

    def formfield_for_dbfield(self, db_field, **kwargs):
        fields = [
            'author',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)


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


admin.site.register(Topic, TopicAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(NewsAnswer, NewsAnswerAdmin)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(SurveyOption, SurveyOptionAdmin)
admin.site.register(SurveyAnswer, SurveyAnswerAdmin)
