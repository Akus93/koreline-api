from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Użytkownik')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Data urodzenia')
    is_teacher = models.BooleanField(default=False)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    class Meta:
        verbose_name = 'Profil użytkownika'
        verbose_name_plural = 'Profile użytkowników'


class Subject(models.Model):
    name = models.CharField(verbose_name='Nazwa', max_length=128)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Przedmiot'
        verbose_name_plural = 'Przedmioty'


class Lesson(models.Model):
    teacher = models.ForeignKey(UserProfile, verbose_name='Nauczyciel')
    title = models.CharField(verbose_name='Tytuł', max_length=255)
    subject = models.ForeignKey(Subject, verbose_name='Przedmiot')
    slug = models.SlugField(unique=True)
    price = models.PositiveSmallIntegerField(verbose_name='Cena za 15min')

    @property
    def subject_name(self):
        return self.subject.name

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Lekcja'
        verbose_name_plural = 'Lekcje'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


@receiver(post_delete, sender=UserProfile)
def post_delete_user(sender, instance, *args, **kwargs):
    instance.user.delete()

