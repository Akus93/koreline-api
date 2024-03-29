from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Użytkownik')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Data urodzenia')
    is_teacher = models.BooleanField(verbose_name='Czy nauczyciel', default=False)
    photo = models.ImageField(verbose_name='Zdjęcie', upload_to='photos', max_length=255, blank=True, null=True)
    tokens = models.PositiveIntegerField(verbose_name='Żetony', default=0)
    headline = models.CharField(verbose_name='Nagłówek', max_length=70, blank=True, null=True)
    biography = models.TextField(verbose_name='Biografia', max_length=2048, blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    class Meta:
        verbose_name = 'Profil użytkownika'
        verbose_name_plural = 'Profile użytkowników'


class Notification(models.Model):
    INVITE = 'INVITE'
    TEACHER_UNSUBSCRIBE = 'TEACHER_UNSUBSCRIBE'
    STUDENT_UNSUBSCRIBE = 'STUDENT_UNSUBSCRIBE'
    SUBSCRIBE = 'SUBSCRIBE'
    COMMENT = 'COMMENT'
    NEW_BILL = 'NEW_BILL'
    PAID_BILL = 'PAID_BILL'
    DELETE_BILL = 'DELETE_BILL'
    NOTIFICATION_TYPES = (
        (INVITE, 'INVITE'),
        (TEACHER_UNSUBSCRIBE, 'TEACHER_UNSUBSCRIBE'),
        (STUDENT_UNSUBSCRIBE, 'STUDENT_UNSUBSCRIBE'),
        (SUBSCRIBE, 'SUBSCRIBE'),
        (COMMENT, 'COMMENT'),
        (NEW_BILL, 'NEW_BILL'),
        (PAID_BILL, 'PAID_BILL'),
        (DELETE_BILL, 'DELETE_BILL')
    )
    user = models.ForeignKey(UserProfile, verbose_name='Odbiorca')
    title = models.CharField(verbose_name='Tytuł', max_length=128)
    text = models.CharField(verbose_name='Tekst', max_length=255)
    type = models.CharField(verbose_name='Typ', choices=NOTIFICATION_TYPES, max_length=32)
    data = models.CharField(verbose_name='Dane', max_length=64, blank=True, null=True)
    is_read = models.BooleanField(verbose_name='Czy odczytane', default=False)
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='Data utworzenia')

    def __str__(self):
        return 'Powiadomienie dla {}'.format(self.user.user.username)

    class Meta:
        verbose_name = 'Powiadomienie'
        verbose_name_plural = 'Powiadomienia'
        ordering = ['-create_date']


class Message(models.Model):
    sender = models.ForeignKey(UserProfile, verbose_name='Nadawca', related_name='senders')
    reciver = models.ForeignKey(UserProfile, verbose_name='Odbiorca', related_name='recivers')
    title = models.CharField(verbose_name='Tytuł', max_length=64)
    text = models.TextField(verbose_name='Tekst', max_length=1024)
    is_read = models.BooleanField(verbose_name='Czy odczytane', default=False)
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='Data utworzenia')

    def __str__(self):
        return 'Wiadomość od {} do {}'.format(self.sender.user.username, self.reciver.user.username)

    class Meta:
        verbose_name = 'Wiadomość'
        verbose_name_plural = 'Wiadomości'
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
        verbose_name_plural = 'Poziomy'


class Lesson(models.Model):
    teacher = models.ForeignKey(UserProfile, verbose_name='Nauczyciel')
    title = models.CharField(verbose_name='Tytuł', max_length=64)
    subject = models.ForeignKey(Subject, verbose_name='Przedmiot')
    short_description = models.CharField(verbose_name='Krótki opis', max_length=255)
    long_description = models.TextField(verbose_name='Długi opis', max_length=2048)
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
    close_date = models.DateTimeField(verbose_name='Data zamknięcia', blank=True, null=True)

    def __str__(self):
        return 'Pokój konwersacji {}'.format(self.lesson)

    class Meta:
        verbose_name = 'pokój konwersacji'
        verbose_name_plural = 'Pokoje konwersacji'


class Comment(models.Model):
    author = models.ForeignKey(UserProfile, verbose_name='Autor', related_name='author')
    teacher = models.ForeignKey(UserProfile, verbose_name='Nauczyciel', related_name='teacher')
    text = models.CharField(verbose_name='Tekst', max_length=255)
    rate = models.SmallIntegerField(verbose_name='Ocena', choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])
    is_active = models.BooleanField(verbose_name='Czy aktywny', default=True)
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='Data utworzenia')

    def __str__(self):
        return 'Komentarz {} o {}'.format(self.author, self.teacher)

    class Meta:
        verbose_name = 'komentarz'
        verbose_name_plural = 'Komentarze'


class ReportedComment(models.Model):
    author = models.ForeignKey(UserProfile, verbose_name='Autor zgłoszenia')
    comment = models.ForeignKey(Comment, verbose_name='Komentarz')
    text = models.CharField(verbose_name='Tekst zgłoszenia', max_length=255)
    is_pending = models.BooleanField(verbose_name='Czy oczekujący', default=True)
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='Data utworzenia')

    def __str__(self):
        return 'Zgłoszenie komentarza {}'.format(self.comment)

    class Meta:
        verbose_name = 'zgłoszenie komentarza'
        verbose_name_plural = 'Zgłoszone komentarze'


class AccountOperation(models.Model):
    BUY = 'BUY'
    SELL = 'SELL'
    OPERATION_TYPES = (
        (BUY, 'BUY'),
        (SELL, 'SELL'),
    )
    user = models.ForeignKey(UserProfile, verbose_name='Uzytkownik')
    type = models.CharField(verbose_name='Typ operacji', choices=OPERATION_TYPES, max_length=32)
    amount = models.PositiveSmallIntegerField(verbose_name='Liczba żetonów')
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='Data utworzenia')

    def __str__(self):
        return 'Operacja {} na koncie {}'.format(self.type, self.user)

    class Meta:
        verbose_name = 'operacja na koncie'
        verbose_name_plural = 'Operacje na koncie'


class Bill(models.Model):
    user = models.ForeignKey(UserProfile, verbose_name='Odbiorca')
    lesson = models.ForeignKey(Lesson, verbose_name='Lekcja')
    amount = models.PositiveSmallIntegerField(verbose_name='Kwota')
    is_paid = models.BooleanField(verbose_name='Czy oplacono', default=False)
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='Data utworzenia')
    paid_date = models.DateTimeField(verbose_name='Data opłacenia', blank=True, null=True)

    def __str__(self):
        return 'Rachunek za lekcje {} dla {}'.format(self.lesson, self.user)

    class Meta:
        verbose_name = 'rachunek'
        verbose_name_plural = 'Rachunki'
