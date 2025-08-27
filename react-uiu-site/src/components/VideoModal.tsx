import React, { useEffect, useRef } from 'react';

interface VideoModalProps {
  videoId: string;
  title: string;
  timestamps: string[];
  onClose: () => void;
}

const VideoModal: React.FC<VideoModalProps> = ({ videoId, title, timestamps, onClose }) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    // ESCキーでモーダルを閉じる
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'auto';
    };
  }, [onClose]);

  const handleBackgroundClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handleTimestampClick = (timestamp: string) => {
    const match = timestamp.match(/([0-9]{1,2}:[0-9]{2}(?::[0-9]{2})?)/);
    const timeStr = match ? match[1] : timestamp.trim();
    const timeParts = timeStr.split(':').map(part => parseInt(part, 10));
    let seconds = 0;
    
    if (timeParts.length === 3) {
      // HH:MM:SS 形式
      seconds = timeParts[0] * 3600 + timeParts[1] * 60 + timeParts[2];
    } else if (timeParts.length === 2) {
      // MM:SS 形式
      seconds = timeParts[0] * 60 + timeParts[1];
    } else if (timeParts.length === 1) {
      // SS 形式
      seconds = timeParts[0];
    }

    jumpToTime(seconds);
  };

  const jumpToTime = (seconds: number) => {
    // postMessage APIを使用
    try {
      if (iframeRef.current?.contentWindow) {
        iframeRef.current.contentWindow.postMessage(
          JSON.stringify({
            event: 'command',
            func: 'seekTo',
            args: [seconds, true]
          }), 
          '*'
        );
      }
    } catch (e) {
      console.log('postMessage failed, trying URL reload method');
    }
    
    // URL再読み込み（フォールバック）
    setTimeout(() => {
      if (iframeRef.current) {
        const baseUrl = `https://www.youtube.com/embed/${videoId}`;
        const newSrc = `${baseUrl}?autoplay=1&rel=0&enablejsapi=1&origin=${window.location.origin}&start=${seconds}`;
        iframeRef.current.src = newSrc;
      }
    }, 100);
  };

  return (
    <div className="video-modal show" onClick={handleBackgroundClick}>
      <div className="video-container">
        <button className="video-close" onClick={onClose}>
          &times;
        </button>
        <div className="video-title">{title}</div>
        <iframe
          ref={iframeRef}
          className="video-iframe"
          src={`https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0&enablejsapi=1&origin=${window.location.origin}`}
          allowFullScreen
          title={title}
        />
        
        <div className="timestamp-section">
          <h4>タイムスタンプ</h4>
          <ul className="video-timestamps">
            {timestamps.length > 0 ? (
              timestamps.map((timestamp, index) => (
                <li 
                  key={index}
                  onClick={() => handleTimestampClick(timestamp)}
                >
                  {timestamp}
                </li>
              ))
            ) : (
              <li>タイムスタンプはありません。</li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default VideoModal;
