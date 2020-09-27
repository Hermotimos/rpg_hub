from django.contrib import admin
from django.db.models import Case, When, Value
from django.utils.html import format_html

from users.models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['get_img', 'user', 'character_name', 'status', 'image']
    list_editable = ['character_name', 'status', 'image']
    list_filter = ['status']
    search_fields = ['user', 'character_name']

    def get_img(self, obj):
        if obj.image:
            return format_html(
                f'<img src="{obj.image.url}" width="70" height="70">'
            )
        default_img = "media/profile_pics/profile_default.jpg"
        return format_html(f'<img src={default_img} width="70" height="70">')

    # TODO This is not working. Generally should be reworked, but it's huge...
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.order_by(
            Case(
                When(status='active_player', then=Value(0)),
                When(status='inactive_player', then=Value(1)),
                When(status='dead_player', then=Value(2)),
                When(status='living_npc', then=Value(3)),
                When(status='dead_npc', then=Value(4)),
                When(status='gm', then=Value(5)),
                default=Value(100)
            )
        )
        print(qs)
        return qs


admin.site.register(Profile, ProfileAdmin)
