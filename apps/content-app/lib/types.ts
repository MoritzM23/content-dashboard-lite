/**
 * UI-Mode: Live (echte Daten) vs. Demo (Storytelling-Snapshot).
 * Persistent gespeichert über `lib/mode-context.tsx`.
 */
export type Mode = 'live' | 'demo';

/**
 * Types für den content_intel-Block aus dashboard-data.json.
 * Quelle: scripts/generate_dashboard_data.py -> load_content_intel()
 */

export type AiStandard = {
  sentiment?: 'positive' | 'neutral' | 'negative' | 'mixed';
  sentiment_score?: number;
  topic_tag?: string;
  topic_subtags?: string[];
  hook_score?: number;
  hook_type?: string;
  audience_questions?: string[];
  key_observations?: string[];
};

export type AiDeep = {
  why_it_worked?: string;
  replicable_patterns?: string[];
  recommendation?: string;
  audience_insight?: string;
  hook_breakdown?: string;
  theme_position?: string;
  viral_factors?: Record<string, number>;
};

export type Reel = {
  shortcode: string;
  url: string;
  posted: string;            // YYYY-MM-DD
  posted_at?: string;        // full ISO
  posted_hour?: number;
  posted_dayofweek?: string;
  views: number;
  plays?: number;
  likes: number;
  comments: number;
  engagement_rate: number;
  like_rate?: number;
  comment_rate?: number;
  comment_to_like_ratio?: number;
  video_duration?: number;
  hashtags?: string[];
  caption_full?: string;
  caption_snippet?: string;
  caption_length?: number;
  transcript?: string;
  transcript_snippet?: string;
  summary?: string;
  audio?: {
    audio_id?: string;
    title?: string;
    artist?: string;
    is_original?: boolean;
  };
  comments_stats?: {
    total_count?: number;
    top_likes?: number;
    avg_likes?: number;
    unique_commenters?: number;
    top_commenter?: { username: string; comments: number } | null;
    reply_ratio?: number;
    time_span_hours?: number;
    top_words?: Array<{ word: string; count: number }>;
  };
  ai_standard?: AiStandard;
  ai_deep?: AiDeep;
  handle?: string;
  /** Relativer Vault-Pfad zur final.mp4 — leer wenn Reel nicht in Library liegt. */
  final_mp4?: string;
};

export type HashtagPerformance = {
  tag: string;
  count: number;
  avg_er: number;
  avg_views: number;
  top_reel_shortcode: string;
  top_reel_er: number;
};

export type PostingPatternHour = { hour: number; count: number; avg_er: number };
export type PostingPatternDow = { day: string; count: number; avg_er: number };

export type CreatorStats = {
  handle: string;
  reels_count: number;
  avg_views: number;
  avg_likes: number;
  avg_comments: number;
  avg_engagement_rate: number;
  total_views: number;
  total_likes: number;
  total_comments: number;
  max_views: number;
  max_likes: number;
  max_engagement_rate: number;
  min_views: number;
  min_likes: number;
  min_engagement_rate: number;
  median_engagement_rate: number;
  avg_like_rate: number;
  avg_comment_rate: number;
  avg_comment_to_like_ratio: number;
  avg_bounce_rate: number | null;
  bounce_coverage: number;
  avg_video_duration: number;
  avg_caption_length: number;
  transcript_coverage: number;
  summary_coverage: number;
  post_frequency_days: number;
  top_hashtags: Array<{ tag: string; count: number }>;
  hashtag_performance?: HashtagPerformance[];
  posting_pattern_hours?: PostingPatternHour[];
  posting_pattern_dow?: PostingPatternDow[];
  best_hour?: number | null;
  best_dayofweek?: string | null;
  best_reel_er?: Reel | null;
  best_reel_views?: Reel | null;
  worst_reel_er?: Reel | null;
  top_reel?: Reel | null;
  reels: Reel[];
};

