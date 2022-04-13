from django.db import models


class AutoDateModel(models.Model):
    """Abstract model add date creation"""
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        abstract = True
