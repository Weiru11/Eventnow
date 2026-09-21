from django.db import models
from django.contrib.auth.models import User

# 對應你 ERD 的 subscriptions 表
# User 表直接用 Django 內建的，不需要自己建
class Subscription(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    user = models.OneToOneField(
        User, on_delete=models.CASCADE
    )
    plan = models.CharField(max_length=50, choices=PLAN_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan}"


# 對應你 ERD 的 attendees 表
class Attendee(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    organisation = models.CharField(
        max_length=200, blank=True, null=True
    )
    job_title = models.CharField(
        max_length=200, blank=True, null=True
    )

    def __str__(self):
        return self.full_name


# 對應你 ERD 的 events 表
class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('conference', 'Conference'),
        ('meetup', 'Meetup'),
        ('workshop', 'Workshop'),
        ('webinar', 'Webinar'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
    ]
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]
    # organiser_id 對應到 Django 內建 User
    organiser = models.ForeignKey(
        User, on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(
        max_length=200, blank=True, null=True
    )
    event_type = models.CharField(
        max_length=50, choices=EVENT_TYPE_CHOICES
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    max_capacity = models.IntegerField(null=True, blank=True)
    visibility = models.CharField(
        max_length=50, choices=VISIBILITY_CHOICES, default='public'
    )
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default='draft'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# 對應你 ERD 的 tracks 表
class Track(models.Model):
    # event_id FK 對應 events 表
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200)
    colour = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.event.title})"


# 對應你 ERD 的 sessions 表
class Session(models.Model):
    # track_id FK 對應 tracks 表
    track = models.ForeignKey(
        Track, on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    speaker = models.CharField(max_length=200, blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    max_capacity = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title


# 對應你 ERD 的 registrations 表
class Registration(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
    ]
    # event_id FK 對應 events 表
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE
    )
    # attendee_id FK 對應 attendees 表
    attendee = models.ForeignKey(
        Attendee, on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default='pending'
    )
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.attendee.full_name} - {self.event.title}"


# 對應你 ERD 的 session_registrations 表（多對多中間表）
class SessionRegistration(models.Model):
    # registration_id FK 對應 registrations 表
    registration = models.ForeignKey(
        Registration, on_delete=models.CASCADE
    )
    # session_id FK 對應 sessions 表
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.registration} → {self.session.title}"