export type RangeKpi = {
  count: number;
  total_views: number;
  total_likes: number;
  total_comments: number;
  avg_views: number;
  avg_likes: number;
  avg_comments: number;
  avg_engagement_rate: number;
  // Comment-Rate = comments/views * 100, ohne Likes — separater Engagement-Indikator
  avg_comment_rate?: number;
  best_reel_shortcode: string | null;
  best_reel_er: number;
  best_comment_rate?: number;
  /** View-Delta aus reel_history.db: "neue Views in den letzten N Tagen über ALLE
   * Reels", auch für Reels die schon vor dem Fenster gepostet wurden. Quelle:
   * reel_history.all_reels_delta(). Nur für 7d/30d. */
  views_delta_total?: number;
  likes_delta_total?: number;
  comments_delta_total?: number;
  /** Anzahl Reels die in der Time-Series sind (Delta-Basis). */
  reels_tracked?: number;
  /** Start des Delta-Fensters als YYYY-MM-DD. */
  window_start?: string;
};

export type RangeKpis = {
  today: RangeKpi;
  '7d': RangeKpi;
  '30d': RangeKpi;
  all: RangeKpi;
  /** Datum des ältesten Snapshots in reel_history.db. Wenn ein Fenster (z.B. 30d)
   * vor diesem Datum beginnt, ist die Delta-Zahl artificially niedriger weil
   * History fehlt. UI zeigt einen Hinweis. */
  history_first_snapshot?: string;
};

export type TopicCluster = {
  themes?: Array<{
    name: string;
    reel_shortcodes?: string[];
    avg_engagement_rate?: number;
    top_reel_shortcode?: string;
  }>;
  theme_winner?: string;
  gaps?: string[];
  recommendation?: string;
};

export type DiscoveredReel = {
  url?: string;
  shortcode?: string;
  views?: number;
  likes?: number;
  comments?: number;
  engagement_rate?: number;
  caption_snippet?: string;
  /** Bei tracked-Reels aus dem Instagram-Tracker: Tracker-Zusammenfassung. */
  summary?: string;
  transcript_snippet?: string;
  topic_tag?: string;
  hook_type?: string;
  hook_score?: number;
  sentiment?: string;
  key_observation?: string;
  why_it_worked?: string;
};

export type DiscoveryCandidate = {
  handle: string;
  follower_count_estimate?: number;
  post_count_seen?: number;
  avg_views?: number;
  avg_engagement_rate?: number;
  theme_match?: number;
  recency_days?: number;
  /** Klassischer Score (ER × 0.4 + theme × 0.4 + recency × 0.2) */
  score?: number;
  /** Sonnet-Aehnlichkeitsscore 0-100 (verkauft aehnliches Produkt?) */
  similarity_score?: number;
  /** 1-Satz-Begruendung warum dieser Score */
  similarity_reason?: string;
  /** Finaler Rank-Score: 0.7 × similarity + 0.3 × score */
  final_score?: number;
  language?: 'de' | 'en' | 'unknown';
  /** @deprecated identisch zu similarity_reason, bleibt fuer Backwards-Compat */
  ai_reason?: string;
  sample_reel_url?: string;
  sample_caption_snippet?: string;
  /** Top-3 Reels nach ER, fuer "kannst du replizieren" */
  top_reels?: DiscoveredReel[];
};

export type Discovery = {
  available?: boolean;
  discovered_at?: string;
  themes_used?: string[];
  themes_source?: string;
  hashtags_searched?: string[];
  creators_discovered_total?: number;
  creators_after_filter?: number;
  candidates_dropped_irrelevant?: number;
  candidates?: DiscoveryCandidate[];
  stats?: { apify_calls: number; hashtag_searches: number; ai_calls: number; dropped_irrelevant?: number };
};

/**
 * Unified Markt-Eintrag: Mischung aus getrackten Konkurrenten und neu
 * entdeckten Creators. Quelle: generate_dashboard_data._build_market_creators.
 * Tracked = similarity_score 100 (per Definition relevant).
 * Discovered = similarity_score 40-100 (Sonnet-Bewertung, <40 gefiltert).
 */
