from django.urls import path
from .views import home_view, signup_view, public_view, protected_view

urlpatterns = [
    path('', home_view),
    path('signup/', signup_view),
    path('public/', public_view),
    path('protected/', protected_view),
]
