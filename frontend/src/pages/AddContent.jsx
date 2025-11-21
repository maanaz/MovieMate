import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { contentAPI, genreAPI, platformAPI } from '../services/api'
import toast from 'react-hot-toast'
import { FaSearch, FaSpinner, FaTimes } from 'react-icons/fa'
import './AddContent.css'

const AddContent = () => {
  const navigate = useNavigate()
  const [contentType, setContentType] = useState('movie')
  const [dataSource, setDataSource] = useState('tmdb')
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [searching, setSearching] = useState(false)
  const [genres, setGenres] = useState([])
  const [platforms, setPlatforms] = useState([])
  const [formData, setFormData] = useState({
    title: '',
    director: '',
    description: '',
    release_date: '',
    genre: [],
    platform: '',
    status: 'wishlist',
    content_type: 'movie',
    poster_url: '',
    runtime: '',
    total_seasons: 1,
    total_episodes: 0,
  })

  useEffect(() => {
    loadGenresAndPlatforms()
  }, [])

  useEffect(() => {
    setSearchResults([])
  }, [dataSource, contentType])

  const loadGenresAndPlatforms = async () => {
    try {
      const [genresRes, platformsRes] = await Promise.all([
        genreAPI.getAll(),
        platformAPI.getAll(),
      ])
      setGenres(genresRes.data.results || genresRes.data)
      setPlatforms(platformsRes.data.results || platformsRes.data)
    } catch (error) {
      console.error('Error loading genres/platforms:', error)
    }
  }

  const searchExternal = async () => {
    if (!searchQuery.trim()) {
      toast.error('Please enter a search query')
      return
    }

    try {
      setSearching(true)
      const results =
        dataSource === 'tmdb'
          ? await contentAPI.searchTMDB(searchQuery, contentType)
          : await contentAPI.searchOMDB(searchQuery, contentType)
      setSearchResults(results.data)
    } catch (error) {
      console.error('Error searching external source:', error)
      toast.error('Error searching. Please try again.')
    } finally {
      setSearching(false)
    }
  }

  const importFromTMDB = async (tmdbResult) => {
    try {
      const response = await contentAPI.importFromTMDB({
        tmdb_id: tmdbResult.tmdb_id,
        content_type: contentType,
        status: formData.status,
      })
      
      toast.success('Content imported successfully!')
      navigate(`/content/${response.data.id}`)
    } catch (error) {
      console.error('Error importing from TMDB:', error)
      toast.error('Error importing content. You can add it manually.')
      // Fill form with TMDB data
      setFormData({
        ...formData,
        title: tmdbResult.title,
        description: tmdbResult.description || '',
        release_date: tmdbResult.release_date || '',
        poster_url: tmdbResult.poster_url || '',
        content_type: contentType,
      })
      setSearchResults([])
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    try {
      const submitData = {
        ...formData,
        genre: formData.genre.map(id => parseInt(id)),
        platform: formData.platform ? parseInt(formData.platform) : null,
        runtime: formData.runtime ? parseInt(formData.runtime) : null,
        release_date: formData.release_date || null,
        total_seasons: formData.content_type === 'tv_show' ? parseInt(formData.total_seasons) : null,
        total_episodes: formData.content_type === 'tv_show' ? parseInt(formData.total_episodes) : null,
      }

      if (formData.content_type === 'tv_show') {
        submitData.episodes_per_season = {}
      }

      const response = await contentAPI.create(submitData)
      toast.success('Content added successfully!')
      navigate(`/content/${response.data.id}`)
    } catch (error) {
      console.error('Error creating content:', error)
      toast.error('Error creating content. Please check all fields.')
    }
  }

  const handleChange = (e) => {
    const { name, value, type } = e.target
    
    if (type === 'checkbox') {
      const checked = e.target.checked
      if (name === 'genre') {
        setFormData({
          ...formData,
          genre: checked
            ? [...formData.genre, value]
            : formData.genre.filter(id => id !== value),
        })
      }
    } else {
      setFormData({ ...formData, [name]: value })
    }
  }

  return (
    <div className="add-content">
      <h1 className="page-title">Add Content</h1>
      
      <div className="add-content-container">
        {/* TMDB Search Section */}
        <div className="tmdb-search-section">
          <h2>Search TMDB</h2>
          <div className="search-controls">
            <select
              value={contentType}
              onChange={(e) => {
                setContentType(e.target.value)
                setFormData({ ...formData, content_type: e.target.value })
              }}
              className="content-type-select"
            >
              <option value="movie">Movie</option>
              <option value="tv_show">TV Show</option>
            </select>
            <select
              value={formData.status}
              onChange={(e) => setFormData({ ...formData, status: e.target.value })}
              className="status-select"
              title="Set initial status for imported content"
            >
              <option value="wishlist">Wishlist</option>
              <option value="watching">Watching</option>
              <option value="completed">Completed</option>
              <option value="paused">Paused</option>
            </select>
              <input
              type="text"
              placeholder="Search for movies or shows..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && searchExternal()}
              className="search-input"
            />
            <button onClick={searchExternal} disabled={searching} className="search-button">
              {searching ? <FaSpinner className="spinner" /> : <FaSearch />}
              Search
            </button>
          </div>

          {searchResults.length > 0 && (
            <div className="search-results">
              <h3>Search Results</h3>
              <div className="results-grid">
                {searchResults.map((result) => (
                  <div key={result.tmdb_id} className="result-card">
                    {result.poster_url ? (
                      <img src={result.poster_url} alt={result.title} />
                    ) : (
                      <div className="no-poster">No Image</div>
                    )}
                    <div className="result-info">
                      <h4>{result.title}</h4>
                      <div className="meta-row">
                        {result.release_date && (
                          <span className="year">{new Date(result.release_date).getFullYear()}</span>
                        )}
                        {result.runtime && (
                          <span className="runtime">{result.runtime} min</span>
                        )}
                      </div>
                      {result.description && (
                        <p className="short-desc">{result.description.length > 180 ? result.description.slice(0, 180) + '...' : result.description}</p>
                      )}
                      <button
                        onClick={() => importFromTMDB(result)}
                        className="import-button"
                      >
                        Import
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Manual Form Section */}
        <div className="manual-form-section">
          <h2>Or Add Manually</h2>
          <form onSubmit={handleSubmit} className="content-form">
            <div className="form-group">
              <label>Content Type</label>
              <select
                name="content_type"
                value={formData.content_type}
                onChange={handleChange}
                required
              >
                <option value="movie">Movie</option>
                <option value="tv_show">TV Show</option>
              </select>
            </div>

            <div className="form-group">
              <label>Title *</label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label>Director</label>
              <input
                type="text"
                name="director"
                value={formData.director}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label>Description</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows="4"
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Release Date</label>
                <input
                  type="date"
                  name="release_date"
                  value={formData.release_date}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label>Status</label>
                <select
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                >
                  <option value="wishlist">Wishlist</option>
                  <option value="watching">Watching</option>
                  <option value="completed">Completed</option>
                  <option value="paused">Paused</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Platform</label>
                <select
                  name="platform"
                  value={formData.platform}
                  onChange={handleChange}
                >
                  <option value="">None</option>
                  {platforms.map((platform) => (
                    <option key={platform.id} value={platform.id}>
                      {platform.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Runtime (minutes)</label>
                <input
                  type="number"
                  name="runtime"
                  value={formData.runtime}
                  onChange={handleChange}
                  min="1"
                />
              </div>
            </div>

            {formData.content_type === 'tv_show' && (
              <div className="form-row">
                <div className="form-group">
                  <label>Total Seasons</label>
                  <input
                    type="number"
                    name="total_seasons"
                    value={formData.total_seasons}
                    onChange={handleChange}
                    min="1"
                  />
                </div>

                <div className="form-group">
                  <label>Total Episodes</label>
                  <input
                    type="number"
                    name="total_episodes"
                    value={formData.total_episodes}
                    onChange={handleChange}
                    min="0"
                  />
                </div>
              </div>
            )}

            <div className="form-group">
              <label>Genres</label>
              <div className="genre-checkboxes">
                {genres.map((genre) => (
                  <label key={genre.id} className="checkbox-label">
                    <input
                      type="checkbox"
                      name="genre"
                      value={genre.id}
                      checked={formData.genre.includes(String(genre.id))}
                      onChange={handleChange}
                    />
                    {genre.name}
                  </label>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label>Poster URL</label>
              <input
                type="url"
                name="poster_url"
                value={formData.poster_url}
                onChange={handleChange}
              />
            </div>

            <button type="submit" className="submit-button">
              Add Content
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

export default AddContent

