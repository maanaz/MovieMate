import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { contentAPI, ratingAPI, reviewAPI, watchProgressAPI } from '../services/api'
import toast from 'react-hot-toast'
import { FaStar, FaClock, FaEdit, FaTrash, FaPlus } from 'react-icons/fa'
import './ContentDetail.css'

const ContentDetail = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [content, setContent] = useState(null)
  const [loading, setLoading] = useState(true)
  const [rating, setRating] = useState(0)
  const [review, setReview] = useState('')
  const [notes, setNotes] = useState('')
  const [season, setSeason] = useState(1)
  const [episode, setEpisode] = useState(1)
  const [estimate, setEstimate] = useState(null)

  useEffect(() => {
    loadContent()
  }, [id])

  useEffect(() => {
    if (content) {
      if (content.rating_value) {
        setRating(content.rating_value)
      }
      if (content.review_text) {
        setReview(content.review_text)
      }
      loadRating()
      loadReview()
      if (content.content_type === 'tv_show') {
        loadEstimate()
      }
    }
  }, [content])

  const loadContent = async () => {
    try {
      setLoading(true)
      const response = await contentAPI.get(id)
      setContent(response.data)
    } catch (error) {
      console.error('Error loading content:', error)
      toast.error('Error loading content')
    } finally {
      setLoading(false)
    }
  }

  const loadRating = async () => {
    try {
      const response = await ratingAPI.getAll()
      const ratings = response.data.results || response.data
      const contentRating = ratings.find(r => r.content === parseInt(id))
      if (contentRating) {
        setRating(contentRating.rating)
      } else if (content?.rating_value) {
        setRating(content.rating_value)
      }
    } catch (error) {
      console.error('Error loading rating:', error)
      if (content?.rating_value) {
        setRating(content.rating_value)
      }
    }
  }

  const loadReview = async () => {
    try {
      const response = await reviewAPI.getAll()
      const reviews = response.data.results || response.data
      const contentReview = reviews.find(r => r.content === parseInt(id))
      if (contentReview) {
        setReview(contentReview.review_text)
        setNotes(contentReview.notes)
      } else if (content?.review_text) {
        setReview(content.review_text)
      }
    } catch (error) {
      console.error('Error loading review:', error)
      if (content?.review_text) {
        setReview(content.review_text)
      }
    }
  }

  const loadEstimate = async () => {
    try {
      const response = await contentAPI.getCompletionEstimate(id)
      setEstimate(response.data)
    } catch (error) {
      console.error('Error loading estimate:', error)
    }
  }

  const handleRatingChange = async (newRating) => {
    try {
      setRating(newRating)
      await ratingAPI.create({
        content: parseInt(id),
        rating: newRating,
      })
      toast.success('Rating saved!')
    } catch (error) {
      console.error('Error saving rating:', error)
      toast.error('Error saving rating')
      setRating(0)
    }
  }

  const handleReviewSubmit = async (e) => {
    e.preventDefault()
    
    try {
      if (review.trim()) {
        await reviewAPI.create({
          content: parseInt(id),
          review_text: review,
          notes: notes,
        })
        toast.success('Review saved!')
      }
    } catch (error) {
      console.error('Error saving review:', error)
      toast.error('Error saving review')
    }
  }

  const generateReviewFromNotes = async () => {
    if (!notes.trim()) {
      toast.error('Please add some notes first')
      return
    }

    try {
      const response = await reviewAPI.generateFromNotes({
        content: parseInt(id),
        notes: notes,
      })
      setReview(response.data.review_text)
      toast.success('Review generated from notes!')
    } catch (error) {
      console.error('Error generating review:', error)
      toast.error('Error generating review')
    }
  }

  const handleMarkEpisode = async () => {
    try {
      await watchProgressAPI.markEpisode({
        content: parseInt(id),
        season: season,
        episode: episode,
      })
      toast.success(`Season ${season}, Episode ${episode} marked as watched!`)
      loadContent()
      loadEstimate()
    } catch (error) {
      console.error('Error marking episode:', error)
      toast.error('Error marking episode')
    }
  }

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this content?')) {
      return
    }

    try {
      await contentAPI.delete(id)
      toast.success('Content deleted!')
      navigate('/')
    } catch (error) {
      console.error('Error deleting content:', error)
      toast.error('Error deleting content')
    }
  }

  const statusColors = {
    watching: '#4CAF50',
    completed: '#2196F3',
    wishlist: '#FF9800',
    paused: '#9E9E9E',
  }

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  if (!content) {
    return <div className="empty-state">Content not found</div>
  }

  return (
    <div className="content-detail">
      <div className="detail-header">
        <div className="poster-section">
          {content.poster_url ? (
            <img src={content.poster_url} alt={content.title} className="poster" />
          ) : (
            <div className="placeholder-poster">No Poster</div>
          )}
        </div>

        <div className="info-section">
          <h1 className="detail-title">{content.title}</h1>
          
          {content.director && (
            <p className="detail-director">Director: {content.director}</p>
          )}
          
          {content.release_date && (
            <p className="detail-date">
              {content.content_type === 'movie' ? 'Released' : 'First Aired'}:{' '}
              {new Date(content.release_date).toLocaleDateString()}
            </p>
          )}

          <div className="detail-meta">
            <div className="status-control">
              <label className="status-label">Status:</label>
              <select
                value={content.status}
                onChange={async (e) => {
                  const newStatus = e.target.value
                  try {
                    await contentAPI.update(id, { status: newStatus })
                    toast.success('Status updated')
                    loadContent()
                  } catch (err) {
                    console.error('Error updating status:', err)
                    toast.error('Error updating status')
                  }
                }}
                className="status-select"
              >
                <option value="wishlist">Wishlist</option>
                <option value="watching">Watching</option>
                <option value="completed">Completed</option>
                <option value="paused">Paused</option>
              </select>
              <span 
                className="status-badge"
                style={{ backgroundColor: statusColors[content.status] }}
              >{content.status}</span>
            </div>
            
            {content.platform_name && (
              <span className="platform-badge">{content.platform_name}</span>
            )}

            {content.runtime && (
              <span className="runtime-badge">
                <FaClock /> {content.runtime} min
              </span>
            )}
          </div>

          {content.genre && content.genre.length > 0 && (
            <div className="detail-genres">
              {content.genre.map((g) => (
                <span key={g.id} className="genre-tag">{g.name}</span>
              ))}
            </div>
          )}

          {content.description && (
            <p className="detail-description">{content.description}</p>
          )}

          {content.content_type === 'tv_show' && (
            <div className="tv-show-info">
              <p>Seasons: {content.total_seasons}</p>
              <p>Episodes: {content.total_episodes}</p>
              {content.progress_info && (
                <p>Watched: {content.progress_info.total_watched_episodes || 0} episodes</p>
              )}
              {estimate && (
                <div className="estimate-info">
                  <p className="estimate-label">Completion Estimate:</p>
                  <p className="estimate-value">
                    {estimate.estimated_days} days ({estimate.remaining_episodes} episodes remaining)
                  </p>
                  <p className="estimate-progress">
                    {estimate.completion_percentage}% complete
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="detail-actions">
        <div className="action-section">
          <h2>Rating</h2>
          <div className="rating-input">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((value) => (
              <button
                key={value}
                className={`rating-star ${rating >= value ? 'active' : ''}`}
                onClick={() => handleRatingChange(value)}
              >
                <FaStar />
              </button>
            ))}
            {rating > 0 && <span className="rating-value">{rating}/10</span>}
          </div>
        </div>

        {content.content_type === 'tv_show' && (
          <div className="action-section">
            <h2>Mark Episode Watched</h2>
            <div className="episode-input">
              <label>
                Season:
                <input
                  type="number"
                  min="1"
                  value={season}
                  onChange={(e) => setSeason(parseInt(e.target.value))}
                />
              </label>
              <label>
                Episode:
                <input
                  type="number"
                  min="1"
                  value={episode}
                  onChange={(e) => setEpisode(parseInt(e.target.value))}
                />
              </label>
              <button onClick={handleMarkEpisode} className="mark-button">
                <FaPlus /> Mark Watched
              </button>
            </div>
          </div>
        )}

        <div className="action-section">
          <h2>Review</h2>
          <form onSubmit={handleReviewSubmit} className="review-form">
            <div className="form-group">
              <label>Notes</label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Add your personal notes..."
                rows="3"
              />
              <button
                type="button"
                onClick={generateReviewFromNotes}
                className="generate-button"
              >
                Generate Review from Notes
              </button>
            </div>
            <div className="form-group">
              <label>Review</label>
              <textarea
                value={review}
                onChange={(e) => setReview(e.target.value)}
                placeholder="Write your review..."
                rows="5"
                required
              />
            </div>
            <button type="submit" className="save-button">Save Review</button>
          </form>
        </div>

        <div className="action-section">
          <button onClick={handleDelete} className="delete-button">
            <FaTrash /> Delete Content
          </button>
        </div>
      </div>
    </div>
  )
}

export default ContentDetail

