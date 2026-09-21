import json
import urllib.request
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from .models import (
    Event, Track, Session,
    Registration, Attendee,
    SessionRegistration, Subscription
)
from .forms import SubscriberForm

def index(request):
    return render(request, 'index.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def dashboard(request):
    events = Event.objects.filter(organiser=request.user)
    total_registrations = Registration.objects.filter(
        event__organiser=request.user
    ).count()
    total_sessions = Session.objects.filter(
        track__event__organiser=request.user
    ).count()
    context = {
        'events': events,
        'total_registrations': total_registrations,
        'total_sessions': total_sessions,
    }
    return render(request, 'dashboard.html', context)

@login_required
def event_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        location = request.POST.get('location')
        event_type = request.POST.get('event_type')
        start_datetime = request.POST.get('start_datetime')
        end_datetime = request.POST.get('end_datetime')
        max_capacity = request.POST.get('max_capacity') or None
        visibility = request.POST.get('visibility', 'public')
        action = request.POST.get('action', 'draft')
        status = 'published' if action == 'publish' else 'draft'

        event = Event.objects.create(
            organiser=request.user,
            title=title,
            description=description,
            location=location,
            event_type=event_type,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            max_capacity=max_capacity,
            visibility=visibility,
            status=status,
        )
        return redirect('schedule', event_id=event.id)
    return render(request, 'eventcreate.html')

@login_required
def event_edit(request, event_id):
    event = get_object_or_404(Event, id=event_id, organiser=request.user)
    if request.method == 'POST':
        event.title = request.POST.get('title')
        event.description = request.POST.get('description')
        event.location = request.POST.get('location')
        event.event_type = request.POST.get('event_type')
        event.start_datetime = request.POST.get('start_datetime')
        event.end_datetime = request.POST.get('end_datetime')
        event.max_capacity = request.POST.get('max_capacity') or None
        event.visibility = request.POST.get('visibility', 'public')
        action = request.POST.get('action', 'draft')
        event.status = 'published' if action == 'publish' else 'draft'
        event.save()
        return redirect('dashboard')
    return render(request, 'eventcreate.html', {'event': event})

@login_required
def event_delete(request, event_id):
    event = get_object_or_404(Event, id=event_id, organiser=request.user)
    if request.method == 'POST':
        event.delete()
    return redirect('dashboard')

@login_required
def schedule(request, event_id):
    event = get_object_or_404(Event, id=event_id, organiser=request.user)
    tracks = Track.objects.filter(event=event)
    sessions = Session.objects.filter(track__event=event).order_by('start_time')

    if request.method == 'POST':
        session_title = request.POST.get('session_title')
        speaker = request.POST.get('speaker')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        track_name = request.POST.get('track_name', 'General')

        # 找或建立 track
        track, _ = Track.objects.get_or_create(
            event=event,
            name=track_name
        )
        Session.objects.create(
            track=track,
            title=session_title,
            speaker=speaker,
            start_time=start_time,
            end_time=end_time,
        )
        return redirect('schedule', event_id=event.id)

    context = {
        'event': event,
        'tracks': tracks,
        'sessions': sessions,
    }
    return render(request, 'schedule.html', context)

@login_required
def session_delete(request, event_id, session_id):
    event = get_object_or_404(Event, id=event_id, organiser=request.user)
    session = get_object_or_404(Session, id=session_id, track__event=event)
    if request.method == 'POST':
        session.delete()
    return redirect('schedule', event_id=event.id)

@login_required
def session_edit(request, event_id, session_id):
    event = get_object_or_404(Event, id=event_id, organiser=request.user)
    session = get_object_or_404(Session, id=session_id, track__event=event)

    if request.method == 'POST':
        session_title = request.POST.get('session_title', '').strip()
        speaker = request.POST.get('speaker', '').strip()
        start_time = request.POST.get('start_time', '')
        end_time = request.POST.get('end_time', '')
        track_name = request.POST.get('track_name', '').strip()

        # 找或建立 track
        track, _ = Track.objects.get_or_create(
            event=event,
            name=track_name
        )

        session.title = session_title
        session.speaker = speaker
        session.start_time = start_time
        session.end_time = end_time
        session.track = track
        session.save()

        return redirect('schedule', event_id=event.id)

    # GET — 預填現有資料
    context = {
        'event': event,
        'session': session,
    }
    return render(request, 'session_edit.html', context)

@login_required
def tracking(request, event_id):
    event = get_object_or_404(Event, id=event_id, organiser=request.user)
    registrations = Registration.objects.filter(
        event=event
    ).select_related('attendee')
    total = registrations.count()
    confirmed = registrations.filter(status='confirmed').count()
    pending = registrations.filter(status='pending').count()
    sessions = Session.objects.filter(track__event=event)

    # 計算剩餘名額
    if event.max_capacity:
        spots_remaining = event.max_capacity - total
        capacity_percent = round((total / event.max_capacity) * 100)
    else:
        spots_remaining = None
        capacity_percent = 0

    context = {
        'event': event,
        'registrations': registrations,
        'total': total,
        'confirmed': confirmed,
        'pending': pending,
        'sessions': sessions,
        'capacity': event.max_capacity or 0,
        'spots_remaining': spots_remaining,
        'capacity_percent': capacity_percent,
    }
    return render(request, 'tracking.html', context)


def register(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    sessions = Session.objects.filter(
        track__event=event
    ).order_by('start_time')
    tracks = Track.objects.filter(event=event)

    registered_count = Registration.objects.filter(event=event).count()
    if event.max_capacity:
        spots_remaining = event.max_capacity - registered_count
    else:
        spots_remaining = None

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        organisation = request.POST.get('organisation', '').strip()
        job_title = request.POST.get('job_title', '').strip()

        # 基本驗證
        if not full_name or not email:
            context = {
                'event': event,
                'sessions': sessions,
                'tracks': tracks,
                'spots_remaining': spots_remaining,
                'registered_count': registered_count,
                'error': 'Please fill in your name and email.',
            }
            return render(request, 'register.html', context)

        # 找或建立 attendee
        attendee, created = Attendee.objects.get_or_create(
            email=email,
            defaults={
                'full_name': full_name,
                'organisation': organisation,
                'job_title': job_title,
            }
        )

        # 如果 attendee 已存在，更新資料
        if not created:
            attendee.full_name = full_name
            attendee.organisation = organisation
            attendee.job_title = job_title
            attendee.save()

        # 建立 registration（避免重複）
        registration, reg_created = Registration.objects.get_or_create(
            event=event,
            attendee=attendee,
            defaults={'status': 'confirmed'}
        )

        # 處理 session 選擇
        if reg_created:
            for session in sessions:
                key = f'session_{session.id}'
                if request.POST.get(key):
                    SessionRegistration.objects.get_or_create(
                        registration=registration,
                        session=session,
                    )

        return redirect('register_success', event_id=event.id)

    context = {
        'event': event,
        'sessions': sessions,
        'tracks': tracks,
        'spots_remaining': spots_remaining,
        'registered_count': registered_count,
    }
    return render(request, 'register.html', context)

def register_success(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'register_success.html', {'event': event})



@login_required
def manage_subscribers(request):
    search_query = request.GET.get('search', '')
    subscribers = Subscription.objects.select_related('user').all().order_by('id')

    if search_query:
        subscribers = subscribers.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(plan__icontains=search_query)
        )

    # Pagination — 5 per page
    paginator = Paginator(subscribers, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'subscribers': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': page_obj.has_other_pages(),
        'search_query': search_query,
    }
    return render(request, 'manage_subscribers.html', context)


@login_required
def subscriber_add(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        plan = request.POST.get('plan', 'free')
        status = request.POST.get('status', 'active')

        # 檢查 username 是否已存在
        if User.objects.filter(username=username).exists():
            return render(request, 'subscriber_form.html', {
                'action': 'Add',
                'error': f'Username "{username}" already exists.',
                'form_data': request.POST,
            })

        if not username or not password:
            return render(request, 'subscriber_form.html', {
                'action': 'Add',
                'error': 'Username and password are required.',
                'form_data': request.POST,
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        Subscription.objects.create(
            user=user,
            plan=plan,
            status=status,
        )
        return redirect('manage_subscribers')

    return render(request, 'subscriber_form.html', {'action': 'Add'})


@login_required
def subscriber_edit(request, pk):
    subscription = get_object_or_404(Subscription, pk=pk)
    user = subscription.user

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        plan = request.POST.get('plan', subscription.plan)
        status = request.POST.get('status', subscription.status)

        user.username = username
        user.email = email
        if password:
            user.set_password(password)
        user.save()

        subscription.plan = plan
        subscription.status = status
        subscription.save()

        return redirect('manage_subscribers')

    return render(request, 'subscriber_form.html', {
        'action': 'Edit',
        'subscription': subscription,
        'form_data': {
            'username': user.username,
            'email': user.email,
            'plan': subscription.plan,
            'status': subscription.status,
        }
    })


@login_required
def subscriber_archive(request, pk):
    subscription = get_object_or_404(Subscription, pk=pk)
    if request.method == 'POST':
        subscription.status = 'cancelled'
        subscription.save()
        return redirect('manage_subscribers')
    return render(request, 'subscriber_confirm_archive.html', {
        'subscription': subscription
    })

def _call_ai(system_prompt, user_message, max_tokens=500):
    payload = json.dumps({
        "model": "gpt-5.4-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "max_completion_tokens": max_tokens,
        "temperature": 0.7
    }).encode('utf-8')

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode('utf-8'))
        return result['choices'][0]['message']['content'].strip()


@login_required
def ai_describe(request):
    """Generate event description using AI — returns partial HTML via HTMX"""
    if request.method != 'POST':
        return HttpResponse('')

    title = request.POST.get('title', '').strip()
    location = request.POST.get('location', '').strip()
    event_type = request.POST.get('event_type', '').strip()

    if not title:
        return render(request, 'partials/_ai_description.html', {
            'error': 'Please enter an event name first.'
        })

    try:
        prompt = f'Event name: "{title}"'
        if location:
            prompt += f', Location: {location}'
        if event_type:
            prompt += f', Type: {event_type}'
        prompt += '. Write a compelling 2-3 sentence event description.'

        description = _call_ai(
            system_prompt="You are an expert event coordinator. Generate a compelling, professional event description in 2-3 sentences. Be specific and engaging. Return only the description text, no extra formatting or quotes.",
            user_message=prompt
        )

        return render(request, 'partials/_ai_description.html', {
            'description': description
        })

    except Exception as e:
        return render(request, 'partials/_ai_description.html', {
            'error': str(e)
        })


@login_required
def ai_sessions(request):
    """Suggest session titles using AI — returns partial HTML via HTMX"""
    if request.method != 'POST':
        return HttpResponse('')

    event_title = request.POST.get('event_title', '').strip()

    if not event_title:
        return render(request, 'partials/_ai_sessions.html', {
            'error': 'No event title provided.'
        })

    try:
        result = _call_ai(
            system_prompt='You are an expert event coordinator. Suggest exactly 5 creative and relevant session titles. Return ONLY a JSON array of 5 strings, no other text. Example: ["Title 1", "Title 2", "Title 3", "Title 4", "Title 5"]',
            user_message=f'Suggest 5 session titles for an event called "{event_title}".'
        )

        # Parse JSON array
        suggestions = json.loads(result.strip())
        if not isinstance(suggestions, list):
            raise ValueError("Not a list")

        return render(request, 'partials/_ai_sessions.html', {
            'suggestions': suggestions[:5]
        })

    except Exception as e:
        return render(request, 'partials/_ai_sessions.html', {
            'error': f'Could not generate suggestions: {str(e)}'
        })


@login_required
def ai_chat_ui(request, event_id):
    """Show the AI Event Assistant chat interface"""
    event = get_object_or_404(Event, id=event_id, organiser=request.user)
    # Reset session chat history
    request.session['chat_history'] = []
    request.session['chat_event_id'] = event_id
    return render(request, 'ai_chat.html', {'event': event})


@login_required
def ai_chat_init(request):
    """Generate initial AI greeting — called on page load via HTMX"""
    event_id = request.session.get('chat_event_id')
    event = get_object_or_404(Event, id=event_id)

    system = f"""You are a helpful event planning assistant for "{event.title}".
    Event details: Type: {event.event_type}, Location: {event.location or 'TBD'}, Date: {event.start_datetime}.
    Help the organiser with event planning advice, session ideas, promotion tips, and attendee engagement strategies.
    Be friendly, concise and practical."""

    try:
        greeting = _call_ai(
            system_prompt=system,
            user_message="Introduce yourself briefly and ask how you can help with this event. Keep it to 2-3 sentences.",
            max_tokens=200
        )
    except Exception:
        greeting = f"Hi! I'm your AI assistant for {event.title}. How can I help you plan this event?"

    # Save to session
    request.session['chat_history'] = [
        {"role": "assistant", "content": greeting}
    ]
    request.session.modified = True

    return render(request, 'partials/_chat_message.html', {
        'message': greeting,
        'is_user': False,
    })


@login_required
def ai_chat_message(request):
    """Process user message and return AI response — via HTMX"""
    if request.method != 'POST':
        return HttpResponse('')

    user_message = request.POST.get('message', '').strip()
    if not user_message:
        return HttpResponse('')

    event_id = request.session.get('chat_event_id')
    event = get_object_or_404(Event, id=event_id)

    history = request.session.get('chat_history', [])

    # Build conversation for API
    system = f"""You are a helpful event planning assistant for "{event.title}".
    Event details: Type: {event.event_type}, Location: {event.location or 'TBD'}.
    Help with event planning, session ideas, promotion tips, and engagement strategies.
    Be friendly, concise and practical. Keep responses under 150 words."""

    # 統一使用我們定義好的 _call_ai 函式，它已經處理好 OpenAI 的所有細節了
    try:
        # 將歷史訊息轉化為單一字串作為 user_message (或是你可以修改 _call_ai 來接受 list)
        # 為了簡單起見，我們先用 _call_ai 處理當前訊息
        bot_reply = _call_ai(
            system_prompt=system,
            user_message=user_message,
            max_tokens=300
        )
    except Exception as e:
        bot_reply = f"Sorry, I encountered an error: {str(e)}"

    # 更新 session 紀錄
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": bot_reply})
    request.session['chat_history'] = history[-10:]
    request.session.modified = True

    return render(request, 'partials/_chat_exchange.html', {
        'user_message': user_message,
        'bot_message': bot_reply,
    })

