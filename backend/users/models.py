from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.db.models import F, Q

User = get_user_model()


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_following'
            ),
            models.CheckConstraint(check=(
                ~Q(user=F('author'))
            ), name='can_not_follow_himself')
        ]


class User(AbstractUser):
    first_name = models.CharField(
        max_length=150,
        blank=False,
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
    )
    email = models.EmailField(
        max_length=254,
        blank=False,
        unique=True,)
    password = models.CharField(
        max_length=150,
        blank=False,
    )
    following = models.ManyToManyField(
        'self',
        through=Follow,
        symmetrical=False,
        related_name='followers',
        verbose_name='ПОДПИСКИ',
    )
    groups = models.ManyToManyField(
        Group,
        related_name='users',
        blank=True,
        verbose_name='Группы',
        help_text='Группы пользователя',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='users',
        blank=True,
        verbose_name='Права доступа',
        help_text='Права доступа пользователя',
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.get_full_name()
