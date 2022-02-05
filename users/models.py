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
    F, Max, Q,
    Model,
    Prefetch,
    Value,
    When,
)

from rpg_project.utils import ReplaceFileStorage
from users.managers import ActivePlayerProfileManager, NonGMProfileManager, \
    ContactableProfileManager, LivingProfileManager, NPCProfileManager, \
    PlayerProfileManager, GMControlledProfileManager

STATUS = [
    ('gm', 'MG'),
    ('npc', 'BN'),
    ('player', 'GRACZ'),
    ('spectator', 'WIDZ'),
]


class Profile(Model):
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
    # Character name copied from Character (by signal) to avoid queries
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
        ordering = ['-status', '-is_active', 'character_name_copy']
    
    def __str__(self):
        return self.character_name_copy or self.user.username

    def save(self, *args, **kwargs):
        first_save = True if not self.pk else False
        super().save(*args, **kwargs)
        if first_save and self.image:
            img = Image.open(self.image.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)
       
    def characters_all_known_annotated_if_indirectly(self):
        from prosoponomikon.models import Character
        if self.can_view_all:
            qs = Character.objects.all()
        else:
            known_dir = self.characters_known_directly.all()
            known_indir = self.characters_known_indirectly.all()
            known_only_indir = known_indir.exclude(id__in=known_dir)
            all_known = (known_dir | known_indir).distinct()
            qs = all_known.annotate(
                only_indirectly=Case(
                    When(id__in=known_only_indir, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                ))
        qs = qs.prefetch_related('known_directly', 'known_indirectly')
        qs = qs.select_related('profile')
        qs = qs.exclude(id=self.character.id)
        return qs
    
    def locations_all_known_annotated_if_indirectly(self):
        if self.can_view_all:
            from toponomikon.models import Location
            qs = Location.objects.all()
        else:
            known_dir = self.locs_known_directly.all()
            known_indir = self.locs_known_indirectly.all()
            known_only_indir = known_indir.exclude(id__in=known_dir)
            all_known = (known_dir | known_indir).distinct()
            qs = all_known.annotate(
                only_indirectly=Case(
                    When(id__in=known_only_indir, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                ))
        qs = qs.prefetch_related('known_directly', 'known_indirectly')
        qs = qs.select_related('main_image__image')
        return qs

    def characters_groups_authored_with_characters(self):
        characters = self.characters_all_known_annotated_if_indirectly()
        character_groups = self.character_groups_authored.all()
        character_groups = character_groups.prefetch_related(
            Prefetch('characters', queryset=characters),
            'characters__profile__user',
            'characters__known_directly',
            'characters__known_indirectly',
            'characters__first_name')
        return character_groups

    def skills_acquired_with_skill_levels(self):
        from rules.models import Skill, SkillLevel
        skills = Skill.objects.filter(skill_levels__acquired_by=self)
        skill_levels = SkillLevel.objects.filter(acquired_by=self)
        skills = skills.prefetch_related(
            Prefetch('skill_levels', queryset=skill_levels))
        return skills.distinct()

    def synergies_acquired_with_synergies_levels(self):
        from rules.models import Synergy, SynergyLevel
        synergies = Synergy.objects.filter(synergy_levels__acquired_by=self)
        synergy_levels = SynergyLevel.objects.filter(acquired_by=self)
        synergies = synergies.prefetch_related(
            Prefetch('synergy_levels', queryset=synergy_levels))
        return synergies.distinct()

    @property
    def undone_demands(self):
        demands = self.received_demands.exclude(author=self)
        return demands.exclude(is_done=True)

    @property
    def unseen_announcements(self):
        from communications.models import Announcement, Statement
        unseen_statements = Statement.objects.exclude(seen_by=self)
        return Announcement.objects.filter(
            known_directly=self,
            statements__in=unseen_statements)
        
    @property
    def unseen_debates(self):
        from communications.models import Statement, Debate
        unseen_remarks = Statement.objects.exclude(seen_by=self)
        return Debate.objects.filter(
            known_directly=self,
            statements__in=unseen_remarks).distinct()

    @property
    def can_view_all(self):
        return self.status in ['gm', 'spectator']
    
    @property
    def can_action(self):
        return self.status in ['gm', 'player']
