from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Event, Session, Track,
    Registration, Attendee,
    SessionRegistration, Subscription
)

# ── SUBSCRIPTION（SaaS 重點，要有 Archive 功能）──

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'plan', 'status',
        'start_date', 'end_date', 'is_archived'
    )
    list_filter = ('plan', 'status')
    search_fields = ('user__username', 'plan')
    actions = ['archive_subscriptions', 'activate_subscriptions']

    def is_archived(self, obj):
        return obj.status == 'cancelled'
    is_archived.boolean = True
    is_archived.short_description = 'Archived'

    @admin.action(description='Archive selected subscriptions')
    def archive_subscriptions(self, request, queryset):
        queryset.update(status='cancelled')

    @admin.action(description='Activate selected subscriptions')
    def activate_subscriptions(self, request, queryset):
        queryset.update(status='active')


# ── EVENT ──

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'organiser', 'event_type',
        'status', 'start_datetime', 'location',
        'registration_count'
    )
    list_filter = ('status', 'event_type', 'visibility')
    search_fields = ('title', 'organiser__username', 'location')
    actions = ['publish_events', 'archive_events']

    def registration_count(self, obj):
        return Registration.objects.filter(event=obj).count()
    registration_count.short_description = 'Registrations'

    @admin.action(description='Publish selected events')
    def publish_events(self, request, queryset):
        queryset.update(status='published')

    @admin.action(description='Archive selected events')
    def archive_events(self, request, queryset):
        queryset.update(status='cancelled')


# ── TRACK ──

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'colour')
    search_fields = ('name', 'event__title')
    list_filter = ('event',)


# ── SESSION ──

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'track', 'speaker',
        'start_time', 'end_time', 'max_capacity'
    )
    search_fields = ('title', 'speaker', 'track__name')
    list_filter = ('track__event', 'track')


# ── ATTENDEE ──

@admin.register(Attendee)
class AttendeeAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 'email',
        'organisation', 'job_title'
    )
    search_fields = ('full_name', 'email', 'organisation')


# ── REGISTRATION ──

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = (
        'attendee', 'event', 'status', 'registered_at'
    )
    list_filter = ('status', 'event')
    search_fields = (
        'attendee__full_name',
        'attendee__email',
        'event__title'
    )
    actions = ['confirm_registrations', 'cancel_registrations']

    @admin.action(description='Confirm selected registrations')
    def confirm_registrations(self, request, queryset):
        queryset.update(status='confirmed')

    @admin.action(description='Cancel selected registrations')
    def cancel_registrations(self, request, queryset):
        queryset.update(status='cancelled')


# ── SESSION REGISTRATION ──

@admin.register(SessionRegistration)
class SessionRegistrationAdmin(admin.ModelAdmin):
    list_display = ('registration', 'session')
    search_fields = (
        'registration__attendee__full_name',
        'session__title'
    )
    list_filter = ('session__track__event',)