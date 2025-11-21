import React, { useState, useEffect } from 'react'
import { contentAPI } from '../services/api'
import ContentCard from '../components/ContentCard'
import { FaSearch } from 'react-icons/fa'
import './Home.css'

const Movies = () => {
  const [movies, setMovies] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  useEffect(() => {
    loadMovies()
  }, [search, statusFilter])

  const loadMovies = async () => {
    try {
      setLoading(true)
      const response = await contentAPI.getMovies()
      let data = response.data.results || response.data

      if (search) {
        data = data.filter(m => 
          m.title.toLowerCase().includes(search.toLowerCase()) ||
          (m.director && m.director.toLowerCase().includes(search.toLowerCase()))
        )
      }

      if (statusFilter) {
        data = data.filter(m => m.status === statusFilter)
      }

      setMovies(data)
    } catch (error) {
      console.error('Error loading movies:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="home">
      <h1 className="page-title">Movies</h1>
      
      <div className="filters-section">
        <div className="search-box">
          <FaSearch className="search-icon" />
          <input
            type="text"
            placeholder="Search movies..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="filter-group">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">All Status</option>
            <option value="watching">Watching</option>
            <option value="completed">Completed</option>
            <option value="wishlist">Wishlist</option>
            <option value="paused">Paused</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="loading">Loading...</div>
      ) : movies.length === 0 ? (
        <div className="empty-state">
          <p>No movies found. Add some movies to get started!</p>
        </div>
      ) : (
        <div className="content-grid">
          {movies.map((movie) => (
            <ContentCard key={movie.id} content={movie} />
          ))}
        </div>
      )}
    </div>
  )
}

export default Movies


