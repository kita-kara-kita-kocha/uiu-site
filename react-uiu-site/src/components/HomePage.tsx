import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { VideoData, VideoItem, FilterState } from '../types';
import VideoModal from './VideoModal';
import AgeVerificationModal from './AgeVerificationModal';
import FilterControls from './FilterControls';
import ThumbnailGrid from './ThumbnailGrid';
import './HomePage.css';

const HomePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('youtube');
  const [data, setData] = useState<{ [key: string]: VideoData }>({});
  const [filterState, setFilterState] = useState<FilterState>({
    youtube: { subscriberOnly: false },
    fciu: { membersOnly: false, partialFree: false, fullFree: false }
  });
  const [selectedVideo, setSelectedVideo] = useState<{
    videoId: string;
    title: string;
    timestamps: string[];
  } | null>(null);
  const [ageVerified, setAgeVerified] = useState<boolean>(false);
  const [showAgeModal, setShowAgeModal] = useState<boolean>(false);

  useEffect(() => {
    // 初期データ読み込み
    loadTabData('youtube');
    loadTabData('niconico_l');
    loadTabData('fciu');
    loadTabData('secret_ac');
  }, []);

  const loadTabData = async (tabName: string) => {
    try {
      const response = await fetch(`/${tabName}.json?v=${Date.now()}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const tabData: VideoData = await response.json();
      setData(prev => ({ ...prev, [tabName]: tabData }));
    } catch (error) {
      console.error(`Error loading ${tabName}.json:`, error);
      setData(prev => ({ ...prev, [tabName]: { items: [] } }));
    }
  };

  const handleTabChange = (tabName: string) => {
    if (tabName === 'secret_ac' && !ageVerified) {
      setShowAgeModal(true);
      return;
    }
    setActiveTab(tabName);
  };

  const handleAgeVerification = (verified: boolean) => {
    setShowAgeModal(false);
    if (verified) {
      setAgeVerified(true);
      setActiveTab('secret_ac');
    } else {
      setActiveTab('youtube');
    }
  };

  const filterItems = (items: VideoItem[], tabType: string): VideoItem[] => {
    if (tabType === 'youtube' && filterState.youtube.subscriberOnly) {
      return items.filter(item => 
        item.addAdditionalClass && item.addAdditionalClass.includes('subscriber_only')
      );
    }
    
    if (tabType === 'fciu') {
      const { membersOnly, partialFree, fullFree } = filterState.fciu;
      if (membersOnly || partialFree || fullFree) {
        return items.filter(item => {
          const viewingCondition = item.metadata?.find(meta => meta.startsWith('視聴条件:'));
          if (!viewingCondition) return false;
          
          const condition = viewingCondition.split('視聴条件: ')[1].trim();
          
          if (membersOnly && condition === '会員のみ') return true;
          if (partialFree && condition === '一部無料') return true;
          if (fullFree && condition === '全編無料') return true;
          
          return false;
        });
      }
    }
    
    return items;
  };

  const currentData = data[activeTab]?.items || [];
  const filteredData = filterItems(currentData, activeTab);

  return (
    <div className="container">
      <header>
        <div className="header-background">
          <svg className="background-pattern" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid slice">
            <defs>
              <pattern id="hearts" x="0" y="0" width="50" height="50" patternUnits="userSpaceOnUse">
                <path d="M25,15 C22,10 16,10 14,15 C12,10 6,10 4,15 C4,22 14,30 14,30 C14,30 24,22 24,15 Z" fill="#87ceeb" opacity="0.4"/>
                <path d="M40,35 C38.5,32 35,32 33.5,35 C32,32 28.5,32 27,35 C27,38 33.5,42 33.5,42 C33.5,42 40,38 40,35 Z" fill="#add8e6" opacity="0.6"/>
                <path d="M15,40 C13.5,37 10,37 8.5,40 C7,37 3.5,37 2,40 C2,43 8.5,47 8.5,47 C8.5,47 15,43 15,40 Z" fill="#b0e0e6" opacity="0.5"/>
                <circle cx="45" cy="10" r="1.5" fill="#87ceeb" opacity="0.7"/>
                <circle cx="8" cy="25" r="1" fill="#add8e6" opacity="0.8"/>
              </pattern>
              
              <pattern id="clouds" x="0" y="0" width="80" height="60" patternUnits="userSpaceOnUse">
                <g fill="white" opacity="0.6">
                  <circle cx="20" cy="30" r="8"/>
                  <circle cx="30" cy="30" r="10"/>
                  <circle cx="40" cy="30" r="8"/>
                  <circle cx="25" cy="22" r="6"/>
                  <circle cx="35" cy="22" r="7"/>
                </g>
                <g fill="white" opacity="0.4">
                  <circle cx="65" cy="15" r="4"/>
                  <circle cx="70" cy="15" r="5"/>
                  <circle cx="75" cy="15" r="4"/>
                  <circle cx="68" cy="10" r="3"/>
                  <circle cx="72" cy="10" r="3"/>
                </g>
                <g fill="white" opacity="0.3">
                  <circle cx="10" cy="50" r="2"/>
                  <circle cx="13" cy="50" r="3"/>
                  <circle cx="16" cy="50" r="2"/>
                  <circle cx="13" cy="47" r="2"/>
                </g>
              </pattern>
              
              <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#e6f3ff" stopOpacity={1} />
                <stop offset="25%" stopColor="#cce7ff" stopOpacity={1} />
                <stop offset="50%" stopColor="#b3daff" stopOpacity={1} />
                <stop offset="75%" stopColor="#99ccff" stopOpacity={1} />
                <stop offset="100%" stopColor="#80bfff" stopOpacity={1} />
              </linearGradient>
            </defs>
            <rect x="0" y="0" width="100%" height="100%" fill="url(#bgGradient)"/>
            <rect x="0" y="0" width="100%" height="100%" fill="url(#clouds)"/>
            <rect x="0" y="0" width="100%" height="100%" fill="url(#hearts)"/>
          </svg>
        </div>
        <h1>(非公式)ういせいういんふぉ</h1>
        <div className="menu">
          <Link to="/analytics" className="menu-item">解析ツール</Link>
          <Link to="/calendar" className="menu-item">カレンダー</Link>
        </div>
        
        <div className="tab-navigation">
          <button 
            className={`tab-button ${activeTab === 'youtube' ? 'active' : ''}`}
            onClick={() => handleTabChange('youtube')}
          >
            YouTube
          </button>
          <button 
            className={`tab-button ${activeTab === 'niconico_l' ? 'active' : ''}`}
            onClick={() => handleTabChange('niconico_l')}
          >
            ういせとおやすみ<br />ニコニコ
          </button>
          <button 
            className={`tab-button ${activeTab === 'fciu' ? 'active' : ''}`}
            onClick={() => handleTabChange('fciu')}
          >
            いうねこないと<br />FC
          </button>
          <button 
            className={`tab-button secret ${activeTab === 'secret_ac' ? 'active' : ''}`}
            onClick={() => handleTabChange('secret_ac')}
          >
            裏垢
          </button>
        </div>
      </header>

      <main className="tab-content active">
        <FilterControls 
          activeTab={activeTab}
          filterState={filterState}
          setFilterState={setFilterState}
          filteredCount={filteredData.length}
          totalCount={currentData.length}
        />
        
        <ThumbnailGrid 
          items={filteredData}
          tabType={activeTab}
          onVideoSelect={setSelectedVideo}
        />
      </main>

      {selectedVideo && (
        <VideoModal 
          videoId={selectedVideo.videoId}
          title={selectedVideo.title}
          timestamps={selectedVideo.timestamps}
          onClose={() => setSelectedVideo(null)}
        />
      )}

      {showAgeModal && (
        <AgeVerificationModal onVerify={handleAgeVerification} />
      )}
    </div>
  );
};

export default HomePage;
