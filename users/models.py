from PIL import Image
from django.contrib.auth.models import User
from django.db.models import (
    BooleanField,
    CASCADE,
    Case,
    CharField,
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
    user = OneToOneField(to=User, on_delete=CASCADE)
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
    copied_character_name = CharField(max_length=100, blank=True, null=True)

    objects = Manager()
    non_gm = NonGMProfileManager()
    players = PlayerProfileManager()
    active_players = ActivePlayerProfileManager()
    npcs = NPCProfileManager()
    living = LivingProfileManager()
    contactables = ContactableProfileManager()

    class Meta:
        ordering = ['-status', '-is_active', 'user__username']
    
    def __str__(self):
        return self.copied_character_name or self.user.username

    def save(self, *args, **kwargs):
        first_save = True if not self.pk else False
        super().save(*args, **kwargs)
        if first_save and self.image:
            img = Image.open(self.image.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)
       
    @staticmethod
    def _characters_all_related(qs):
        qs = qs.prefetch_related('known_directly', 'known_indirectly')
        qs = qs.select_related('profile')
        return qs

    def characters_all_known(self):
        if self.can_view_all:
            print('characters_all_known')
            from prosoponomikon.models import Character
            qs = Character.objects.all()
        else:
            known_dir = self.characters_known_directly.all()
            known_indir = self.characters_known_indirectly.all()
            qs = (known_dir | known_indir).distinct()
        return self._characters_all_related(qs).exclude(id=self.character.id)
    
    def characters_known_only_indirectly(self):
        if self.can_view_all:
            print('characters_known_only_indirectly')
            from prosoponomikon.models import Character
            qs = Character.objects.none()
        else:
            known_dir = self.characters_known_directly.all()
            known_indir = self.characters_known_indirectly.all()
            qs = known_indir.exclude(id__in=known_dir)
        return self._characters_all_related(qs).exclude(id=self.character.id)

    def characters_all_known_annotated_if_indirectly(self):
        from prosoponomikon.models import Character
        if self.can_view_all:
            print('characters_all_known_annotated_if_indirectly')
            qs = Character.objects.all()
        else:
            known_only_indir = self.characters_known_only_indirectly()
            all_known = self.characters_all_known()
            qs = all_known.annotate(
                only_indirectly=Case(
                    When(id__in=known_only_indir, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
            )
        return self._characters_all_related(qs).exclude(id=self.character.id)

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
        print(last_news_answers_unseen)
        
        news_with_unseen_last_answer = allowed.filter(
            news_answers__in=last_news_answers_unseen)

        return news_with_unseen_last_answer
    
    @property
    def unseen_surveys(self):
        from news.models import SurveyAnswer
        allowed = self.surveys_received.exclude(author=self)
        surveys_unseen = allowed.exclude(seen_by=self)
        
        allowed_annotated = allowed.annotate(
            last_answer_id=Max('survey_answers__id')
        ).filter(survey_answers__id=F('last_answer_id'))
        
        last_survey_answers_ids = [survey.last_answer_id for survey in allowed_annotated]
        last_survey_answers_unseen = SurveyAnswer.objects.filter(
            id__in=last_survey_answers_ids).filter(~Q(seen_by=self))
        
        surveys_with_unseen_last_answer = allowed.filter(
            survey_answers__in=last_survey_answers_unseen)
            
        return (surveys_unseen | surveys_with_unseen_last_answer).distinct()

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
