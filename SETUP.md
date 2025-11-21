# MovieMate - Quick Setup Guide

## Prerequisites

Before starting, ensure you have:
- Python 3.8 or higher installed
- Node.js 16+ and npm installed
- Git installed

## Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd moviemate
```

### 2. Backend Setup

#### 2.1 Create and Activate Virtual Environment

**Windows:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

#### 2.2 Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2.3 Configure Environment

Create a `.env` file in the `backend` directory:

```env
SECRET_KEY=your-secret-key-change-this-in-production
DEBUG=True
TMDB_API_KEY=your-tmdb-api-key-optional
```

**To get TMDB API Key:**
1. Visit https://www.themoviedb.org/
2. Create an account
3. Go to Settings > API
4. Request an API key (free)
5. Copy the API key to `.env` file

#### 2.4 Run Migrations

```bash
python manage.py migrate
```

#### 2.5 Seed Initial Data (Optional but Recommended)

```bash
python manage.py seed_data
```

This creates initial genres and platforms.

#### 2.6 Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

#### 2.7 Start Backend Server

```bash
python manage.py runserver
```

The backend will run on `http://localhost:8000`

### 3. Frontend Setup

#### 3.1 Navigate to Frontend Directory

Open a new terminal window:

```bash
cd frontend
```

#### 3.2 Install Dependencies

```bash
npm install
```

#### 3.3 Start Frontend Server

```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

### 4. Access the Application

1. Open your browser
2. Navigate to `http://localhost:3000`
3. Start adding movies and shows!

## First Steps

1. **Add Platforms** (via Admin Panel)
   - Go to `http://localhost:8000/admin`
   - Login with superuser credentials
   - Add streaming platforms (Netflix, Prime, etc.)

2. **Add Genres** (if not seeded)
   - Go to Admin Panel
   - Add genres (Action, Comedy, Drama, etc.)

3. **Add Content**
   - Click "Add Content" in the navigation
   - Use TMDB search or add manually
   - Start building your collection!

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
python manage.py runserver 8001
```

**Migration errors:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**Import errors:**
- Ensure virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt`

### Frontend Issues

**Port 3000 already in use:**
- Vite will automatically try the next available port
- Or modify `vite.config.js` to use a different port

**Module not found:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**CORS errors:**
- Ensure backend is running
- Check `backend/moviemate/settings.py` for CORS settings
- Ensure frontend is accessing correct backend URL

### TMDB Issues

**TMDB search not working:**
- Verify API key in `.env` file
- Check API key validity at TMDB website
- API key is optional - you can still add content manually

### Database Issues

**Database locked:**
- Stop the server
- Delete `db.sqlite3` if it exists
- Run migrations again: `python manage.py migrate`

## Production Setup

### Backend

1. Set `DEBUG=False` in `.env`
2. Set `ALLOWED_HOSTS` in `settings.py`
3. Use PostgreSQL instead of SQLite
4. Configure static files serving
5. Set up proper secret key

### Frontend

1. Build for production:
   ```bash
   npm run build
   ```
2. Update API URL in `src/services/api.js`
3. Deploy `dist` folder to hosting service

## Next Steps

- Add your favorite movies and shows
- Rate and review content
- Track your watching progress
- Explore recommendations
- View your statistics

## Support

For issues or questions:
- Email: doniya@sayonetech.com
- CC: ranju@sayonetech.com

Happy watching! 🎬


