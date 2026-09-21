from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Event CRUD
    path('event/create/', views.event_create, name='event_create'),
    path('event/<int:event_id>/edit/', views.event_edit, name='event_edit'),
    path('event/<int:event_id>/delete/', views.event_delete, name='event_delete'),

    # Session CRUD
    path('event/<int:event_id>/schedule/', views.schedule, name='schedule'),
    path('event/<int:event_id>/session/<int:session_id>/edit/',views.session_edit, name='session_edit'),
    path('event/<int:event_id>/session/<int:session_id>/delete/',views.session_delete, name='session_delete'),
     

    # Registration
    path('event/<int:event_id>/register/', views.register, name='register'),
    path('event/<int:event_id>/register/success/',
         views.register_success, name='register_success'),

    # Tracking
    path('event/<int:event_id>/tracking/', views.tracking, name='tracking'),

    # Subscriber Management 
    path('subscribers/', views.manage_subscribers, name='manage_subscribers'),
    path('subscribers/add/', views.subscriber_add, name='subscriber_add'),
    path('subscribers/<int:pk>/edit/', views.subscriber_edit, name='subscriber_edit'),
    path('subscribers/<int:pk>/archive/', views.subscriber_archive, name='subscriber_archive'),

    # ── AI Features ──
    path('ai/describe/', views.ai_describe, name='ai_describe'),
    path('ai/sessions/', views.ai_sessions, name='ai_sessions'),
    path('ai/chat/<int:event_id>/', views.ai_chat_ui, name='ai_chat_ui'),
    path('ai/chat/init/', views.ai_chat_init, name='ai_chat_init'),
    path('ai/chat/message/', views.ai_chat_message, name='ai_chat_message'),
]