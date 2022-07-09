from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from associations.models import Comment
from knowledge.models import KnowledgePacket
from rpg_project.utils import auth_profile
from users.models import Profile


@login_required
@auth_profile(['gm'])
def comments_view(request):
    current_profile = request.current_profile
    
    comments = Comment.objects.select_related('author__character',
                                              'content_type')
    # Use prefetch_related for GenericRelation and GenericForeignKey
    comments = comments.prefetch_related('content_object')
    
    authors = Profile.objects.prefetch_related('comments')
    
    knowledge_packets = KnowledgePacket.objects.select_related(
        'author__character')
    knowledge_packets = knowledge_packets.prefetch_related('comments')
    
    context = {
        'page_title': 'Komentarze',
        'comments': comments,
        'authors': authors,
        'knowledge_packets': knowledge_packets,
    }
    return render(request, 'comments/main.html', context)
