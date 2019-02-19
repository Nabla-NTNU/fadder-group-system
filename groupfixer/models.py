from django.db import models

# Create your models here.


class Gruppe(models.Model):

    name = models.CharField(
        verbose_name='Navn på faddergruppe',
        blank=False,
        max_length=80,
        unique=True,
    )

    class Meta:
        verbose_name = 'Faddergruppe'
        verbose_name_plural = 'Faddergrupper'

    def __str__(self):
        return self.name


class Barn(models.Model):

    name = models.CharField(
        verbose_name='Navn på fadderbarn',
        blank=False,
        max_length=80,
        unique=True,
    )

    GENDERS = (
        ('female', 'Kvinne'),
        ('male', 'Mann'),
        ('other', 'Annet/Ønsker ikke å oppgi'),
    )

    gender = models.CharField(
        verbose_name='Kjønn',
        blank=False,
        max_length=10,
        choices=GENDERS,
    )

    pri_1 = models.ForeignKey(
        Gruppe,
        related_name='pri_1s',
        verbose_name='Førsteprioritet',
        on_delete=models.CASCADE,
        null=True,
    )

    pri_2 = models.ForeignKey(
        Gruppe,
        related_name='pri_2s',
        verbose_name='Andrerioritet',
        on_delete=models.CASCADE,
        null=True,
    )

    pri_3 = models.ForeignKey(
        Gruppe,
        related_name='pri_3s',
        verbose_name='Tredjeprioritet',
        on_delete=models.CASCADE,
        null=True,
    )

    class Meta:
        verbose_name = 'Fadderbarn'
        verbose_name_plural = 'Fadderbarn'

    def __str__(self):
        return self.name
