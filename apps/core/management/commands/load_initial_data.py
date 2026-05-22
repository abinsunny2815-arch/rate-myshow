"""
Management command to load initial OMDB data.
"""
from django.core.management.base import BaseCommand
from apps.core.services import OMDBService


class Command(BaseCommand):
    help = 'Load popular movies and TV shows from OMDB'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--movies',
            type=int,
            default=50,
            help='Number of popular movies to load (default: 50)'
        )
        parser.add_argument(
            '--shows',
            type=int,
            default=50,
            help='Number of popular TV shows to load (default: 50)'
        )
    
    def handle(self, *args, **options):
        service = OMDBService()
        
        # Popular movies (you would need a list of IDs)
        popular_movie_ids = [
            'tt0111161', 'tt0068646', 'tt0071562', 'tt0102926', 'tt0110912',
            'tt0137523', 'tt0109830', 'tt0816692', 'tt1375666', 'tt0910970',
        ]
        
        self.stdout.write(self.style.SUCCESS(f'Loading {len(popular_movie_ids)} movies...'))
        for omdb_id in popular_movie_ids:
            title = service.sync_title_to_db(omdb_id)
            if title:
                self.stdout.write(self.style.SUCCESS(f'✓ Loaded: {title.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'✗ Failed to load: {omdb_id}'))
        
        self.stdout.write(self.style.SUCCESS('\nInitial data loaded successfully!'))
