# MovieMate - Project Documentation

## Overview

MovieMate is a comprehensive web application designed to help users track and manage their personal movie and TV show collections. The application provides features for organizing content, tracking viewing progress, rating and reviewing, and discovering new content through personalized recommendations.

## Architecture

### Backend Architecture

The backend is built using Django REST Framework, providing a robust RESTful API for the frontend application.

#### Models

1. **Content** (Abstract Base Model)
   - Base model for movies and TV shows
   - Fields: title, director, description, release_date, genre (M2M), platform (FK), status, content_type, poster_url, tmdb_id, imdb_id, runtime
   - Status choices: watching, completed, wishlist, paused

2. **Movie** (Inherits from Content)
   - Specific model for movies
   - No additional fields (uses Content base)

3. **TVShow** (Inherits from Content)
   - Specific model for TV shows
   - Additional fields: total_seasons, total_episodes, episodes_per_season (JSON)

4. **Genre**
   - Categorization for content
   - Fields: name (unique)

5. **Platform**
   - Streaming platforms (Netflix, Prime, etc.)
   - Fields: name (unique), icon

6. **Rating**
   - User ratings for content
   - Fields: content (FK), rating (1-10), rated_at
   - One rating per content

7. **Review**
   - Detailed reviews and notes
   - Fields: content (FK), review_text, notes, created_at, updated_at

8. **WatchProgress**
   - Episode tracking for TV shows
   - Fields: content (FK), season, episode, completed, watched_at, watch_time_minutes
   - Unique constraint on (content, season, episode)

9. **WatchHistory**
   - Watch session tracking for statistics
   - Fields: content (FK), watch_date, watch_time_minutes, session_type

#### API Endpoints

The API follows RESTful conventions and provides comprehensive endpoints for all operations:

- **Content Management**: Full CRUD operations with filtering, sorting, and searching
- **TMDB Integration**: Search and import functionality
- **Recommendations**: Genre-based recommendation engine
- **Statistics**: Collection and watch time statistics
- **Progress Tracking**: Episode marking and completion estimates

### Frontend Architecture

The frontend is built with React using functional components and hooks, following modern React patterns.

#### Component Structure

1. **Layout Components**
   - `Navbar`: Navigation bar with routing links
   - `ContentCard`: Reusable card component for displaying content

2. **Page Components**
   - `Home`: Main collection view with filtering
   - `Movies`: Movies-only view
   - `TVShows`: TV shows-only view
   - `AddContent`: Content addition form with TMDB integration
   - `ContentDetail`: Detailed view with ratings, reviews, and progress tracking
   - `Statistics`: Analytics and charts
   - `Recommendations`: Personalized recommendations view

3. **Services**
   - `api.js`: Centralized API service functions for all endpoints

#### State Management

- React hooks (useState, useEffect) for local state
- API calls using Axios
- Toast notifications for user feedback

## Features Implementation

### Core Features

#### 1. Content Management

- **Manual Entry**: Form-based content addition with validation
- **TMDB Integration**: Search and import from The Movie Database
- **Filtering**: Multiple filter criteria (status, platform, genre, type)
- **Sorting**: Various sorting options (date, title, rating)
- **Search**: Full-text search across titles and descriptions

#### 2. Progress Tracking

- **Episode Tracking**: Mark individual episodes as watched
- **Progress Calculation**: Automatic calculation of watched episodes
- **Completion Estimates**: Time-based estimates for show completion
- **History Tracking**: Maintain watch history for statistics

#### 3. Ratings & Reviews

- **Star Rating**: Interactive 1-10 rating system
- **Review Writing**: Rich text review functionality
- **Notes System**: Personal notes separate from reviews
- **Review Generation**: Basic template-based review generation from notes

#### 4. Statistics & Analytics

