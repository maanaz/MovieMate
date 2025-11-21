import React, { useState, useEffect } from 'react'
import { contentAPI } from '../services/api'
import ContentCard from '../components/ContentCard'
import { FaSearch, FaFilter, FaSort } from 'react-icons/fa'
import './Home.css'

const Home = () => {
  const [content, setContent] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    search: '',
    status: '',
    platform: '',
    genre: '',
    content_type: '',
    ordering: '-created_at',
  })

  useEffect(() => {
    loadContent()
  }, [filters])

  const loadContent = async () => {
    try {
      setLoading(true)
      const params = {}
      
      if (filters.search) params.search = filters.search
      if (filters.status) params.status = filters.status
      if (filters.platform) params.platform = filters.platform
      if (filters.genre) params.genre = filters.genre
      if (filters.content_type) params.content_type = filters.content_type
      if (filters.ordering) params.ordering = filters.ordering

      const response = await contentAPI.getAll(params)
      setContent(response.data.results || response.data)
    } catch (error) {
      console.error('Error loading content:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFilterChange = (key, value) => {
    setFilters({ ...filters, [key]: value })
  }

  return (
    <div className="home">
      <h1 className="page-title">My Collection</h1>
      
      <div className="filters-section">
        <div className="search-box">
          <FaSearch className="search-icon" />
          <input
            type="text"
            placeholder="Search movies and shows..."
            value={filters.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            className="search-input"
          />
        </div>

        <div className="filter-group">
          <select
            value={filters.content_type}
            onChange={(e) => handleFilterChange('content_type', e.target.value)}
            className="filter-select"
          >
            <option value="">All Types</option>
            <option value="movie">Movies</option>
            <option value="tv_show">TV Shows</option>
          </select>

          <select
            value={filters.status}
            onChange={(e) => handleFilterChange('status', e.target.value)}
            className="filter-select"
          >
            <option value="">All Status</option>
            <option value="watching">Watching</option>
            <option value="completed">Completed</option>
            <option value="wishlist">Wishlist</option>
            <option value="paused">Paused</option>
          </select>

          <select
            value={filters.ordering}
            onChange={(e) => handleFilterChange('ordering', e.target.value)}
            className="filter-select"
          >
            <option value="-created_at">Newest First</option>
            <option value="created_at">Oldest First</option>
            <option value="title">Title A-Z</option>
            <option value="-title">Title Z-A</option>
            <option value="-release_date">Newest Release</option>
            <option value="release_date">Oldest Release</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="loading">Loading...</div>
      ) : content.length === 0 ? (
        <div className="empty-state">
          <p>No content found. Add some movies or shows to get started!</p>
        </div>
      ) : (
        <div className="content-grid">
          {content.map((item) => (
            <ContentCard key={item.id} content={item} />
          ))}
        </div>
      )}
    </div>
  )
}

export default Home


