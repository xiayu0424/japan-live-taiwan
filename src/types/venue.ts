export interface Venue {
  id: string;
  name: string;
  city: string;
  district?: string;
  address?: string;
  capacity?: number;
  official_url?: string;
  google_maps_url?: string;
}
