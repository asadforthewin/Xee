from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class LikedItems(models.Model):
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    #the type of an object
    content_type = models.ForeignKey(ContentType, on_delete = models.CASCADE)
    #the id
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()