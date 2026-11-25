import { api } from './client';

export type HealthMetric =
  | 'blood_pressure'
  | 'blood_glucose'
  | 'temperature'
  | 'weight'
  | 'heart_rate';

export interface HealthReading {
  id: number;
  parent_id: number;
  parent_name?: string | null;
  metric: HealthMetric;
  value: number;
  secondary_value?: number | null;
  unit: string;
  recorded_at: string;
  notes?: string | null;
  created_at: string;
}

export interface HealthReadingInput {
  parent_id: number;
  metric: HealthMetric;
  value: number;
  secondary_value?: number;
  unit: string;
  recorded_at: string;
  notes?: string;
}

export const healthApi = {
  getReadings: (parentId?: number, metric?: HealthMetric): Promise<HealthReading[]> => {
    const params = new URLSearchParams();
    if (parentId) params.set('parent_id', String(parentId));
    if (metric) params.set('metric', metric);
    const query = params.toString() ? `?${params.toString()}` : '';
    return api.get<HealthReading[]>(`/health-readings${query}`);
  },

  createReading: (data: HealthReadingInput): Promise<HealthReading> =>
    api.post<HealthReading>('/health-readings', data),

  deleteReading: (id: number): Promise<void> =>
    api.delete<void>(`/health-readings/${id}`),
};
