"""Моделі бази даних KinoVote."""

import secrets

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

INVITE_CODE_LENGTH = 8


def generate_invite_code():
    """Генерує випадковий код запрошення до кімнати."""
    return secrets.token_urlsafe(INVITE_CODE_LENGTH)[:INVITE_CODE_LENGTH]


class Room(models.Model):
    """Приватна кімната для спільного вибору фільму."""

    class Status(models.TextChoices):
        WAITING = 'waiting', 'Waiting'
        VOTING = 'voting', 'Voting'
        FINISHED = 'finished', 'Finished'

    name = models.CharField(max_length=100)
    invite_code = models.CharField(
        max_length=INVITE_CODE_LENGTH,
        unique=True,
        default=generate_invite_code,
        editable=False,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_rooms',
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.WAITING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.invite_code})'


class RoomMember(models.Model):
    """Учасник кімнати та його роль."""

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MEMBER = 'member', 'Member'

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='members',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='room_memberships',
    )
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.MEMBER,
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['joined_at']
        constraints = [
            # Користувач може бути учасником кімнати лише один раз
            models.UniqueConstraint(
                fields=['room', 'user'],
                name='unique_room_member',
            ),
        ]

    def __str__(self):
        return f'{self.user} in {self.room} ({self.role})'


class Movie(models.Model):
    """Фільм, збережений локально з даних TMDB."""

    tmdb_id = models.PositiveIntegerField(unique=True)
    title = models.CharField(max_length=255)
    poster_url = models.URLField(max_length=500, blank=True)
    overview = models.TextField(blank=True)
    release_year = models.PositiveSmallIntegerField(null=True, blank=True)
    # Список назв жанрів, наприклад ["Drama", "Comedy"]
    genres = models.JSONField(default=list, blank=True)
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )
    trailer_url = models.URLField(max_length=500, blank=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        if self.release_year:
            return f'{self.title} ({self.release_year})'
        return self.title


class RoomMoviePool(models.Model):
    """Фільм, доданий до пулу кандидатів конкретної кімнати."""

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='movie_pool',
    )
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='room_pools',
    )
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='added_pool_movies',
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['added_at']
        verbose_name = 'room movie pool entry'
        verbose_name_plural = 'room movie pool'
        constraints = [
            # Один фільм не може бути доданий у пул кімнати двічі
            models.UniqueConstraint(
                fields=['room', 'movie'],
                name='unique_room_pool_movie',
            ),
        ]

    def __str__(self):
        return f'{self.movie} in {self.room}'


class Vote(models.Model):
    """Оцінка (1–5) користувача для фільму з пулу кімнати."""

    pool_entry = models.ForeignKey(
        RoomMoviePool,
        on_delete=models.CASCADE,
        related_name='votes',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='votes',
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            # Один голос від користувача за кожен фільм у пулі
            models.UniqueConstraint(
                fields=['pool_entry', 'user'],
                name='unique_user_vote_per_pool_entry',
            ),
            models.CheckConstraint(
                condition=models.Q(score__gte=1, score__lte=5),
                name='vote_score_between_1_and_5',
            ),
        ]

    def __str__(self):
        return f'{self.user}: {self.score} for {self.pool_entry}'


class WatchedMovie(models.Model):
    """Фільм, який уже переглянули в конкретній кімнаті."""

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='watched_movies',
    )
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='watched_in_rooms',
    )
    watched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-watched_at']
        constraints = [
            models.UniqueConstraint(
                fields=['room', 'movie'],
                name='unique_room_watched_movie',
            ),
        ]

    def __str__(self):
        return f'{self.movie} watched in {self.room}'