- **Collection Overview**: Total items, movies, shows counts
- **Status Distribution**: Visual pie chart of status breakdown
- **Watch Time Tracking**: Weekly and monthly watch time
- **Daily Breakdown**: Day-by-day watch time visualization
- **Average Ratings**: Calculated average rating across collection

### Optional Features

#### 1. TMDB Integration

- **Search**: Query TMDB API for movies/shows
- **Import**: One-click import with metadata
- **Auto-population**: Automatic filling of forms with TMDB data

#### 2. Recommendations

- **Genre-based**: Recommendations based on highly-rated genres
- **Rating Analysis**: Considers ratings >= 7 for preferences
- **Exclusion**: Excludes already-rated content

#### 3. Completion Estimates

- **Time Calculation**: Based on remaining episodes and average watch time
- **Progress Percentage**: Visual progress indicators
- **Daily Estimates**: Days remaining based on watching habits

## Database Schema

### Relationships

```
Content (Abstract)
├── Movie (inherits)
├── TVShow (inherits)
├── Genre (M2M)
├── Platform (FK)
├── Rating (1:1)
├── Review (1:M)
├── WatchProgress (1:M) - TV Shows only
└── WatchHistory (1:M)
```

### Key Constraints

- Unique constraint on Content.tmdb_id
- Unique constraint on Rating(content)
- Unique constraint on WatchProgress(content, season, episode)

## API Design

### Response Format

All API responses follow a consistent format:

```json
{
  "id": 1,
  "field": "value",
  ...
}
```

For list endpoints with pagination:

```json
{
  "count": 100,
  "next": "http://api/content/?page=2",
  "previous": null,
  "results": [...]
}
```

### Error Handling

Errors follow standard HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 404: Not Found
- 500: Server Error

Error response format:

```json
{
  "error": "Error message"
}
```

## Security Considerations

1. **Environment Variables**: Sensitive data stored in .env files
2. **CORS Configuration**: Proper CORS settings for production
3. **Input Validation**: Server-side validation on all inputs
4. **SQL Injection Prevention**: Django ORM provides protection
5. **XSS Prevention**: React automatically escapes content

## Performance Optimization

1. **Database Indexing**: Key fields indexed for faster queries
2. **Query Optimization**: Use of select_related and prefetch_related
3. **Pagination**: Large result sets paginated
4. **Frontend Optimization**: Code splitting and lazy loading

## Testing

### Backend Testing

```bash
python manage.py test
```

Test coverage includes:
- Model creation and relationships
- API endpoint functionality
- Filtering and sorting
- TMDB integration

### Frontend Testing

```bash
npm test
```

## Deployment Considerations

### Backend

1. **Environment Configuration**: Set DEBUG=False, configure ALLOWED_HOSTS
2. **Database**: Switch to PostgreSQL for production
3. **Static Files**: Configure static file serving
4. **Media Files**: Configure media file storage
5. **API Keys**: Secure storage of TMDB API key

### Frontend

1. **Build Optimization**: Production build with minification
2. **API URL**: Update API base URL for production
3. **Environment Variables**: Configure production environment

## Future Enhancements

1. **User Authentication**: Multi-user support with profiles
2. **Social Features**: Share collections, follow users
3. **Advanced AI**: ML-based recommendations using scikit-learn
4. **Watch Party**: Suggest optimal watch times
5. **Mobile App**: React Native mobile application
6. **Export/Import**: Backup and restore collections

## API Rate Limiting

TMDB API has rate limits:
- 40 requests per 10 seconds
- Application handles this gracefully

## Troubleshooting

### Common Issues

1. **CORS Errors**: Check CORS_ALLOWED_ORIGINS in settings.py
2. **TMDB Errors**: Verify API key in .env file
3. **Database Errors**: Run migrations: `python manage.py migrate`
4. **Port Conflicts**: Change ports in runserver and vite config

## Support

For issues or questions:
- Email: doniya@sayonetech.com
- CC: ranju@sayonetech.com

---

Documentation Version: 1.0
Last Updated: 2024


