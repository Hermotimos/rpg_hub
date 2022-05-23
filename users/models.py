from PIL import Image
from django.contrib.auth.models import User
from django.db.models import (
    BooleanField,
    CASCADE,
    Case,
    CharField,
    ForeignKey as FK,
    ImageField,
    IntegerField,
    Manager,
    Model,
    Prefetch,
    Value,
    When,
)

from rpg_project.utils import ReplaceFileStorage
from users.managers import ActivePlayerProfileManager, NonGMProfileManager, \
    ContactableProfileManager, LivingProfileManager, NPCProfileManager, \
    PlayerProfileManager, GMControlledProfileManager


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
        storage=ReplaceFileStorage(),
    )
    user_image = ImageField(
        default='profile_pics/profile_default.jpg',
        upload_to='user_pics',
        blank=True,
        null=True,
        storage=ReplaceFileStorage(),
    )
    # TODO delete after more testing (along signal in prosoponomikon.models)
    character_name_copy = CharField(max_length=100, blank=True, null=True)

    objects = Manager()
    non_gm = NonGMProfileManager()
    gm_controlled = GMControlledProfileManager()
    players = PlayerProfileManager()
    active_players = ActivePlayerProfileManager()
    npcs = NPCProfileManager()
    living = LivingProfileManager()
    contactables = ContactableProfileManager()

    class Meta:
        ordering = ['-status', '-is_active', 'character__fullname']
    
    def __str__(self):
        return self.character.fullname or self.user.username

    def save(self, *args, **kwargs):
        first_save = True if not self.pk else False
        super().save(*args, **kwargs)
        if first_save and self.image:
            img = Image.open(self.image.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)
                
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
        qs = qs.select_related('main_image__image')
        return qs

    def skills_acquired_with_skill_levels(self):
        from rules.models import Skill, SkillLevel
        skills = Skill.objects.filter(skill_levels__acquired_by=self)
        skill_levels = SkillLevel.objects.filter(acquired_by=self)
        skills = skills.prefetch_related(
            Prefetch('skill_levels', queryset=skill_levels),
            'skill_levels__perks__conditional_modifiers__conditions',
            'skill_levels__perks__conditional_modifiers__combat_types',
            'skill_levels__perks__conditional_modifiers__modifier__factor',
            'skill_levels__perks__comments'
        ).distinct()
        return skills

    def synergies_acquired_with_synergies_levels(self):
        from rules.models import Synergy, SynergyLevel, SkillLevel
        skill_levels = SkillLevel.objects.filter(acquired_by=self)
    
        synergy_levels = SynergyLevel.objects.prefetch_related('skill_levels')
        synergy_levels_ids = [
            synergy_lvl.id for synergy_lvl in synergy_levels
            if all([(skill_lvl in skill_levels) for skill_lvl in
                    synergy_lvl.skill_levels.all()])
        ]
        synergy_levels = SynergyLevel.objects.filter(id__in=synergy_levels_ids)
        synergy_levels = synergy_levels.prefetch_related(
            'synergy__skills',
            'perks__conditional_modifiers__conditions',
            'perks__conditional_modifiers__combat_types',
            'perks__conditional_modifiers__modifier__factor',
            'perks__comments',
            'skill_levels__skill',
        )
        synergies = Synergy.objects.filter(synergy_levels__in=synergy_levels)
        synergies = synergies.prefetch_related(
            Prefetch('synergy_levels', queryset=synergy_levels))
        return synergies.distinct()

    def synergies_allowed(self):
        """Get synergies whose all composing skills are allowed to any od user's profiles."""
        from rules.models import Synergy, Skill
        skills = Skill.objects.filter(allowees__in=self.user.profiles.all())
        synergies = Synergy.objects.prefetch_related(
            'skills',
            'synergy_levels__skill_levels__skill',
            'synergy_levels__perks__conditional_modifiers__conditions',
            'synergy_levels__perks__conditional_modifiers__combat_types',
            'synergy_levels__perks__conditional_modifiers__modifier__factor',
            'synergy_levels__perks__comments',
        )
        return [
            synergy for synergy in synergies
            if all([(skill in skills) for skill in synergy.skills.all()])
        ]

    @property
    def undone_demands(self):
        demands = self.received_demands.exclude(author=self)
        return demands.exclude(is_done=True)

    @property
    def unseen_announcements(self):
        from communications.models import Announcement, Statement
        unseen_statements = Statement.objects.exclude(seen_by=self)
        return Announcement.objects.filter(
            participants=self,
            statements__in=unseen_statements)
        
    @property
    def unseen_debates(self):
        from communications.models import Statement, Debate
        unseen_remarks = Statement.objects.exclude(seen_by=self)
        return Debate.objects.filter(
            participants=self,
            statements__in=unseen_remarks).distinct()

    @property
    def can_view_all(self):
        return self.status in ['gm', 'spectator']
    
    @property
    def can_action(self):
        return self.status in ['gm', 'player']


# -----------------------------------------------------------------------------
# Provide User with method to get Profile-s with prefetched Character-s

def get_profiles(self):
    user_profiles = self.profiles.select_related('character')
    return user_profiles.order_by('status', 'character__fullname')


User.add_to_class("get_profiles", get_profiles)
