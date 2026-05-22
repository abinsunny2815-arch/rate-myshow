"""
URLs for ratings app.
"""
from django.urls import path
from . import views

app_name = 'ratings'

urlpatterns = [
    path('review/<str:omdb_id>/create/', views.ReviewCreateView.as_view(), name='review_create'),
    path('review/<int:pk>/edit/', views.ReviewUpdateView.as_view(), name='review_update'),
    path('review/<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='review_delete'),
    path('review/<int:review_id>/helpful/', views.mark_helpful, name='mark_helpful'),
    path('review/<int:review_id>/unhelpful/', views.mark_unhelpful, name='mark_unhelpful'),
]
