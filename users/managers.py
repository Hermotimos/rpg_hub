from django.db.models import Manager


class NonGMProfileManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(status__in=['player', 'npc'])
        return qs


class PlayerProfileManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(status__icontains='player')


class ActivePlayerProfileManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(status__icontains='player', is_active=True)


class GMControlledProfileManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.exclude(status__icontains='player', is_active=True)


class NPCProfileManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(status__icontains='npc')


class LivingProfileManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(status__in=['player', 'npc'])
        qs = qs.filter(is_alive=True)
        return qs


class ContactableProfileManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(status__in=['gm', 'player'])
        qs = qs.filter(is_active=True)
        return qs
