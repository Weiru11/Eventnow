## Deployment URL
https://infs3202-1b6241d1.uqcloud.net/eventnow/

# EventNow

EventNow is a web-based event management platform built with Django.
It allows users to create and manage events, organize sessions,
handle registrations, track attendees, and manage subscribers.

The project also integrates LLM-powered features for assisting
with event planning and content generation.

## Features

- User authentication and registration
- Event creation and management
- Session scheduling
- Event registration
- Registration and attendee tracking
- Subscriber management
- AI-generated event descriptions
- AI session title suggestions
- AI event planning chatbot
- Django Admin interface

## Local Setup

1. Clone the repository
2. Create a virtual environment
3. Install dependencies
4. Run database migrations
5. Start the Django development server




## Page Navigation Guide
| Feature | URL |
|---------|-----|
| Landing Page | /eventnow/ |
| Login | /eventnow/login/ |
| Sign Up | /eventnow/signup/ |
| Dashboard | /eventnow/dashboard/ |
| Create Event | /eventnow/event/create/ |
| Session Schedule | /eventnow/event/{id}/schedule/ |
| Event Registration | /eventnow/event/{id}/register/ |
| Registration Tracking | /eventnow/event/{id}/tracking/ |
| AI Assistant Chatbot | /eventnow/ai/chat/{id}/ |
| Subscriber Management | /eventnow/subscribers/ |
| Django Admin | /eventnow/admin/ |

## AI Usage Statement

I used Claude (Anthropic) to assist with the following:

- Generated the models, views and url routing for the Event, 
  Session, Registration and Subscription features
- Generated the HTML templates and CSS design system for all pages
- Helped debug the CSRF error in the register form
- Helped debug the 500 error in the subscribers page
- Gave feedback on the database schema design
- Generated the HTMX integration code for AI features

I used OpenAI GPT-5.4-mini (via the course-provided API key) 
for the in-app AI features:
- AI event description generator (Create Event page)
- AI session title suggester (Session Schedule page)  
- AI event planning chatbot (AI Assistant page)

## Tech Stack
- Backend: Django 6.0 (Python 3.14)
- Database: MySQL
- Frontend: Custom CSS + Bootstrap 5
- AI: OpenAI GPT-5.4-mini
- Dynamic UI: HTMX
- Deployment: UQCloud (Nginx + Gunicorn)

## Background

This project was originally developed for the INFS3202 Web
Information Systems course at The University of Queensland and
deployed on UQCloud.

It has since been configured to run locally using SQLite.
