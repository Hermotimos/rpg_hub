from django.contrib import admin

from communications.models import AnnouncementStatement
from users.models import Profile, User


class AnnouncementStatementAuthorFilter(admin.SimpleListFilter):
    title = 'author'
    parameter_name = 'author'
    
    def lookups(self, request, model_admin):
        announcement_statements = AnnouncementStatement.objects.all()
        authors = User.objects.filter(
            profiles__in=Profile.objects.filter(statements__in=announcement_statements))
        return [(user.id, user.username) for user in authors]
    
    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(author__user__id=self.value())
        return queryset


class DebateStatementAuthorFilter(admin.SimpleListFilter):
    title = 'author'
    parameter_name = 'author'
    
    def lookups(self, request, model_admin):
        authors = Profile.objects.exclude(statements=None)
        return [
            (profile.id, profile.character_name_copy) for profile in authors]
    
    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(author__id__exact=self.value())
        return queryset
