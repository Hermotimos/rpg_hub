from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import TextField, CharField, ForeignKey, OneToOneField
from django.forms import Textarea, TextInput, Select
from rpg_project.utils import formfield_for_dbfield_cached
from chronicles.models import (
    PlotThread,
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
                  'plot_threads', 'locations', 'known_directly',
                  'known_indirectly', 'picture_sets', 'debates', 'audio']
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
            'picture_sets': FilteredSelectMultiple(
                'Picture Sets', False, attrs={'style': 'height:100px'}
            ),
            'plot_threads': FilteredSelectMultiple(
                'PlotThreads', False, attrs={'style': 'height:100px'}
            ),
            'debates': FilteredSelectMultiple(
                'Debates', False, attrs={'style': 'height:100px'}
            ),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['plot_threads'].label = 'Active PlotThreads'
        self.fields['known_directly'].queryset = Profile.non_gm.all()
        self.fields['known_indirectly'].queryset = Profile.non_gm.all()


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
        fields = [
            'audio',    # Tested that here only audio optimizes queries
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)
    
    
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
        fields = [
            'date_start',
            'date_end',
            'in_timeunit',
            'known_directly',
            'known_indirectly',
            'locations',
            'plot_threads',    # To allow for filtering in GameEventAdminForm
            'picture_sets',
            'audio',
            'debates',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)
    
    
class HistoryEventAdminForm(forms.ModelForm):
    class Meta:
        model = GameEvent
        fields = ['date_start', 'date_end', 'in_timeunit', 'description_short',
                  'description_long', 'plot_threads', 'locations',
                  'known_short_desc', 'known_long_desc']
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
            'picture_sets': FilteredSelectMultiple(
                'Picture Sets', False, attrs={'style': 'height:100px'}
            ),
            'plot_threads': FilteredSelectMultiple(
                'PlotThreads', False, attrs={'style': 'height:100px'}
            ),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['plot_threads'].label = 'Active PlotThreads'
        self.fields['known_short_desc'].queryset = Profile.non_gm.all()
        self.fields['known_long_desc'].queryset = Profile.non_gm.all()
        
        
class HistoryEventAdmin(admin.ModelAdmin):
    form = HistoryEventAdminForm
    list_display = ['id', 'date_in_period', 'date_in_era',
                    'date_in_chronology', 'description_short',
                    'description_long', 'audio']
    list_editable = ['description_short', 'description_long', 'audio']
    search_fields = ['description_short', 'description_long']
    
    
# ----------------------------------------------
# ----------------------------------------------
# ------ GameSession, Chapter & PlotThread -----
# ----------------------------------------------
# ----------------------------------------------


class GameSessionAdmin(admin.ModelAdmin):
    formfield_overrides = {
        CharField: {'widget': TextInput(attrs={'size': 70})},
    }
    inlines = [GameEventInline]
    list_display = ['game_no', 'title', 'chapter', 'date']
    list_editable = ['title', 'chapter', 'date']
    list_select_related = ['chapter']
    ordering = ['-game_no']
    search_fields = ['title']

    def formfield_for_dbfield(self, db_field, **kwargs):
        fields = [
            'chapter',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)

    
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['chapter_no', 'title', 'image']
    list_editable = ['title', 'image']
    search_fields = ['title']
    select_related = ['image']


class PlotThreadAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_ended']
    list_editable = ['name', 'is_ended']
    list_filter = ['is_ended']
    search_fields = ['name']


# ----------------------------------------------
# ----------------------------------------------
# ---------- Chronology, Era & Period ----------
# ----------------------------------------------
# ----------------------------------------------

class TimeUnitAdmin(admin.ModelAdmin):
    list_display = ['id', 'description_short', 'description_long']
    search_fields = ['description_short', 'description_long']
    

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

    def formfield_for_dbfield(self, db_field, **kwargs):
        fields = [
            'date_start',
            'date_end',
            'in_timeunit',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)
    
    
class PeriodAdminForm(TimeSpanForm):
    in_timeunit = forms.ModelChoiceField(queryset=Era.objects.all())
    locations = forms.ModelMultipleChoiceField(
        queryset=SecondaryLocation.objects.filter(
            location_type__name='Kraina'),
        required=False,
        widget=FilteredSelectMultiple('Secondary locations', False),
    )


class PeriodAdmin(EraAdmin):
    form = PeriodAdminForm
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

    def formfield_for_dbfield(self, db_field, **kwargs):
        fields = [
            'date_start',
            'date_end',
            'in_timeunit',
        ]
        return formfield_for_dbfield_cached(self, db_field, fields, **kwargs)


# Chronicle models
admin.site.register(PlotThread, PlotThreadAdmin)
admin.site.register(Date)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(GameSession, GameSessionAdmin)

# TimeUnit model
admin.site.register(TimeUnit, TimeUnitAdmin)

# TimeUnit proxies
admin.site.register(Chronology, ChronologyAdmin)
admin.site.register(Era, EraAdmin)
admin.site.register(Period, PeriodAdmin)
admin.site.register(HistoryEvent, HistoryEventAdmin)
admin.site.register(GameEvent, GameEventAdmin)
