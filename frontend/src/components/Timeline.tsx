import { EventTimelineItem } from '../lib/api'
import './Timeline.css'

interface TimelineProps {
  events: EventTimelineItem[]
}

function Timeline({ events }: TimelineProps) {
  if (events.length === 0) {
    return <div className="timeline-empty">No events found</div>
  }

  return (
    <div className="timeline">
      <h3>Provenance Timeline</h3>
      <div className="timeline-container">
        {events.map((event, index) => (
          <div key={event.event_hash} className="timeline-item">
            <div className="timeline-marker">
              <div className={`marker-dot ${event.signature_valid ? 'valid' : 'invalid'}`} />
              {index < events.length - 1 && <div className="timeline-line" />}
            </div>
            <div className="timeline-content">
              <div className="event-header">
                <span className="event-type">{event.event_type}</span>
                <span className="event-time">
                  {new Date(event.timestamp).toLocaleString()}
                </span>
              </div>
              <div className="event-details">
                <p><strong>Actor:</strong> {event.actor_id}</p>
                {event.prev_event_hash && (
                  <p><strong>Previous:</strong> <code>{event.prev_event_hash.substring(0, 16)}...</code></p>
                )}
                {event.anchored && event.batch_id && (
                  <p className="anchored-badge">
                    ✓ Anchored in batch: <code>{event.batch_id.substring(0, 8)}...</code>
                  </p>
                )}
                {!event.signature_valid && (
                  <p className="invalid-badge">✗ Signature invalid</p>
                )}
              </div>
              <details className="event-payload">
                <summary>Payload</summary>
                <pre>{JSON.stringify(event.payload, null, 2)}</pre>
              </details>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Timeline

