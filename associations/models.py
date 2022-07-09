from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import (
    CASCADE, Model, Index, TextField, ForeignKey as FK, PositiveIntegerField,
    ManyToManyField as M2M, CharField,
)

from users.models import Profile


# class Comment(Model):
#     author = FK(to=Profile, related_name='comments', on_delete=CASCADE)
#     text = TextField()
#     object_id = PositiveIntegerField()
#     content_type = FK(ContentType, on_delete=CASCADE)
#     content_object = GenericForeignKey()
#     linked_comments = M2M(to='self', blank=True)
#
#     class Meta:
#         indexes = [
#             Index(fields=["author"]),
#             Index(fields=["content_type", "object_id"]),
#         ]
#
#     def __str__(self):
#         return self.text


# -----------------------------------------------------------------------------

#
# class Association(Model):
#     author_ct = FK(ContentType, on_delete=CASCADE)
#     author_id = PositiveIntegerField()
#     author = GenericForeignKey('author_ct', 'author_id')
#     # ------------------------------------
#     title = CharField(max_length=1024)
#     comment = TextField(blank=True, null=True)
#
#     def __str__(self):
#         return self.title
#
#
# class AssociationItem(Model):
#     message = FK(Association, on_delete=CASCADE)
#     item_ct = FK(ContentType, on_delete=CASCADE)
#     item_id = PositiveIntegerField()
#     item = GenericForeignKey('item_ct', 'item_id')
#
#     def __str__(self):
#         return str(self.item)      # TODO will it work?