export type MarketCreator = {
  handle: string;
  source: 'tracked' | 'discovered';
  similarity_score: number;
  similarity_reason: string;
  avg_views?: number;
  avg_engagement_rate?: number;
  reels_count?: number;
  language?: 'de' | 'en' | 'unknown';
  top_reels?: DiscoveredReel[];
  final_score?: number;
};

/**
 * Cross-cutting Top-Reels-Feed: beste Reels quer durch den ganzen Markt.
 * Quelle: generate_dashboard_data._build_market_top_reels.
 */
export type MarketTopReel = {
  handle: string;
  source: 'tracked' | 'discovered';
  similarity_score: number;
  url: string;
  shortcode: string;
  /** Posting-Datum als YYYY-MM-DD (oder ISO). Für Zeitfilter im Trend-Feed. */
  posted?: string;
  views: number;
  likes: number;
  comments: number;
  engagement_rate: number;
  caption_snippet: string;
  topic_tag?: string;
  hook_type?: string;
  hook_score?: number;
  summary?: string;
  why_it_worked?: string;
};

/**
 * Sonnet-generierte Markt-Uebersicht, gecacht 24h.
 * Quelle: scripts/market_analysis.py
 */
export type MarketAnalysis = {
  generated_at: string;
  creators_input: string[];
  summary: string;
  themes: string[];
  top_performers: string[];
  gaps: string[];
  _model?: string;
};

export type ContentIntel = {
  available: boolean;
  note?: string;
  snapshot_date?: string;
  self_handle?: string;
  mein_account?: CreatorStats;
  all_self_reels?: Reel[];
  range_kpis?: RangeKpis;
  competitors?: Record<string, CreatorStats>;
  competitor_handles?: string[];
  topic_clusters?: TopicCluster | null;
  discovery?: Discovery | null;
  /** Unified Liste: tracked + discovered, gefiltert + sortiert nach similarity_score. */
  market_creators?: MarketCreator[];
  /** Cross-cutting Feed: beste Reels quer durch den Markt, sortiert nach ER. */
  market_top_reels?: MarketTopReel[];
  market_analysis?: MarketAnalysis | null;
  top10_overall?: Reel[];
  totals?: { creators: number; reels_total: number; errors: number };
};

/**
 * To-Do-Block aus dashboard-data.json.
 * Quelle: scripts/generate_dashboard_data.py -> load_todos_from_daily_note().
 * Felder pro Eintrag: text, done, source (Section-Header der Daily Note,
 * dient als Kontext-Tag).
 */
export type TodoItem = {
  text: string;
  done: boolean;
  source?: string;        // Section-Heading aus Daily Note (Kontext)
  /** Wenn die Task aus einer älteren Daily Note stammt (Multi-Day-Carry-Over).
   *  Format: YYYY-MM-DD. Wenn leer/unset = aus heutiger Note. */
  carry_over_from?: string;
  // Folgende Felder sind nicht im Generator vorgesehen, aber optional, damit
  // wir später erweitern können, ohne die UI zu brechen.
  context?: string;
  priority?: 'high' | 'normal' | 'low';
};

export type TodosByPerson = Record<string, TodoItem[]>;

/**
 * Projekt-Eintrag aus dashboard-data.json.
 * Quelle: scripts/generate_dashboard_data.py -> load_projects().
 */
export type Project = {
  title: string;
  file: string;
  status: string;             // "aktiv" | "idee" | "paused" | "archiviert"
  status_notiz?: string;      // Freitext-Zusatz, z.B. "in-build", "Folgecall steht aus"
  priority?: string;          // "hoch" | "mittel" | "niedrig"
  deadline?: string;          // ISO-Date oder leer
  created?: string;
  category?: string;          // "Produkt" | "Content" | "Go-to-Market" | "Organisation" | "Sonstiges"
  goal?: string;
  next_steps?: string[];
  clients?: string[];
};

/**
 * News-Eintrag aus dashboard-data.json (Quelle: news[]).
 * Wird im Wissens-Hub als Top-News-Block angezeigt.
 */
export type NewsItem = {
  title: string;
  summary?: string;
  source?: string;
  source_url?: string;
  category?: string;
  date?: string;
};

