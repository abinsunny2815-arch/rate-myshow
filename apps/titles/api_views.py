"""
REST API views for titles.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from apps.titles.models import Title
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters


class TitleSearchAPI(APIView):
    """API endpoint for title search."""
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        title_type = request.query_params.get('type', None)
        
        if len(query) < 2:
            return Response({'error': 'Query too short'}, status=status.HTTP_400_BAD_REQUEST)
        
        titles = Title.objects.filter(title__icontains=query)
        if title_type:
            titles = titles.filter(type=title_type)
        
        titles = titles.values(
            'omdb_id', 'title', 'year', 'poster_url', 'type', 'avg_rating', 'rating_count'
        )[:20]
        
        return Response({'results': list(titles)})


class TitleDetailAPI(APIView):
    """API endpoint for title detail."""
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request, omdb_id):
        title = Title.objects.filter(omdb_id=omdb_id).first()
        if not title:
            return Response({'error': 'Title not found'}, status=status.HTTP_404_NOT_FOUND)
        
        data = {
            'omdb_id': title.omdb_id,
            'title': title.title,
            'type': title.type,
            'year': title.year,
            'released_date': title.released_date,
            'rated': title.rated,
            'runtime': title.runtime,
            'plot': title.plot,
            'poster_url': title.poster_url,
            'imdb_rating': title.imdb_rating,
            'avg_rating': title.avg_rating,
            'rating_count': title.rating_count,
            'genres': list(title.genres.values_list('name', flat=True)),
            'actors': list(title.actors.values_list('name', flat=True)),
            'director': title.director,
        }
        
        return Response(data)
