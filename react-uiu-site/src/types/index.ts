export interface VideoItem {
  title: string;
  image: string;
  alt?: string;
  description?: string;
  metadata?: string[];
  upload_date?: string;
  video_url?: string;
  videoId?: string;
  timestamps?: string[];
  addAdditionalClass?: string[];
}

export interface VideoData {
  items: VideoItem[];
}

export interface FilterState {
  youtube: {
    subscriberOnly: boolean;
  };
  fciu: {
    membersOnly: boolean;
    partialFree: boolean;
    fullFree: boolean;
  };
}

export interface AnalyticsData {
  each_video: {
    title: string;
    views: {
      v_datetime: string;
      view_count: number;
    }[];
  }[];
}

export interface CalendarEvent {
  type: 'youtube' | 'niconico' | 'fciu' | 'api';
  date: string;
  title: string;
  description?: string;
  thumbnail?: string;
}
