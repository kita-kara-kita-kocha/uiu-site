import React from 'react';
import { VideoItem } from '../types';

interface ThumbnailGridProps {
  items: VideoItem[];
  tabType: string;
  onVideoSelect: (video: { videoId: string; title: string; timestamps: string[] }) => void;
}

const ThumbnailGrid: React.FC<ThumbnailGridProps> = ({ items, tabType, onVideoSelect }) => {
  const getAdditionalClass = (item: VideoItem, tabType: string): string => {
    let additionalClass = tabType;
    
    if (tabType === 'youtube' && item.addAdditionalClass) {
      additionalClass += ' ' + item.addAdditionalClass.join(' ');
    }
    
    if (tabType === 'niconico_l') {
      const timeshiftMeta = item.metadata?.find(meta => meta.startsWith('タイムシフト視聴期限:'));
      if (timeshiftMeta) {
        const currentDate = new Date();
        const timeshiftLimitDate = new Date(timeshiftMeta.split('タイムシフト視聴期限: ')[1].trim());
        if (timeshiftLimitDate < currentDate || 
            timeshiftMeta === 'タイムシフト視聴期限: 視聴不可' || 
            timeshiftMeta === 'タイムシフト視聴期限: 不明') {
          additionalClass += ' timeshiftout';
        }
      } else {
        additionalClass += ' timeshiftout';
      }
    }
    
    if (tabType === 'fciu') {
      const viewingCondition = item.metadata?.find(meta => meta.startsWith('視聴条件:'));
      if (viewingCondition) {
        const condition = viewingCondition.split('視聴条件: ')[1].trim();
        if (condition === '会員のみ') {
          additionalClass += ' fciu-members-only';
        } else if (condition === '一部無料') {
          additionalClass += ' fciu-partial-free';
        } else if (condition === '全編無料') {
          additionalClass += ' fciu-full-free';
        }
      }
    }
    
    return additionalClass;
  };

  const handleItemClick = (item: VideoItem) => {
    if (item.video_url) {
      window.open(item.video_url, '_blank');
    } else {
      alert(`URL情報がありません。バグです。\nタイトル: ${item.title}\n画像: ${item.image}`);
    }
  };

  const handlePlayButtonClick = (e: React.MouseEvent, item: VideoItem) => {
    e.stopPropagation();
    if (item.videoId && item.title) {
      onVideoSelect({
        videoId: item.videoId,
        title: item.title,
        timestamps: item.timestamps || []
      });
    }
  };

  return (
    <div className="thumbnail-grid">
      {items.map((item, index) => (
        <div 
          key={index}
          className={`thumbnail-item ${getAdditionalClass(item, tabType)}`}
          onClick={() => handleItemClick(item)}
          style={{ position: 'relative' }}
        >
          <img 
            src={item.image} 
            alt={item.alt || item.title} 
            className="thumbnail-image"
          />
          
          {tabType === 'youtube' && item.videoId && 
           !(item.addAdditionalClass?.includes('subscriber_only')) && (
            <button 
              className="play-button"
              onClick={(e) => handlePlayButtonClick(e, item)}
            />
          )}
          
          <div className="thumbnail-info">
            <h3>{item.title}</h3>
            {item.description && <p>{item.description}</p>}
            {item.metadata?.map((meta, metaIndex) => (
              <p key={metaIndex}>{meta}</p>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ThumbnailGrid;
