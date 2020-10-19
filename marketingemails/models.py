from django.db import models


class User(models.Model):
    
    name = models.CharField(max_length=200)
    email_address = models.CharField(max_length=200)    
    join_date = models.DateTimeField('date published')

    def __str__(self):
        return self.name