/**
 * Wissensbibliothek-Tiles aus dashboard-data.json (knowledge_library.tiles[]).
 * Quelle: scripts/generate_dashboard_data.py -> build_knowledge_library().
 */
export type KnowledgeRecent = {
  name: string;
  filename: string;
  mtime_iso?: string;
};

export type KnowledgeTile = {
  key: string;
  title: string;
  icon?: string;
  count?: number;
  count_label?: string;
  sublabel?: string;
  recent?: KnowledgeRecent[];
};

export type KnowledgeLibrary = {
  generated_at?: string;
  tiles?: KnowledgeTile[];
  total_files?: number;
};

/**
 * Wissens-Hub V2 — News + Research pro Themenbereich.
 * Quelle: scripts/collect_knowledge.py → data/knowledge_hub.json.
 * Phase 1: news + research. Phase 2: creator_insights + videos.
 */
export type KnowledgeItem = {
  title: string;
  summary: string;
  source?: string;     // Domain ohne https
  url?: string;
  tags?: string[];
  // Nur bei top_news: aus welchem Topic
  topic_slug?: string;
  topic_label?: string;
};

export type KnowledgeCreatorInsight = {
  creator: string;
  video_id?: string;
  video_title?: string;
  video_url?: string;
  published_at?: string;
  insight: string;
};

export type KnowledgeVideo = {
  creator: string;
  title: string;
  url: string;
  thumbnail?: string;
  published_at?: string;
};

export type KnowledgeTopic = {
  slug: string;
  label: string;
  icon?: string;
  description?: string;
  research: KnowledgeItem[];
  news: KnowledgeItem[];
  trending_tags?: string[];
  creator_insights?: KnowledgeCreatorInsight[];   // Phase 2
  videos?: KnowledgeVideo[];                       // Phase 2
  last_update?: string;
};

export type KnowledgeHub = {
  generated_at?: string;
  rolling_window_days?: number;
  top_news: KnowledgeItem[];
  topics: KnowledgeTopic[];
};

// ── System-Health ─────────────────────────────────────────────────────────
// Quelle: scripts/system_health.py / generate_dashboard_data.py.
// `health` faltet `running | ok | warn | fail` zusammen, `running` heisst
// "Daemon läuft gerade", waehrend `ok` ein einmal sauber gelaufener
// Periodic-Job ist (pid=null, last_exit=0).

export type JobHealth = 'ok' | 'warn' | 'fail' | 'running' | 'unknown';

export type SystemJob = {
  label: string;
  name?: string;
  description?: string;
  pid?: number | null;
  last_exit?: number | null;
  health?: JobHealth;
  running?: boolean;
  // Optionale Felder für spätere Erweiterungen des Skripts:
  last_run?: string;
  next_run?: string;
  detail?: string;
};

export type SystemHealthSummary = {
  total?: number;
  running: number;
  ok: number;
  warn: number;
  fail: number;
};

export type SystemHealth = {
  generated_at?: string;
  overall?: 'ok' | 'warn' | 'fail' | 'unknown';
  summary?: SystemHealthSummary;
  jobs?: SystemJob[];
};

export type ApiKeyStatus = { set: boolean; preview?: string };
export type ApiStatus = Record<string, ApiKeyStatus>;

/**
 * Kalender-/Schedule-Eintrag für die Übersicht-Hauptseite.
 * Quelle: scripts/generate_dashboard_data.py -> load_schedule_from_calendar_db().
 */
export type ScheduleEvent = {
  title: string;
  start: string;
  end: string;
  type?: string;
  color?: string;
  detail?: string;
  attendees?: string[];
  source?: string;
  prep?: string | null;
  // Routing-Felder für Edit/Delete via Google Calendar API.
  // Bei alten Snapshots koennen diese fehlen.
  event_id?: string;
  account?: string;
  calendar_id?: string;
  calendar_name?: string;
  html_link?: string;
  location?: string;
  description?: string;
};

