// Article related types
export interface Entity {
  name: string;
  type: string;
}

export interface ContentAnalysis {
  keywords: string[];
  topics: string[];
  summary: string;
  sentiment: 'positive' | 'neutral' | 'negative';
  category: string;
  entities: Entity[];
}

export interface TechDetection {
  is_tech_related: boolean;
  categories: string[];
  confidence: number;
  matched_keywords: string[];
}

export interface Article {
  id: string;
  url: string;
  title: string;
  category: string;
  published_time: string;
  content: string;
  tech_detection?: TechDetection;
  content_analysis?: ContentAnalysis;
  created_at: string;
}
