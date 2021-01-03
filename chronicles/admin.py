from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import Q, TextField, CharField, ForeignKey, OneToOneField
from django.forms import Textarea, TextInput, Select

from chronicles.models import (
    Thread, ThreadActive, ThreadEnded,
    Date,
    TimeUnit, Chronology, Era, Period, HistoryEvent, GameEvent,
    Chapter,
    GameSession,
)
from toponomikon.models import SecondaryLocation
from users.models import Profile


# ----------------------------------------------
# ----------------------------------------------
# ---------- GameEvent & HistoryEvent ----------
# ----------------------------------------------
# ----------------------------------------------

class GameEventAdminForm(forms.ModelForm):
    class Meta:
        model = GameEvent
        fields = ['game', 'event_no_in_game', 'date_start', 'date_end',
                  'in_timeunit', 'description_short', 'description_long',
                  'threads', 'locations', 'known_directly', 'known_indirectly',
                  'pictures', 'debates', 'audio']
        widgets = {
            'known_directly': FilteredSelectMultiple(
                'Known directly', False, attrs={'style': 'height:100px'}
            ),
            'known_indirectly': FilteredSelectMultiple(
                'Known indirectly', False, attrs={'style': 'height:100px'}
            ),
            'locations': FilteredSelectMultiple(
                'Locations', False, attrs={'style': 'height:100px'}
            ),
            'pictures': FilteredSelectMultiple(
                'Pictures', False, attrs={'style': 'height:100px'}
            ),
            'threads': FilteredSelectMultiple(
                'Threads', False, attrs={'style': 'height:100px'}
            ),
            'debates': FilteredSelectMultiple(
                'Debates', False, attrs={'style': 'height:100px'}
            ),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['threads'].label = 'Active Threads'
        self.fields['threads'].queryset = ThreadActive.objects.all()
        self.fields['known_directly'].queryset = Profile.objects.exclude(
            Q(status='dead_player') | Q(status='dead_npc') | Q(status='gm')
        )
        self.fields['known_indirectly'].queryset = Profile.objects.exclude(
            Q(status='dead_player') | Q(status='dead_npc') | Q(status='gm')
        )


class GameEventAdmin(admin.ModelAdmin):
    form = GameEventAdminForm
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 12, 'cols': 40})},
    }
    list_display = ['id', 'game', 'event_no_in_game', 'date_in_period',
                    'description_short', 'description_long', 'audio']
    list_editable = ['event_no_in_game', 'description_short',
                     'description_long', 'audio']
    list_filter = ['game']
    search_fields = ['description_short', 'description_long']
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        request = kwargs['request']
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        fields = [
            # Tested that here only audio optimazes queries
            'audio',
        ]
        for field in fields:
            if db_field.name == field:
                choices = getattr(request, f'_{field}_choices_cache', None)
                if choices is None:
                    choices = list(formfield.choices)
                    setattr(request, f'_{field}_choices_cache', choices)
                formfield.choices = choices
        return formfield
    
    
class GameEventInlineForm(GameEventAdminForm):
    exclude = ['game']
    
    
class GameEventInline(admin.TabularInline):
    model = GameEvent
    extra = 0
    form = GameEventInlineForm
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 12, 'cols': 45})},
        CharField: {'widget': TextInput(attrs={'size': 15})},
        ForeignKey: {'widget': Select(attrs={'style': 'width:180px'})},
        OneToOneField: {'widget': Select(attrs={'style': 'width:200px'})},
    }
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        # https://blog.ionelmc.ro/2012/01/19/tweaks-for-making-django-admin-faster/
        # Reduces greatly queries in main view, doubles in detail view
        # The trade-off is still very good
        request = kwargs['request']
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        fields = [
            'date_start',
            'date_end',
            'in_timeunit',
            'known_directly',
            'known_indirectly',
            'locations',
            'threads',    # To allow for filtering in GameEventAdminForm
            'pictures',
            'audio',
        ]
        for field in fields:
            if db_field.name == field:
                choices = getattr(request, f'_{field}_choices_cache', None)
                if choices is None:
                    choices = list(formfield.choices)
                    setattr(request, f'_{field}_choices_cache', choices)
                formfield.choices = choices
        return formfield
    
    