/**
 * Volle Event-Details, live aus Google Calendar via /calendar/event-Endpoint.
 * Im Gegensatz zu ScheduleEvent enthaelt das die echte Beschreibung, Conference-Daten,
 * recurring-Info etc. — wird nur beim Klick aufs Event geladen.
 */
/**
 * Lead-Prep aus data/call-preps/<slug>.json bzw. /calendar/prep-Endpoint.
 * Quelle: scripts/generate_lead_prep.py -> JSON-Schema im SYSTEM_PROMPT.
 * Alte Preps (vor 2026-05-11) haben evtl. nur ein Subset der Felder.
 */
export type LeadPrepBottleneck = {
  pain: string;
  hours_per_week?: number | null;
  cost_eur_per_month?: number | null;
};

export type LeadPrepSource = {
  url: string;
  label?: string;
  note?: string;
};

export type LeadPrepProfileCategory =
  | 'Senior-Solopreneur'
  | 'KMU-Geschäftsführer'
  | 'Aufbau-Solopreneur'
  | 'Premium-Spezialist'
  | 'Angestellter'
  | 'Multi-Brand-Inhaber'
  | 'Familien-KMU'
  | 'Tech-affin'
  | 'Black-Box'
  | 'Test-Booking';

export type LeadPrep = {
  contact?: string;
  // Methodik v2 (Stand 2026-05-11)
  who_is_it?: string;
  branchen_wort?: string;
  what_they_do?: string;
  profile_category?: LeadPrepProfileCategory;
  icp_fit?: {
    level?: 'niedrig' | 'mid' | 'hoch';
    reasoning?: string;
  };
  bottlenecks?: LeadPrepBottleneck[];
  seven_day_step?: string;
  caveats?: string[];
  tonality?: {
    address?: 'du' | 'sie';
    language?: string;
    avoid?: string[];
  };
  opener?: string;
  deal?: {
    price_range?: string;
    leverage?: string;
    risk?: string;
  };
  red_flags?: string[];
  sources?: LeadPrepSource[];
  status?: 'ok' | 'black_box' | 'test_booking' | 'red_flag';
  status_note?: string;

  // Legacy v1-Felder (für alte cache-Files wie max-goertler.json)
  role?: string;
  profession_explainer?: string;
  company_info?: string;
  data_status?: 'ok' | 'sparse' | 'empty';
  data_status_note?: string;
  icp_match?: {
    score?: 'stark' | 'mittel' | 'schwach' | 'unklar';
    reasoning?: string;
  } | null;
  offer_fit?: {
    recommended_tier?: string;
    reasoning?: string;
  } | null;
  found_online?: {
    linkedin?: string;
    company_website?: string;
    other_sources?: string[];
    phone_verified?: boolean | string;
    summary?: string;
  };
  pain_points_hypothesis?: string[];
  questions_to_ask?: string[];
  /** @deprecated weg seit 2026-05-11 */
  talking_points?: string[];
  next_call_agenda?: string[];
  /** @deprecated weg seit 2026-05-11 */
  missing_info?: string[];
  // Legacy-Felder aus alten Preps (Max Görtler etc.)
  summary?: string;
  pain_points?: string[];
  emotional_drivers?: string[];
  opportunities?: string[];
  open_questions?: string[];
  commitments_already_made?: string[];
  prep_todos?: string[];
  recommendations?: string[];
  _meta?: {
    generated_at?: string;
    lead_email?: string;
    lead_phone?: string;
    event_id?: string;
    slug?: string;
    web_queries?: string[];
    web_snippet_count?: number;
    data_quality?: string;
    candidate_alternatives?: string;
  };
  _cache?: { hit?: boolean; slug?: string };
  _trigger?: boolean;
  // 404-Form (kein Prep da)
  error?: string;
  slug?: string;
  trigger?: boolean;
  lead_preview?: { name?: string; email?: string; phone?: string };
};

