import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { VideoData } from '../types';
import './CalendarPage.css';

interface CalendarModalEvent {
  type: 'youtube' | 'niconico' | 'fciu' | 'api';
  date: string;
  title: string;
  description?: string;
  thumbnail?: string;
}

const CalendarPage: React.FC = () => {
  const [currentYear, setCurrentYear] = useState<number>(new Date().getFullYear());
  const [currentMonth, setCurrentMonth] = useState<number>(new Date().getMonth());
  const [allEvents, setAllEvents] = useState<CalendarModalEvent[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [modalEvents, setModalEvents] = useState<CalendarModalEvent[]>([]);
  const [showModal, setShowModal] = useState<boolean>(false);

  const today = new Date();
  const todayDate = today.getDate();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const apiUrl = 'https://script.google.com/macros/s/AKfycbyzR2KODZn0JbfJ0084RTDgHLsbV-hE9ZKd1IyBW9s4ob2bkKGSIqFYDmeYmVN-FEQp/exec';
      
      const [youtubeResponse, niconicoResponse, fciuResponse, apiResponse] = await Promise.all([
        fetch(`/youtube.json?v=${Date.now()}`),
        fetch(`/niconico_l.json?v=${Date.now()}`),
        fetch(`/fciu.json?v=${Date.now()}`),
        fetch(`${apiUrl}?v=${Date.now()}`)
      ]);

      const [youtubeData, niconicoData, fciuData, apiData]: [VideoData, VideoData, VideoData, any] = await Promise.all([
        youtubeResponse.json(),
        niconicoResponse.json(),
        fciuResponse.json(),
        apiResponse.json()
      ]);

      const events: CalendarModalEvent[] = [
        ...youtubeData.items.map(item => ({
          type: 'youtube' as const,
          date: item.upload_date || '',
          title: item.title,
          description: item.description,
          thumbnail: item.image
        })),
        ...niconicoData.items.map(item => ({
          type: 'niconico' as const,
          date: item.upload_date || '',
          title: item.title,
          thumbnail: item.image
        })),
        ...fciuData.items.map(item => ({
          type: 'fciu' as const,
          date: item.upload_date || '',
          title: item.title,
          thumbnail: item.image
        })),
        ...(apiData.data || [])
      ];

      setAllEvents(events);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getDaysInMonth = (year: number, month: number) => {
    return new Date(year, month + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (year: number, month: number) => {
    return new Date(year, month, 1).getDay();
  };

  const handleDayClick = (day: number) => {
    const date = new Date(currentYear, currentMonth, day);
    const dateStr = date.toISOString().split('T')[0];
    
    const eventsForDate = allEvents.filter(event => {
      const eventDate = new Date(event.date);
      if (isNaN(eventDate.getTime())) {
        return false;
      }
      return eventDate.toISOString().split('T')[0] === dateStr;
    });

    if (eventsForDate.length > 0) {
      setModalEvents(eventsForDate);
      setShowModal(true);
    }
  };

  const hasEventOnDay = (day: number) => {
    const date = new Date(currentYear, currentMonth, day);
    const dateStr = date.toISOString().split('T')[0];
    
    return allEvents.some(event => {
      const eventDate = new Date(event.date);
      if (isNaN(eventDate.getTime())) {
        return false;
      }
      return eventDate.toISOString().split('T')[0] === dateStr;
    });
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    if (direction === 'prev') {
      if (currentMonth === 0) {
        setCurrentMonth(11);
        setCurrentYear(currentYear - 1);
      } else {
        setCurrentMonth(currentMonth - 1);
      }
    } else {
      if (currentMonth === 11) {
        setCurrentMonth(0);
        setCurrentYear(currentYear + 1);
      } else {
        setCurrentMonth(currentMonth + 1);
      }
    }
  };

  const renderCalendar = () => {
    const daysInMonth = getDaysInMonth(currentYear, currentMonth);
    const firstDay = getFirstDayOfMonth(currentYear, currentMonth);
    const days = [];

    // 空のセルを追加
    for (let i = 0; i < firstDay; i++) {
      days.push(<div key={`empty-${i}`} className="day"></div>);
    }

    // 日付のセルを追加
    for (let day = 1; day <= daysInMonth; day++) {
      const isToday = day === todayDate && 
                     currentYear === today.getFullYear() && 
                     currentMonth === today.getMonth();
      const hasEvent = hasEventOnDay(day);

      days.push(
        <div
          key={day}
          className={`day ${isToday ? 'current-day' : ''}`}
          onClick={() => handleDayClick(day)}
          style={{ cursor: hasEvent ? 'pointer' : 'default' }}
        >
          {day}
          {hasEvent && <span className="event-dot"></span>}
        </div>
      );
    }

    return days;
  };

  const getEventTitle = (event: CalendarModalEvent) => {
    let title = event.title;
    if (event.type === 'youtube') {
      title = "You Tube 憂世いう: " + event.title;
    } else if (event.type === 'niconico') {
      title = "ニコ生 ういせとおやすみ: " + event.title;
    } else if (event.type === 'fciu') {
      title = "FC いうねこないと: " + event.title;
    } else if (event.type === 'api') {
      title = "予定: " + event.title;
    }
    return title;
  };

  return (
    <div className="calendar-page">
      <div className="calendar-container">
        <Link to="/" className="back-button">&larr; 戻る</Link>
        <h1>カレンダー</h1>
        
        <div className="calendar-header">
          <button onClick={() => navigateMonth('prev')}>前月</button>
          <div className="year-month">
            {currentYear}年 {currentMonth + 1}月
          </div>
          <button onClick={() => navigateMonth('next')}>次月</button>
        </div>
        
        <div className="calendar">
          {renderCalendar()}
        </div>
        
        <div>
          <a 
            href="https://docs.google.com/spreadsheets/d/1DIAuLcJ2_80ftT25dLhq65AOa8bWFG7b4UBuOSwIDpg/edit?usp=sharing" 
            target="_blank" 
            rel="noopener noreferrer"
            className="spreadsheet-link"
          >
            参照してるスプレッドシート
          </a>
        </div>
      </div>

      {loading && (
        <div className="loader">読み込み中...</div>
      )}

      {showModal && (
        <div className="modal" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <span className="close-button" onClick={() => setShowModal(false)}>
              &times;
            </span>
            <div className="modal-events">
              {modalEvents.map((event, index) => (
                <div key={index} className={`calendar-modal-element ${event.type}-event`}>
                  <h3>{getEventTitle(event)}</h3>
                  <p>{new Date(event.date).toLocaleDateString()}</p>
                  {event.thumbnail && (
                    <img src={event.thumbnail} alt={event.title} />
                  )}
                  {event.description && <p>{event.description}</p>}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CalendarPage;
