"""
Views for recommendations app.
"""
from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.recommendations.models import Recommendation


class RecommendationsView(LoginRequiredMixin, ListView):
    """Personalized recommendations for the user."""
    model = Recommendation
    template_name = 'recommendations/list.html'
    context_object_name = 'recommendations'
    paginate_by = 20
    
    def get_queryset(self):
        return Recommendation.objects.filter(
            user=self.request.user,
            is_dismissed=False
        ).select_related('title').order_by('-confidence_score')
