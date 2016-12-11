from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Użytkownik')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Data urodzenia')
    is_teacher = models.BooleanField(default=False)
    photo = models.ImageField(upload_to='photos', max_length=255, blank=True)
    tokens = models.PositiveIntegerField(verbose_name="Żetony", default=0)

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


class Stage(models.Model):
    name = models.CharField(verbose_name='Nazwa', max_length=128)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Poziom'
        verbose_name_plural = 'Poziom'


class Lesson(models.Model):
    teacher = models.ForeignKey(UserProfile, verbose_name='Nauczyciel')
    title = models.CharField(verbose_name='Tytuł', max_length=255)
    subject = models.ForeignKey(Subject, verbose_name='Przedmiot')
    slug = models.SlugField(unique=True)
    price = models.PositiveSmallIntegerField(verbose_name='Cena za 15min')
    stage = models.ForeignKey(Stage, verbose_name='Poziom')
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='Data utworzenia')

    @property
    def subject_name(self):
        return self.subject.name

    @property
    def stage_name(self):
        return self.stage.name

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Lekcja'
        verbose_name_plural = 'Lekcje'
        ordering = ['-create_date']


class LessonMembership(models.Model):
    lesson = models.ForeignKey(Lesson, verbose_name='Lekcja')
    student = models.ForeignKey(UserProfile, verbose_name='Uczeń')
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='Data utworzenia')

    def __str__(self):
        return '{} zapisany do {}'.format(self.student, self.lesson)

    class Meta:
        verbose_name = 'zapis na lekcje'
        verbose_name_plural = 'Zapisy na lekcje'
        ordering = ['-create_date']


class Room(models.Model):
    lesson = models.ForeignKey(Lesson, verbose_name='Lekcja')
    student = models.ForeignKey(UserProfile, verbose_name='Uczeń')
    key = models.CharField(verbose_name='Klucz', max_length=100, unique=True)
    is_open = models.BooleanField(default=True, verbose_name='Czy otwarty')
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='Data utworzenia')
    close_date = models.DateTimeField(auto_now_add=True, verbose_name='Data zamknięcia')

    def __str__(self):
        return 'Pokój konwersacji {}'.format(self.lesson)

    class Meta:
        verbose_name = 'pokój konwersacji'
        verbose_name_plural = 'Pokoje konwersacji'


# class RoomMember(models.Model):
#     room = models.ForeignKey(Room, verbose_name='Pokój')
#     member = models.ForeignKey(UserProfile, verbose_name='Uczeń')
#     join_date = models.DateTimeField(auto_now_add=True, verbose_name='Data dołączenia')
#     leave_date = models.DateTimeField(verbose_name='Data opuszczenia')
#
#     def __str__(self):
#         return 'Dołączenie do konwersacji {}'.format(self.room.lesson)
#
#     class Meta:
#         verbose_name = 'zapis do konwersacji'
#         verbose_name_plural = 'Zapisy do konwersacji'


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

