from django.http import Http404
from django.shortcuts import render
from django.db.models import Max, Min, Sum
from .models import Board, Topic, Post


def forum_view(request):
    boards = Board.objects.all()
    topics = Topic.objects.all()
    posts = Post.objects.all()

    topics_with_last_post_date = {}
    for topic in topics:
        topics_with_last_post_date[topic] = topic.posts.all().aggregate(Max('date_posted'))['date_posted__max']

    topics_with_last_active_user = {}
    for topic in topics:
        last_post = topic.posts.filter(date_posted=topics_with_last_post_date[topic])
        topics_with_last_active_user[topic] = last_post[0].author if last_post else ''

    topics_with_participants = {}
    for topic in topics:
        participants = ''
        for post in posts:
            if post.topic == topic:
                participants += str(post.author.username) + '\n'
        topics_with_participants[topic] = participants

    context = {
        'page_title': 'Wieczorne narady',
        'boards': boards,
        'topics_with_last_post_date': topics_with_last_post_date,
        'topics_with_last_active_user': topics_with_last_active_user,
        'topics_with_participants': topics_with_participants
    }
    return render(request, 'forum/forum.html', context)


# def board_topics_view(request, slug):
#     try:
#         board = Board.objects.get(slug=slug)
#     except Board.DoesNotExist:
#         raise Http404('Temat nie istnieje')
#
#     context = {
#         'page_title': board.title,
#         'board': board,
#         'topics': board.topics.all(),
#     }
#     return render(request, 'forum/board.html', context)
#
#
# def topic_posts_view(request, id):
#     try:
#         topic = Topic.objects.get(id=id)
#     except Topic.DoesNotExist:
#         raise Http404('Taka narada nie istnieje')
#
#     context = {
#         'page_title': topic.topic_name,
#         'topic': topic,
#         'posts': topic.posts.all()
#
#     }
#     return render(request, 'forum/topic.html', context)
