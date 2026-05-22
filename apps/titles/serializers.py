"""
URLs API configuration.
"""
from rest_framework import serializers
from apps.titles.models import Title
from apps.ratings.models import Rating, Review


class GenreSerializer(serializers.StringRelatedField):
    def to_representation(self, value):
        return value.name


class TitleSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    actors = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Title
        fields = [
            'omdb_id', 'title', 'type', 'year', 'released_date',
            'rated', 'runtime', 'plot', 'poster_url', 'imdb_rating',
            'avg_rating', 'rating_count', 'genres', 'actors',
            'director', 'writer', 'production', 'country', 'language'
        ]


class RatingSerializer(serializers.ModelSerializer):
    title = TitleSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Rating
        fields = ['id', 'username', 'title', 'score', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ReviewSerializer(serializers.ModelSerializer):
    title = TitleSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    user_avatar = serializers.ImageField(source='user.avatar', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'username', 'user_avatar', 'title', 'title_review',
            'content', 'contains_spoilers', 'helpful_count', 'unhelpful_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['helpful_count', 'unhelpful_count', 'created_at', 'updated_at']
