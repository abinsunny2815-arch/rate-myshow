"""
URLs for recommendations app.
"""
from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('', views.RecommendationsView.as_view(), name='list'),
]