class HistoryEventAdminForm(forms.ModelForm):
    class Meta:
        model = GameEvent
        fields = ['date_start', 'date_end', 'in_timeunit', 'description_short',
                  'description_long', 'threads', 'locations',
                  'known_short_desc', 'known_long_desc', 'pictures']
        widgets = {
            'known_short_desc': FilteredSelectMultiple(
                'Known directly', False, attrs={'style': 'height:100px'}
            ),
            'known_long_desc': FilteredSelectMultiple(
                'Known indirectly', False, attrs={'style': 'height:100px'}
            ),
            'locations': FilteredSelectMultiple(
                'Locations', False, attrs={'style': 'height:100px'}
            ),
            'pictures': FilteredSelectMultiple(
                'Pictures', False, attrs={'style': 'height:100px'}
            ),
            'threads': FilteredSelectMultiple(
                'Threads', False, attrs={'style': 'height:100px'}
            ),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['threads'].label = 'Active Threads'
        self.fields['threads'].queryset = ThreadActive.objects.all()
        self.fields['known_short_desc'].queryset = Profile.objects.exclude(
            Q(status='dead_player') | Q(status='dead_npc') | Q(status='gm')
        )
        self.fields['known_long_desc'].queryset = Profile.objects.exclude(
            Q(status='dead_player') | Q(status='dead_npc') | Q(status='gm')
        )
        
        
class HistoryEventAdmin(admin.ModelAdmin):
    form = HistoryEventAdminForm
    list_display = ['id', 'date_in_period', 'date_in_era',
                    'date_in_chronology', 'description_short',
                    'description_long', 'audio']
    list_editable = ['description_short', 'description_long', 'audio']
    search_fields = ['description_short', 'description_long']
    
    
# ----------------------------------------------
# ----------------------------------------------
# -------- GameSession, Chapter & Thread -------
# ----------------------------------------------
# ----------------------------------------------


class GameSessionAdmin(admin.ModelAdmin):
    inlines = [GameEventInline]
    list_display = ['game_no', 'title', 'chapter', 'date']
    list_editable = ['title', 'chapter', 'date']
    list_select_related = ['chapter']
    ordering = ['-game_no']
    search_fields = ['title']
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        # https://blog.ionelmc.ro/2012/01/19/tweaks-for-making-django-admin-faster/
        # Reduces greatly queries in main view, doubles in detail view
        # The trade-off is still very good
        request = kwargs['request']
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        fields = [
            'chapter',
        ]
        for field in fields:
            if db_field.name == field:
                choices = getattr(request, f'_{field}_choices_cache', None)
                if choices is None:
                    choices = list(formfield.choices)
                    setattr(request, f'_{field}_choices_cache', choices)
                formfield.choices = choices
        return formfield
    
    
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['chapter_no', 'title', 'image']
    list_editable = ['title', 'image']
    search_fields = ['title']
    select_related = ['image']


class ThreadAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_ended']
    list_editable = ['name', 'is_ended']
    search_fields = ['name']


class ThreadActiveAdmin(ThreadAdmin):
    pass


class ThreadEndedAdmin(ThreadAdmin):
    pass


# ----------------------------------------------
# ----------------------------------------------
# ---------- Chronology, Era & Period ----------
# ----------------------------------------------
# ----------------------------------------------


class ChronologyAdminForm(forms.ModelForm):
    class Meta:
        model = TimeUnit
        fields = ['name', 'name_genetive', 'date_start', 'date_end',
                  'description_short', 'description_long',
                  'known_short_desc', 'known_long_desc']
        widgets = {
            'known_short_desc': FilteredSelectMultiple(
                'Known short desc', False, attrs={'style': 'height:200px'}
            ),
            'known_long_desc': FilteredSelectMultiple(
                'Known long desc', False, attrs={'style': 'height:200px'}
            ),
        }


class ChronologyAdmin(admin.ModelAdmin):
    form = ChronologyAdminForm


class TimeSpanForm(forms.ModelForm):
    class Meta:
        model = TimeUnit
        fields = ['name', 'name_genetive', 'date_start', 'date_end',
                  'in_timeunit', 'description_short', 'description_long',
                  'known_short_desc', 'known_long_desc']
        widgets = {
            'known_short_desc': FilteredSelectMultiple(
                'Known short desc', False, attrs={'style': 'height:200px'}
            ),
            'known_long_desc': FilteredSelectMultiple(
                'Known long desc', False, attrs={'style': 'height:200px'}
            ),
        }


class EraAdminForm(TimeSpanForm):
    in_timeunit = forms.ModelChoiceField(queryset=Chronology.objects.all())


class EraAdmin(admin.ModelAdmin):
    form = EraAdminForm
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 15, 'cols': 40})},
        CharField: {'widget': TextInput(attrs={'size': 12})},
        ForeignKey: {'widget': Select(attrs={'style': 'width:180px'})},
    }
    list_display = ['id', 'name', 'name_genetive', 'date_start', 'date_end',
                    'in_timeunit', 'description_short', 'description_long']
    list_editable = ['name', 'name_genetive', 'date_start', 'date_end',
                     'in_timeunit', 'description_short', 'description_long']
    search_fields = ['name', 'name_genetive', 'description_short',
                     'description_long']
    # Now that 1 obj exists, no visible effect of select_related, check later
    # select_related = ['date_start', 'date_end', 'in_timeunit']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('date_start', 'date_end', 'in_timeunit')
        return qs


class PeriodAdminForm(TimeSpanForm):
    in_timeunit = forms.ModelChoiceField(queryset=Era.objects.all())
    locations = forms.ModelMultipleChoiceField(
        queryset=SecondaryLocation.objects.filter(
            location_type__name='Kraina'),
        required=False,
        widget=FilteredSelectMultiple('Secondary locations', False),
    )


class PeriodAdmin(admin.ModelAdmin):
    form = PeriodAdminForm


# Chronicle models
admin.site.register(Thread, ThreadAdmin)
admin.site.register(ThreadActive, ThreadActiveAdmin)
admin.site.register(ThreadEnded, ThreadEndedAdmin)
admin.site.register(Date)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(GameSession, GameSessionAdmin)

# TimeUnit model
admin.site.register(TimeUnit)

# TimeUnit proxies
admin.site.register(Chronology, ChronologyAdmin)
admin.site.register(Era, EraAdmin)
admin.site.register(Period, PeriodAdmin)
admin.site.register(HistoryEvent, HistoryEventAdmin)
admin.site.register(GameEvent, GameEventAdmin)
