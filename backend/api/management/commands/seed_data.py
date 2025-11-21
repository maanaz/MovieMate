"""
Management command to seed initial data for genres and platforms
"""
from django.core.management.base import BaseCommand
from api.models import Genre, Platform


class Command(BaseCommand):
    help = 'Seeds initial data for genres and platforms'

    def handle(self, *args, **options):
        # Seed Genres
        genres = [
            'Action', 'Adventure', 'Animation', 'Comedy', 'Crime',
            'Documentary', 'Drama', 'Family', 'Fantasy', 'History',
            'Horror', 'Music', 'Mystery', 'Romance', 'Science Fiction',
            'Thriller', 'War', 'Western', 'TV Movie', 'Biography'
        ]
        
        for genre_name in genres:
            Genre.objects.get_or_create(name=genre_name)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(genres)} genres')
        )

        # Seed Platforms
        platforms = [
            {'name': 'Netflix', 'icon': '🎬'},
            {'name': 'Amazon Prime', 'icon': '📺'},
            {'name': 'Disney+', 'icon': '🏰'},
            {'name': 'Hulu', 'icon': '🎭'},
            {'name': 'HBO Max', 'icon': '🎪'},
            {'name': 'Apple TV+', 'icon': '🍎'},
            {'name': 'Paramount+', 'icon': '🏔️'},
            {'name': 'Peacock', 'icon': '🦚'},
            {'name': 'YouTube', 'icon': '▶️'},
            {'name': 'Other', 'icon': '📱'},
        ]
        
        for platform_data in platforms:
            Platform.objects.get_or_create(
                name=platform_data['name'],
                defaults={'icon': platform_data['icon']}
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(platforms)} platforms')
        )

        self.stdout.write(
            self.style.SUCCESS('Data seeding completed!')
        )


