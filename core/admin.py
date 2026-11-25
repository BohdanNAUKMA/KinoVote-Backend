"""Реєстрація моделей KinoVote в адмін-панелі Django."""

from django.contrib import admin

from .models import (
    Movie,
    Room,
    RoomMember,
    RoomMoviePool,
    Vote,
    WatchedMovie,
)


class RoomMemberInline(admin.TabularInline):
    """Учасники кімнати на сторінці редагування кімнати."""

    model = RoomMember
    extra = 0


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'invite_code', 'owner', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'invite_code', 'owner__username')
    readonly_fields = ('invite_code', 'created_at')
    inlines = (RoomMemberInline,)


@admin.register(RoomMember)
class RoomMemberAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'role', 'joined_at')
    list_filter = ('role',)
    search_fields = ('room__name', 'user__username')


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'tmdb_id', 'release_year', 'rating')
    list_filter = ('release_year',)
    search_fields = ('title', 'tmdb_id')


@admin.register(RoomMoviePool)
class RoomMoviePoolAdmin(admin.ModelAdmin):
    list_display = ('room', 'movie', 'added_by', 'added_at')
    search_fields = ('room__name', 'movie__title')


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('pool_entry', 'user', 'score', 'created_at')
    list_filter = ('score',)
    search_fields = ('user__username', 'pool_entry__movie__title')


@admin.register(WatchedMovie)
class WatchedMovieAdmin(admin.ModelAdmin):
    list_display = ('room', 'movie', 'watched_at')
    search_fields = ('room__name', 'movie__title')
