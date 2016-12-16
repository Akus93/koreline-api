from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import pusher


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


class Notification(models.Model):
    user = models.ForeignKey(UserProfile, verbose_name='Odbiorca')
    title = models.CharField(verbose_name='Tytuł', max_length=128)
    text = models.CharField(verbose_name='Tekst', max_length=255)
    is_read = models.BooleanField(verbose_name='Czy odczytane', default=False)
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='Data utworzenia')

    def __str__(self):
        return 'Powiadomienie dla {}'.format(self.user.user.username)

    class Meta:
        verbose_name = 'Powiadomienie'
        verbose_name_plural = 'Powiadomienia'
        ordering = ['-create_date']


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


@receiver(post_save, sender=Room)
def notify_user_about_room(sender, instance, created, **kwargs):
    if created:
        # send message about invitation using pusher
        pusher_client = pusher.Pusher(
            app_id='280178',
            key='15b5a30c14857f14b7a3',
            secret='2c00695673458f67097f',
            cluster='eu',
            ssl=True
        )
        teacher_name = instance.lesson.teacher.user.get_full_name() or instance.teacher.user.username
        pusher_client.trigger(instance.student.user.username+'-room-invite-channel', 'room-invite-event',
                              {
                                  'message': '{} zaprosił Cie do konwersacji.'.format(teacher_name),
                                  'room': instance.key
                              })

        # create notification about invitation
        Notification.objects.create(user=instance.student, title='Zaproszenie do konwersacji',
                                    text='Nauczyciel {} zaprosił Cię do konwersacji dotyczącej lekcji {}.'
                                    .format(instance.lesson.teacher, instance.lesson))


@receiver(post_save, sender=LessonMembership)
def notify_teacher_about_new_student(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(user=instance.lesson.teacher, title='Nowy uczeń',
                                    text='Uczeń {} zapisał się do Twojej lekcji {}.'.format(instance.student,
                                                                                            instance.lesson))


@receiver(post_delete, sender=LessonMembership)
def notify_teacher_about_unsubscribe_from_lesson(sender, instance, *args, **kwargs):
    Notification.objects.create(user=instance.lesson.teacher, title='Wypis ucznia',
                                text='Uczeń {} wypisał się z Twojej lekcji {}.'.format(instance.student,
                                                                                       instance.lesson))


@receiver(post_delete, sender=LessonMembership)
def notify_student_about_unsubscribe_from_lesson(sender, instance, *args, **kwargs):
    Notification.objects.create(user=instance.student, title='Usunięcie z lekcji',
                                text='Nauczyciel {} wypisał Cię z lekcji {}.'.format(instance.lesson.teacher,
                                                                                     instance.lesson))





