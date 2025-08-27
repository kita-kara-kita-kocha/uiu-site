import React from 'react';
import { FilterState } from '../types';

interface FilterControlsProps {
  activeTab: string;
  filterState: FilterState;
  setFilterState: React.Dispatch<React.SetStateAction<FilterState>>;
  filteredCount: number;
  totalCount: number;
}

const FilterControls: React.FC<FilterControlsProps> = ({
  activeTab,
  filterState,
  setFilterState,
  filteredCount,
  totalCount
}) => {
  const handleYouTubeFilterChange = (checked: boolean) => {
    setFilterState(prev => ({
      ...prev,
      youtube: { ...prev.youtube, subscriberOnly: checked }
    }));
  };

  const handleFCIUFilterChange = (filterType: 'membersOnly' | 'partialFree' | 'fullFree', checked: boolean) => {
    setFilterState(prev => ({
      ...prev,
      fciu: { ...prev.fciu, [filterType]: checked }
    }));
  };

  const getFilterInfo = () => {
    if (activeTab === 'youtube' && filterState.youtube.subscriberOnly) {
      return `${filteredCount}件のメンバー限定コンテンツを表示中 (全${totalCount}件)`;
    }
    
    if (activeTab === 'fciu') {
      const { membersOnly, partialFree, fullFree } = filterState.fciu;
      const hasActiveFilter = membersOnly || partialFree || fullFree;
      
      if (hasActiveFilter) {
        const activeFilters = [];
        if (membersOnly) activeFilters.push('会員のみ');
        if (partialFree) activeFilters.push('一部無料');
        if (fullFree) activeFilters.push('全編無料');
        
        return `${filteredCount}件の${activeFilters.join('・')}コンテンツを表示中 (全${totalCount}件)`;
      }
    }
    
    return null;
  };

  if (activeTab !== 'youtube' && activeTab !== 'fciu') {
    return null;
  }

  return (
    <div className="filter-controls" id={`${activeTab}-filters`}>
      <div className={`filter-section ${activeTab === 'fciu' ? 'diagonal-filters' : ''}`}>
        {activeTab === 'youtube' && (
          <label className="filter-toggle">
            <input 
              type="checkbox" 
              checked={filterState.youtube.subscriberOnly}
              onChange={(e) => handleYouTubeFilterChange(e.target.checked)}
            />
            <span className="filter-slider"></span>
            <span className="filter-label">メンバー限定のみ表示</span>
          </label>
        )}
        
        {activeTab === 'fciu' && (
          <>
            <label className="filter-toggle">
              <input 
                type="checkbox" 
                checked={filterState.fciu.membersOnly}
                onChange={(e) => handleFCIUFilterChange('membersOnly', e.target.checked)}
              />
              <span className="filter-slider"></span>
              <span className="filter-label">会員のみ</span>
            </label>
            
            <label className="filter-toggle">
              <input 
                type="checkbox" 
                checked={filterState.fciu.partialFree}
                onChange={(e) => handleFCIUFilterChange('partialFree', e.target.checked)}
              />
              <span className="filter-slider"></span>
              <span className="filter-label">一部無料</span>
            </label>
            
            <label className="filter-toggle">
              <input 
                type="checkbox" 
                checked={filterState.fciu.fullFree}
                onChange={(e) => handleFCIUFilterChange('fullFree', e.target.checked)}
              />
              <span className="filter-slider"></span>
              <span className="filter-label">全編無料</span>
            </label>
          </>
        )}
      </div>
      
      {getFilterInfo() && (
        <div className="filter-info">
          {getFilterInfo()}
        </div>
      )}
    </div>
  );
};

export default FilterControls;
