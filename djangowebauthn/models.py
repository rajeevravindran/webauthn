from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class WebAuthnProfile(models.Model):
    """
    Django model to hold Webauthn related information of each user.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=200)
    credential_id = models.CharField(max_length=200)
    user_public_key = models.TextField()
    signature_counter = models.IntegerField(default=0)
    webauthn_ukey = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

    def update_signature_counter(self, count):
        self.signature_counter = count
        self.save()

    def hackyDict(self):
        temp = dict(self.__dict__)
        tempuser = dict(self.user.__dict__)
        del temp['_state']
        del tempuser['_state']
        del temp['user_id']
        temp['user'] = tempuser
        return temp