export type CalendarEventDetail = {
  event_id: string;
  account: string;
  calendar_id: string;
  calendar_name?: string;
  title: string;
  date: string;
  start: string;
  end: string;
  start_iso?: string;
  end_iso?: string;
  all_day?: boolean;
  location?: string;
  description?: string;
  attendees?: { email?: string; name?: string; status?: string }[];
  organizer?: { email?: string; name?: string };
  html_link?: string;
  meet_link?: string;
  recurring?: boolean;
  writable?: boolean;
};

export type Weather = {
  temp?: string;
  feels_like?: string;
  condition?: string;
  icon?: string;
  humidity?: string;
  wind?: string;
  high?: string;
  low?: string;
};

/**
 * Manuell eingetragene LinkedIn-KPIs aus dem Skript-Frontmatter (`kpis:`-Block).
 * Quelle: scripts/generate_dashboard_data.py -> load_content_planning().
 * Felder sind nullable, weil sie initial leer sind und per CLI nachgetragen werden.
 */
export type ContentPieceKpis = {
  impressions: number | null;
  /** YouTube-Pendant zu impressions. */
  views: number | null;
  likes: number | null;
  comments: number | null;
  reposts: number | null;
  profile_visits: number | null;
  last_updated: string | null;
};

/**
 * Content-Planung aus dem Vault.
 * Quelle: scripts/generate_dashboard_data.py -> load_content_planning().
 */
export type ContentPiece = {
  id: string;
  platform: 'instagram' | 'linkedin' | 'youtube';
  kind: 'konzept' | 'bereit' | 'planned' | 'posted' | 'idea';
  title: string;
  slug: string;
  status: string;
  hook: string;
  trigger_word?: string;
  serie?: string;
  /** Content-Bucket-Slug, z.B. "personal-story", "build-in-public" (vor allem LinkedIn). */
  bucket?: string;
  reel_number?: string | number;
  hashtags: string[];
  caption: string;
  voice_status?: string;
  post_url?: string;
  shortcode?: string;
  posted_at?: string;
  created?: string;
  vault_path: string;
  folder?: string;
  body_preview?: string;
  /** Voller Post-Text (LinkedIn): extrahiert aus erstem Code-Block oder Blockquote im Skript. */
  post_text?: string;
  /** Relativer Vault-Pfad zur final.mp4 — leer wenn kein Video vorhanden. */
  final_mp4?: string;
  /** Relativer Vault-Pfad zu cover.{png,jpg,jpeg,webp} — z.B. für LinkedIn-Post-Vorschau. */
  cover_image?: string;
  /** Cross-Posting-Status: 'posted' = schon auf TikTok, 'open' = noch postbar. */
  crosspost_tiktok?: 'posted' | 'open';
  crosspost_youtube_shorts?: 'posted' | 'open';
  /** Manuelle KPIs (LinkedIn Phase 1). null wenn nichts eingetragen. */
  kpis?: ContentPieceKpis | null;
  /** YouTube-Video-ID (z.B. "5WrIl591cOE"). Leer wenn nicht gepostet. */
  video_id?: string;
  /** Volle YouTube-URL — wird auch als Fallback fuer post_url verwendet. */
  url?: string;
  /** Video-Dauer in Sekunden (YouTube). */
  duration_s?: number | null;
};

export type ContentPlanningPlatform = {
  /** in Konzeption / Skript / Filming */
  konzept: ContentPiece[];
  /** Final.mp4 fertig, wartet auf Upload */
  bereit: ContentPiece[];
  /** Backwards-compat: konzept + bereit */
  planned: ContentPiece[];
  posted: ContentPiece[];
};

export type ContentPlanning = {
  available: boolean;
  note?: string;
  instagram: ContentPlanningPlatform;
  linkedin: ContentPlanningPlatform;
  youtube: ContentPlanningPlatform;
  /** TikTok ist Cross-Post-View: zeigt Instagram-Reels mit final.mp4 + crosspost_tiktok-Status.
   * Hat KEIN eigenes Pipeline/Konzept (kein eigener Content), nur 'bereit' (postbar) + 'posted'. */
  tiktok: ContentPlanningPlatform;
  ideas: ContentPiece[];
  stats?: {
    ig_konzept?: number;
    ig_bereit?: number;
    ig_planned: number;
    ig_posted: number;
    li_konzept?: number;
    li_bereit?: number;
    li_planned: number;
    li_posted: number;
    yt_konzept?: number;
    yt_bereit?: number;
    yt_planned: number;
    yt_posted: number;
    tt_bereit?: number;
    tt_posted?: number;
    ideas: number;
  };
};

