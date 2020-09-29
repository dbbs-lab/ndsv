from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator

# Create your models here.

class ApiUser(AbstractUser):
    pass

class EtchingPlate(models.Model):
    beam_id = models.CharField(unique=True, max_length=36, validators=[MinLengthValidator(36)])
    public_access = models.BooleanField(default=True)
    access_list = models.JSONField(default=list)
    transmitted_on = models.DateTimeField(auto_now=True)
    transmitted_by = models.CharField(max_length=100, default="Unknown")

    def has_access(self, user):
        return self.public_access or user.name in self.access_list

def get_etching_plate(beam_id):
    return EtchingPlate.objects.filter(beam_id=beam_id).first()
