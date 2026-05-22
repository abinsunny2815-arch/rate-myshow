"""
Views for ratings app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.ratings.models import Rating, Review
from apps.titles.models import Title
from . import forms


class ReviewCreateView(LoginRequiredMixin, CreateView):
    """Create a review for a title."""
    model = Review
    form_class = forms.ReviewForm
    template_name = 'ratings/review_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        omdb_id = self.kwargs.get('omdb_id')
        context['title'] = get_object_or_404(Title, omdb_id=omdb_id)
        return context
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        omdb_id = self.kwargs.get('omdb_id')
        form.instance.title = get_object_or_404(Title, omdb_id=omdb_id)
        
        # Link to rating if exists
        rating = Rating.objects.filter(
            user=self.request.user,
            title=form.instance.title
        ).first()
        if rating:
            form.instance.rating = rating
        
        messages.success(self.request, 'Review created successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return self.object.title.get_absolute_url()


class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Edit a review."""
    model = Review
    form_class = forms.ReviewForm
    template_name = 'ratings/review_form.html'
    
    def test_func(self):
        return self.get_object().user == self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Review updated successfully!')
        return super().form_valid(form)


class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a review."""
    model = Review
    
    def test_func(self):
        return self.get_object().user == self.request.user
    
    def get_success_url(self):
        return self.object.title.get_absolute_url()
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Review deleted successfully!')
        return super().delete(request, *args, **kwargs)


@login_required
@require_POST
def mark_helpful(request, review_id):
    """Mark review as helpful."""
    review = get_object_or_404(Review, id=review_id)
    review.helpful_count += 1
    review.save(update_fields=['helpful_count'])
    
    return JsonResponse({'helpful_count': review.helpful_count})


@login_required
@require_POST
def mark_unhelpful(request, review_id):
    """Mark review as unhelpful."""
    review = get_object_or_404(Review, id=review_id)
    review.unhelpful_count += 1
    review.save(update_fields=['unhelpful_count'])
    
    return JsonResponse({'unhelpful_count': review.unhelpful_count})