/**
 * YouTube-Channel-Snapshot + Top-Videos aus der lokalen SQLite-DB.
 * Quelle: scripts/generate_dashboard_data.py -> load_youtube_metrics() (data.content.youtube).
 * Befuellt von scripts/collect_youtube.py (taeglich via launchd com.aios.youtube-tracker).
 */
export type YouTubeVideoStat = {
  title: string;
  views: number;
  likes: number;
  comments: number;
  date: string;
};

export type YouTubeChannel = {
  total_subs: number;
  total_views: number;
  total_videos: number;
  recent_videos: YouTubeVideoStat[];
};

/**
 * TikTok-Video, normalisiert vom Apify-Scraper. Felder weitgehend parallel zum
 * Instagram-Reel, plus shares + saves die TikTok public ausliefert.
 */
export type TikTokVideo = {
  shortcode: string;
  url: string;
  posted: string;
  posted_at: string;
  posted_hour: number | null;
  posted_dayofweek: string;
  views: number;
  plays: number;
  likes: number;
  comments: number;
  shares: number;
  saves: number;
  video_duration?: number | null;
  hashtags: string[];
  caption_full: string;
  caption_snippet: string;
  handle: string;
  engagement_rate: number;
};

export type TikTokRangeKpi = {
  count: number;
  total_views: number;
  total_likes: number;
  total_comments: number;
  total_shares: number;
  total_saves: number;
  avg_views: number;
  avg_engagement_rate: number;
  avg_save_rate: number;
  avg_share_rate: number;
  views_delta_total?: number;
  reels_tracked?: number;
  window_start?: string;
};

export type TikTokIntel = {
  available: boolean;
  note?: string;
  platform?: 'tiktok';
  self_handle?: string;
  snapshot_date?: string;
  all_self_videos?: TikTokVideo[];
  range_kpis?: {
    today: TikTokRangeKpi;
    '7d': TikTokRangeKpi;
    '30d': TikTokRangeKpi;
    all: TikTokRangeKpi;
    history_first_snapshot?: string;
  };
  totals?: { videos_total: number };
};

/**
 * Plattform-Ziele. Pro Plattform genau ein Ziel-Tracker (z.B. Reels/Woche).
 * Quelle: 04-areas/content/scorecard.md Frontmatter (Targets), Ist-Werte
 * werden im Backend automatisch aus dem Vault gezählt.
 */
export type ScorecardGoal = {
  label: string;
  value: number;
  target: number;
  period: string;
};

export type MarketingScorecard = {
  available: boolean;
  last_updated: string;
  goals: {
    instagram: ScorecardGoal;
    tiktok: ScorecardGoal;
  };
};

export type DashboardData = {
  generated_at?: string;
  date?: string;
  weekday?: string;
  user?: string;
  weather?: Weather;
  schedule?: ScheduleEvent[];
  // 30-Tage-Window aus Google Calendar (alle verknuepften Accounts).
  // Key = ISO-Datum (YYYY-MM-DD), Value = Events für diesen Tag (auch leere []).
  // Quelle: scripts/generate_dashboard_data.py -> load_schedule_by_date().
  schedule_by_date?: Record<string, ScheduleEvent[]>;
  content_intel?: ContentIntel;
  content_planning?: ContentPlanning;
  tiktok_intel?: TikTokIntel;
  marketing_scorecard?: MarketingScorecard;
  content?: {
    youtube?: YouTubeChannel;
  };
  todos?: TodosByPerson;
  projects?: Project[];
  news?: NewsItem[];
  knowledge_library?: KnowledgeLibrary;
  knowledge_hub?: KnowledgeHub;
  system_health?: SystemHealth;
  api_status?: ApiStatus;
};
