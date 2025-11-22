# MovieMate 🎬

Track and manage your personal movie and TV show collection with MovieMate - a full-stack web application built with Django and React.

![MovieMate](https://img.shields.io/badge/Status-Active-success)
![Django](https://img.shields.io/badge/Django-5.0.1-green)
![React](https://img.shields.io/badge/React-18.2.0-blue)

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### Core Features

- **Content Management**
  - Add movies and TV shows with detailed information (title, director, genre, platform, status)
  - Track viewing status: Watching, Completed, Wishlist, Paused
  - Support for multiple streaming platforms (Netflix, Prime, Hulu, etc.)
  - Organize by genres and categories

- **Progress Tracking**
  - Track episode-by-episode progress for TV shows
  - Mark episodes as watched with timestamps
  - Visual progress indicators
  - Completion estimates based on watching habits

- **Ratings & Reviews**
  - Rate content on a 1-10 scale
  - Write detailed reviews and personal notes
  - Generate reviews from notes using AI (optional)
  - Track all your ratings in one place

- **Filtering & Sorting**
  - Filter by genre, platform, status, or content type
  - Search by title, director, or description
  - Sort by date added, release date, title, or rating
  - Quick access to movies or TV shows separately

### Optional Features

- **TMDB Integration**
  - Search and import movies/shows from The Movie Database (TMDB)
  - Auto-fetch posters, descriptions, and metadata
  - Seamless integration with manual entry

- **AI Recommendations**
  - Personalized recommendations based on your ratings
  - Genre-based suggestions
  - Content discovery based on watch history

- **Statistics & Analytics**
  - Collection overview (total items, movies, shows)
  - Watch time tracking (weekly/monthly)
  - Status distribution charts
  - Daily watch time graphs
  - Average rating calculations

- **Completion Estimates**
  - Estimate time to complete TV shows
  - Based on your average daily watch time
  - Progress percentage tracking

## 🛠 Tech Stack

### Backend
- **Django 5.0.1** - Python web framework
- **Django REST Framework** - RESTful API
- **SQLite** - Database (can be switched to PostgreSQL)
- **django-cors-headers** - CORS handling
- **django-filter** - Advanced filtering
- **requests** - HTTP client for TMDB API
- **scikit-learn** - For recommendation algorithms

### Frontend
- **React 18.2.0** - UI library
- **React Router** - Navigation
- **Axios** - HTTP client
- **Recharts** - Data visualization
- **React Icons** - Icon library
- **React Hot Toast** - Notifications
- **Vite** - Build tool

## 📦 Installation

### Prerequisites

- Python 3.8+ 
- Node.js 16+ and npm
- Git

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/moviemate.git
   cd moviemate
   ```

2. **Create a virtual environment**
   ```bash
   cd backend
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the `backend` directory:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   TMDB_API_KEY=your-tmdb-api-key-optional
   ```
   
   To get a TMDB API key:
   - Visit https://www.themoviedb.org/
   - Sign up for an account
   - Go to Settings > API
   - Request an API key

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load initial data (optional)**
   ```bash
   python manage.py loaddata initial_data
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```
   
   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```
   
   The frontend will be available at `http://localhost:3000`

## 🚀 Setup Instructions

### Quick Start

1. **Start the backend server**
   ```bash
   cd backend
   python manage.py runserver
   ```

2. **Start the frontend server** (in a new terminal)
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open your browser**
   Navigate to `http://localhost:3000`

### First Time Setup

1. Add some platforms (Netflix, Prime, etc.) via the admin panel at `http://localhost:8000/admin`
2. Add some genres (Action, Comedy, Drama, etc.)
3. Start adding content either manually or via TMDB search

## 💻 Usage

### Adding Content

1. Click "Add Content" in the navigation bar
2. **Option 1**: Search TMDB
   - Select content type (Movie or TV Show)
   - Enter search query
   - Click "Import" on desired result
   
3. **Option 2**: Add manually
   - Fill in all required fields
   - Select genres and platform
   - Choose status
   - Click "Add Content"

### Tracking Progress

1. Navigate to a TV show's detail page
2. Use "Mark Episode Watched" section
3. Enter season and episode numbers
4. Click "Mark Watched"
5. View progress in the detail view

### Rating & Reviews

1. Open any content's detail page
2. Click stars to rate (1-10)
3. Add notes in the "Notes" field
4. Click "Generate Review from Notes" (optional)
5. Write your review
6. Click "Save Review"

### Viewing Statistics

1. Click "Statistics" in the navigation bar
2. View collection overview
3. Check watch time graphs
4. See status distribution charts

### Getting Recommendations

1. Rate several movies/shows
2. Click "Recommendations" in the navigation bar
3. View personalized suggestions based on your ratings

## 📡 API Endpoints

### Content
- `GET /api/content/` - List all content
- `GET /api/content/{id}/` - Get content details
- `POST /api/content/` - Create content
- `PUT /api/content/{id}/` - Update content
- `DELETE /api/content/{id}/` - Delete content
- `GET /api/content/movies/` - List all movies
- `GET /api/content/tv_shows/` - List all TV shows
- `GET /api/content/statistics/` - Get collection statistics
- `GET /api/content/recommendations/` - Get recommendations
- `GET /api/content/search_tmdb/` - Search TMDB
- `POST /api/content/import_from_tmdb/` - Import from TMDB
- `GET /api/content/{id}/completion_estimate/` - Get completion estimate

### Ratings
- `GET /api/ratings/` - List all ratings
- `POST /api/ratings/` - Create/update rating

### Reviews
- `GET /api/reviews/` - List all reviews
- `POST /api/reviews/` - Create review
- `POST /api/reviews/generate_from_notes/` - Generate review from notes

### Watch Progress
- `GET /api/watch-progress/` - List all progress
- `POST /api/watch-progress/mark_episode/` - Mark episode as watched

### Watch History
- `GET /api/watch-history/` - List watch history
- `GET /api/watch-history/statistics/` - Get watch time statistics

### Genres & Platforms
- `GET /api/genres/` - List all genres
- `POST /api/genres/` - Create genre
- `GET /api/platforms/` - List all platforms
- `POST /api/platforms/` - Create platform

## 📁 Project Structure

```
moviemate/
├── backend/
│   ├── api/
│   │   ├── models.py          # Database models
│   │   ├── serializers.py     # DRF serializers
│   │   ├── views.py           # API views
│   │   ├── urls.py            # URL routing
│   │   ├── utils.py           # Utility functions (TMDB, recommendations)
│   │   └── admin.py           # Django admin configuration
│   ├── moviemate/
│   │   ├── settings.py        # Django settings
│   │   ├── urls.py            # Main URL configuration
│   │   └── wsgi.py            # WSGI configuration
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API service functions
│   │   └── App.jsx            # Main app component
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 🚢 Deployment

### Backend (Railway/Heroku)

1. **Prepare for production**
   ```bash
   # Update settings.py DEBUG = False
   # Set ALLOWED_HOSTS
   # Use PostgreSQL database
   ```

2. **Deploy to Railway**
   - Connect your GitHub repo
   - Set environment variables
   - Deploy automatically

### Frontend (Vercel/Netlify)

1. **Build the frontend**
   ```bash
   npm run build
   ```

2. **Deploy to Vercel**
   ```bash
   npm install -g vercel
   vercel
   ```

3. **Update API URL** in `frontend/src/services/api.js` for production

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



## 🎯 Future Enhancements

- [ ] User authentication and profiles
- [ ] Watch party planner
- [ ] Social features (share collections)
- [ ] Advanced AI recommendations
- [ ] Export/import functionality
- [ ] Mobile app version
- [ ] Integration with more APIs (OMDB, Trakt)

## 🙏 Acknowledgments

- The Movie Database (TMDB) for API access
- Django and React communities
- All open-source contributors

## 👨‍💻 Developer

Name: Maanaz K Antony
GitHub: https://github.com/maanaz

Project Repo: https://github.com/maanaz/MovieMate

## 📄 License

This project is open-source and free to use.

---

Made with ❤️ for movie and TV show enthusiasts


