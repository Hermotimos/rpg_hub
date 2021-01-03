from django.contrib import admin
from django.db.models import TextField, CharField
from django.forms import Textarea, TextInput
from django.utils.html import format_html

from prosoponomikon.models import Persona, PlayerPersona, NonPlayerPersona, \
    PersonaGroup


class PersonaAdmin(admin.ModelAdmin):
    list_display = ['get_img', 'name', 'birth_location', 'description']
    list_editable = ['name', 'birth_location', 'description']
    search_fields = ['name', 'description']
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 50})},
        CharField: {'widget': TextInput(attrs={'size': 25})},
    }

    def formfield_for_dbfield(self, db_field, **kwargs):
        # https://blog.ionelmc.ro/2012/01/19/tweaks-for-making-django-admin-faster/
        # Reduces greatly queries in main view, doubles in detail view
        # The trade-off is still very good
        request = kwargs['request']
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        fields = [
            'birth_location',
        ]
        for field in fields:
            if db_field.name == field:
                choices = getattr(request, f'_{field}_choices_cache', None)
                if choices is None:
                    choices = list(formfield.choices)
                    setattr(request, f'_{field}_choices_cache', choices)
                formfield.choices = choices
        return formfield
    
    def get_img(self, obj):
        if obj.profile.image:
            return format_html(
                f'<img src="{obj.profile.image.url}" width="70" height="70">'
            )
        default_img = "media/profile_pics/profile_default.jpg"
        return format_html(f'<img src={default_img} width="70" height="70">')


admin.site.register(PersonaGroup)
admin.site.register(Persona, PersonaAdmin)
admin.site.register(PlayerPersona, PersonaAdmin)
admin.site.register(NonPlayerPersona, PersonaAdmin)
