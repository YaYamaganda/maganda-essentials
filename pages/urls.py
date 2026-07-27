from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('newsletter-signup/', views.newsletter_signup, name='newsletter_signup'),
    path('contact/', views.contact, name='contact'),  # <-- Make sure this exists
]