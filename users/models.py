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
    OneToOneField,
    Prefetch,
    Value,
    When,
)

from rpg_project.utils import ReplaceFileStorage
from users.managers import ActivePlayerProfileManager, NonGMProfileManager, \
    ContactableProfileManager, LivingProfileManager, NPCProfileManager, \
    PlayerProfileManager

STATUS = [
    ('gm', 'MG'),
    ('npc', 'BN'),
    ('player', 'GRACZ'),
    ('spectator', 'WIDZ'),
]


class Profile(Model):
    # user = OneToOneField(to=User, on_delete=CASCADE)
    user_fk = FK(to=User, related_name='profiles', on_delete=CASCADE, default=1)
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
    players = PlayerProfileManager()
    active_players = ActivePlayerProfileManager()
    npcs = NPCProfileManager()
    living = LivingProfileManager()
    contactables = ContactableProfileManager()

    class Meta:
        ordering = ['-status', '-is_active', 'user_fk__username']
    
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
            'characters__profile__user_fk',
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

    @property
    def undone_demands(self):
        demands = self.received_demands.exclude(author=self)
        return demands.exclude(is_done=True)
    
    @property
    def unseen_news(self):
        from news.models import NewsAnswer
        allowed = self.allowed_news.all()
        
        allowed_annotated = allowed.annotate(
            last_answer_id=Max('news_answers')
        ).filter(news_answers__id=F('last_answer_id'))
        
        last_news_answers_ids = [news.last_answer_id for news in allowed_annotated]
        last_news_answers_unseen = NewsAnswer.objects.filter(
            id__in=last_news_answers_ids).filter(~Q(seen_by=self))
        
        news_with_unseen_last_answer = allowed.filter(
            news_answers__in=last_news_answers_unseen)

        return news_with_unseen_last_answer

    @property
    def unseen_announcements(self):
        from communications.models import Announcement, Statement
        unseen_statements = Statement.objects.exclude(seen_by=self)
        return Announcement.objects.filter(statements__in=unseen_statements)
        
    @property
    def unseen_debates(self):
        from debates.models import Remark, Debate
        if self.status == 'gm':
            allowed = Debate.objects.all()
        else:
            allowed = self.debates_known_directly.all()
        
        allowed_annotated = allowed.annotate(
            last_remark_id=Max('remarks__id')
        ).filter(remarks__id=F('last_remark_id'))
        
        last_remarks_ids = [debate.last_remark_id for debate in allowed_annotated]
        last_remarks_unseen = Remark.objects.filter(
            id__in=last_remarks_ids).filter(~Q(seen_by=self))

        debates_with_unseen_last_remark = allowed.filter(
            remarks__in=last_remarks_unseen)

        return debates_with_unseen_last_remark

    @property
    def can_view_all(self):
        return self.status in ['gm', 'spectator']
    
    @property
    def can_action(self):
        return self.status in ['gm', 'player']
