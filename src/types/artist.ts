export type ArtistType =
  | "band"
  | "idol_group"
  | "singer"
  | "voice_actor"
  | "anisong"
  | "jpop"
  | "jrock"
  | "vocaloid"
  | "other";

export interface Artist {
  id: string;
  name: string;
  name_ja?: string;
  name_en?: string;
  name_zh?: string;
  aliases?: string[];
  country: string;
  artist_type: ArtistType;
  official_url?: string;
  social_links?: Record<string, string>;
}
