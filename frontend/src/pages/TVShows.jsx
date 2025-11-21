import React, { useState, useEffect } from 'react'
import { contentAPI } from '../services/api'
import ContentCard from '../components/ContentCard'
import { FaSearch } from 'react-icons/fa'
import './Home.css'

const TVShows = () => {
  const [tvShows, setTVShows] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  useEffect(() => {
    loadTVShows()
  }, [search, statusFilter])

  const loadTVShows = async () => {
    try {
      setLoading(true)
      const response = await contentAPI.getTVShows()
      let data = response.data.results || response.data

      if (search) {
        data = data.filter(show => 
          show.title.toLowerCase().includes(search.toLowerCase())
        )
      }

      if (statusFilter) {
        data = data.filter(show => show.status === statusFilter)
      }

      setTVShows(data)
    } catch (error) {
      console.error('Error loading TV shows:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="home">
      <h1 className="page-title">TV Shows</h1>
      
      <div className="filters-section">
        <div className="search-box">
          <FaSearch className="search-icon" />
          <input
            type="text"
            placeholder="Search TV shows..."
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
      ) : tvShows.length === 0 ? (
        <div className="empty-state">
          <p>No TV shows found. Add some shows to get started!</p>
        </div>
      ) : (
        <div className="content-grid">
          {tvShows.map((show) => (
            <ContentCard key={show.id} content={show} />
          ))}
        </div>
      )}
    </div>
  )
}

export default TVShows


