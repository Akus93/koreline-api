from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from koreline.models import UserProfile, Comment, Notification, LessonMembership, Room, Bill


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
        Notification.objects.create(user=instance.student, title='Zaproszenie do konwersacji', type=Notification.INVITE,
                                    data=instance.key,
                                    text='Nauczyciel {} zaprosił Cię do konwersacji dotyczącej lekcji {}.'
                                    .format(instance.lesson.teacher, instance.lesson))


@receiver(post_save, sender=LessonMembership)
def notify_teacher_about_new_student(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(user=instance.lesson.teacher, title='Nowy uczeń', type=Notification.SUBSCRIBE,
                                    data=instance.student.user.username,
                                    text='Uczeń {} zapisał się do Twojej lekcji {}.'.format(instance.student,
                                                                                            instance.lesson))


@receiver(post_delete, sender=LessonMembership)
def notify_teacher_about_unsubscribe_from_lesson(sender, instance, *args, **kwargs):
    Notification.objects.create(user=instance.lesson.teacher, title='Wypis ucznia',
                                type=Notification.TEACHER_UNSUBSCRIBE,
                                text='Uczeń {} został wypisany z Twojej lekcji {}.'.format(instance.student,
                                                                                           instance.lesson))


@receiver(post_delete, sender=LessonMembership)
def notify_student_about_unsubscribe_from_lesson(sender, instance, *args, **kwargs):
    Notification.objects.create(user=instance.student, title='Usunięcie z lekcji',
                                type=Notification.STUDENT_UNSUBSCRIBE,
                                text='Wypisano Cię z lekcji {}.'.format(instance.lesson))


@receiver(post_save, sender=Comment)
def notify_teacher_about_new_comment(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(user=instance.teacher, title='Nowy komentarz', type=Notification.COMMENT,
                                    text='Użytkownik {} wystawił Ci opinie.'.format(instance.author))


@receiver(post_save, sender=Bill)
def notify_student_about_new_bill(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(user=instance.user, title='Nowy rachunek', type=Notification.NEW_BILL,
                                    text='Wystawiono Ci rachunek za lekcję {}.'.format(instance.lesson))


@receiver(post_delete, sender=Bill)
def notify_student_about_delete_bill(sender, instance, *args, **kwargs):
    Notification.objects.create(user=instance.user, title='Usunięcie rachunku',
                                type=Notification.DELETE_BILL,
                                text='Rachunek do lekcji {} został usunięty.'.format(instance.lesson))