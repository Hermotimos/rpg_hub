from django.shortcuts import render, get_object_or_404
from django.db.models import Max, Min, Sum
from .models import Board, Topic, Post
from .forms import CreatePostForm


def forum_view(request):
    boards = Board.objects.all()
    topics = Topic.objects.all()
    posts = Post.objects.all()

    # with dict comprehension
    topics_with_last_post_date = {topic: topic.posts.all().aggregate(Max('date_posted'))['date_posted__max']
                                  for topic in topics}
    # with for loop
    topics_with_last_active_user = {}
    for topic in topics:
        last_post = topic.posts.filter(date_posted=topics_with_last_post_date[topic])
        topics_with_last_active_user[topic] = last_post[0].author if last_post else ''

    topics_with_participants = {}
    for topic in topics:
        participants = ''
        for post in posts:
            if post.topic == topic and str(post.author.username) not in participants:
                participants += str(post.author.username) + ' '
        topics_with_participants[topic] = participants

    context = {
        'page_title': 'Wieczorne narady',
        'boards': boards,
        'topics_with_last_post_date': topics_with_last_post_date,
        'topics_with_last_active_user': topics_with_last_active_user,
        'topics_with_participants': topics_with_participants
    }
    return render(request, 'forum/forum.html', context)


def posts_in_topic_view(request, topic_slug):
    topic = get_object_or_404(Topic, slug=topic_slug)

    context = {
        'page_title': topic.topic_name,
        'topic': topic,
        'topic_posts': topic.posts.all()
    }
    return render(request, 'forum/topic.html', context)


def create_post_view(request):
    post = CreatePostForm()
    # post = CreatePostForm(request.POST or None)       # needs way to set author=authenticated user
    if post.is_valid():
        post.save()
        post = CreatePostForm

    context = {
        'post': post
    }
    return render(request, 'forum/create_post.html', context)
