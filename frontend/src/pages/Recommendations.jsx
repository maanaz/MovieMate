import React, { useState, useEffect } from 'react'
import { contentAPI } from '../services/api'
import ContentCard from '../components/ContentCard'
import { FaMagic } from 'react-icons/fa'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import './Home.css'

const Recommendations = () => {
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    loadRecommendations()
  }, [])

  const loadRecommendations = async () => {
    try {
      setLoading(true)
      const response = await contentAPI.getRecommendations()
      setRecommendations(response.data || [])
    } catch (error) {
      console.error('Error loading recommendations:', error)
    } finally {
      setLoading(false)
    }
  }

  const importTmdbItem = async (item) => {
    try {
      const payload = { tmdb_id: item.tmdb_id, content_type: 'movie' }
      const res = await contentAPI.importFromTMDB(payload)
      const newId = res.data.id || (res.data.data && res.data.data.id)
      toast.success('Imported to your collection')
      if (newId) {
        navigate(`/content/${newId}`)
      } else {
        // refresh recommendations if no id returned
        loadRecommendations()
      }
    } catch (err) {
      console.error('Error importing recommendation:', err)
      toast.error('Failed to import item')
    }
  }

  return (
    <div className="home">
      <h1 className="page-title">
        <FaMagic /> Recommendations
      </h1>
      
      <div className="recommendations-intro" style={{
        background: 'white',
        padding: '1.5rem',
        borderRadius: '12px',
        marginBottom: '2rem',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
      }}>
        <p style={{ margin: 0, color: '#666', lineHeight: '1.6' }}>
          These recommendations are based on your watch history and ratings. 
          Content you've highly rated helps us suggest similar genres and titles you might enjoy!
        </p>
      </div>

      {loading ? (
        <div className="loading">Loading recommendations...</div>
      ) : recommendations.length === 0 ? (
        <div className="empty-state">
          <p>
            No recommendations available yet. Start rating your movies and shows 
            to get personalized recommendations!
          </p>
        </div>
      ) : (
        <>
          <div className="content-grid">
            {recommendations.map((item) => (
              item.id ? (
                <ContentCard key={item.id} content={item} />
              ) : (
                <div key={item.tmdb_id} className="recommendation-card">
                  <div className="card-image">
                    {item.poster_url ? (
                      <img src={item.poster_url} alt={item.title} />
                    ) : (
                      <div className="placeholder-image">No Image</div>
                    )}
                  </div>
                  <div className="card-content">
                    <h3 className="card-title">{item.title}</h3>
                    {item.release_date && (
                      <p className="card-date">{new Date(item.release_date).getFullYear()}</p>
                    )}
                    {item.description && (
                      <p className="card-desc">{item.description.length > 140 ? item.description.slice(0, 140) + '...' : item.description}</p>
                    )}
                    <div className="card-actions">
                      <button className="import-button" onClick={() => importTmdbItem(item)}>Add to collection</button>
                    </div>
                  </div>
                </div>
              )
            ))}
          </div>
        </>
      )}
    </div>
  )
}

export default Recommendations
