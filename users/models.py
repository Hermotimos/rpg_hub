from django.contrib.auth.models import User
from django.db.models import (
    BooleanField,
    CASCADE,
    Case,
    CharField,
    ForeignKey as FK,
    ImageField,
    IntegerField,
    Model,
    Prefetch,
    Q,
    Value,
    When,
)

from users import managers
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


class Profile(Model):
    STATUS = [
        ('gm', 'MG'),
        ('npc', 'BN'),
        ('player', 'GRACZ'),
        ('spectator', 'WIDZ'),
    ]
    
    user = FK(to=User, related_name='profiles', on_delete=CASCADE, default=1)
    status = CharField(max_length=50, choices=STATUS, default='npc')
    is_alive = BooleanField(default=True)
    is_active = BooleanField(default=True)
    image = ImageField(
        default='profile_pics/profile_default.jpg',
        upload_to='profile_pics',
        blank=True,
        null=True,
    )
    user_image = ImageField(
        default='profile_pics/profile_default.jpg',
        upload_to='user_pics',
        blank=True,
        null=True,
    )

    objects = managers.ProfileManager()
    non_gm = managers.NonGMProfileManager()
    gm_controlled = managers.GMControlledProfileManager()
    players = managers.PlayerProfileManager()
    active_players = managers.ActivePlayerProfileManager()
    npcs = managers.NPCProfileManager()
    living = managers.LivingProfileManager()
    contactables = managers.ContactableProfileManager()

    class Meta:
        ordering = ['-status', '-is_active', 'character__fullname']
    
    def __str__(self):
        try:
            return str(self.character.fullname)
        except ObjectDoesNotExist:
            return f"[{self.user.username}]: assign Character!"
    
    @property
    def user_img_url(self):
        try:
            return self.user_image.url
        except ValueError:
            return f"{settings.STATIC_URL}img/profile_default.jpg"
        
    def gameevents_known_annotated(self):
        """Get GameEvent set known to the profile, annotate if GameEvent
        is known only indirectly.
        """
        from chronicles.models import GameEvent
        if self.can_view_all:
            qs = GameEvent.objects.all()
        else:
            known_dir = GameEvent.objects.filter(participants=self)
            known_indir = GameEvent.objects.filter(informees=self)
            known_only_indir = known_indir.exclude(id__in=known_dir)
            all_known = (known_dir | known_indir).distinct()
            qs = all_known.annotate(
                only_indirectly=Case(
                    When(id__in=known_only_indir, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                ))
        return qs

    def characters_known_annotated(self):
        """Get Character set known to the profile, annotate if Character
        is known only indirectly.
        """
        from prosoponomikon.models import Character
        if self.can_view_all:
            qs = Character.objects.all()
        else:
            known_dir = self.characters_participated.all()
            known_indir = self.characters_informed.all()
            known_only_indir = known_indir.exclude(id__in=known_dir)
            all_known = (known_dir | known_indir).distinct()
            qs = all_known.annotate(
                only_indirectly=Case(
                    When(id__in=known_only_indir, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                ))
        qs = qs.prefetch_related('participants', 'informees')
        qs = qs.select_related('profile')
        qs = qs.exclude(id=self.character.id)
        return qs
    
    def locations_known_annotated(self):
        """Get Location set known to the profile, annotate if Location
        is known only indirectly.
        """
        if self.can_view_all:
            from toponomikon.models import Location
            qs = Location.objects.all()
        else:
            known_dir = self.locations_participated.all()
            known_indir = self.locations_informed.all()
            known_only_indir = known_indir.exclude(id__in=known_dir)
            all_known = (known_dir | known_indir).distinct()
            qs = all_known.annotate(
                only_indirectly=Case(
                    When(id__in=known_only_indir, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                ))
        qs = qs.prefetch_related('participants', 'informees')
        qs = qs.select_related('main_image__image', 'location_type')
        return qs

    def synergies_allowed(self, skilltype_kind):
        """Get synergies whose all composing skills are allowed to any od user's profiles."""
        from rules.models import Synergy, RegularSynergy, MentalSynergy, Skill
        
        skills = Skill.objects.filter(types__kinds__name=skilltype_kind)
        skills = skills.exclude(~Q(allowees__in=self.user.profiles.all()))

        if skilltype_kind == "Powszechne":
            synergies = RegularSynergy.objects.all()
        elif skilltype_kind == "Mentalne":
            synergies = MentalSynergy.objects.all()
        else:
            synergies = Synergy.objects.none()

        synergies = synergies.filter(skills__in=skills)
        synergies = synergies.prefetch_related(
            'skills',
            'synergy_levels__skill_levels__skill',
            'synergy_levels__perks__conditional_modifiers__conditions',
            'synergy_levels__perks__conditional_modifiers__combat_types',
            'synergy_levels__perks__conditional_modifiers__modifier__factor',
            'synergy_levels__perks__comments',
        )
        return synergies

    @property
    def undone_demands(self):
        demands = self.received_demands.exclude(author=self)
        return demands.exclude(is_done=True)

    @property
    def unseen_announcements(self):
        from communications.models import AnnouncementStatement
        announcements = self.threads_participated.filter(
            kind="Announcement",
            statements__in=AnnouncementStatement.objects.exclude(seen_by=self))
        if self.status == 'gm':
            return announcements.filter(participants=self)
        return announcements

    @property
    def unseen_debates(self):
        from communications.models import DebateStatement
        debates = self.threads_participated.filter(
            kind="Debate",
            statements__in=DebateStatement.objects.exclude(seen_by=self))
        if self.status != 'gm':
            return debates.filter(participants=self)
        return debates

    @property
    def can_view_all(self):
        return self.status in ['gm', 'spectator']
    
    @property
    def can_action(self):
        return self.status in ['gm', 'player'] and self.is_active


# -----------------------------------------------------------------------------
# Provide User with method to get Profile-s with prefetched Character-s

def get_profiles(self):
    user_profiles = self.profiles.select_related('character')
    return user_profiles.order_by('status', 'character__fullname')


User.add_to_class("get_profiles", get_profiles)
