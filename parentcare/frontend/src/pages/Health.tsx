import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Activity, Plus, Trash2, AlertCircle, HeartPulse } from 'lucide-react';
import { healthApi, type HealthMetric, type HealthReading } from '../api/health';
import { parentsApi } from '../api/parents';
import type { Parent } from '../types';
import { LoadingSpinner } from '../components/LoadingSpinner';

const metricLabels: Record<HealthMetric, string> = {
  blood_pressure: 'Blood pressure',
  blood_glucose: 'Blood glucose',
  temperature: 'Body temperature',
  weight: 'Weight',
  heart_rate: 'Heart rate',
};

const units: Record<Exclude<HealthMetric, 'blood_pressure'>, string[]> = {
  blood_glucose: ['mg/dL', 'mmol/L'],
  temperature: ['°C', '°F'],
  weight: ['kg', 'lb'],
  heart_rate: ['bpm'],
};

const localDateTime = () => {
  const date = new Date();
  date.setMinutes(date.getMinutes() - date.getTimezoneOffset());
  return date.toISOString().slice(0, 16);
};

export const Health: React.FC = () => {
  const [parents, setParents] = useState<Parent[]>([]);
  const [readings, setReadings] = useState<HealthReading[]>([]);
  const [parentFilter, setParentFilter] = useState('');
  const [metricFilter, setMetricFilter] = useState<HealthMetric | ''>('');
  const [metric, setMetric] = useState<HealthMetric>('blood_pressure');
  const [parentId, setParentId] = useState('');
  const [value, setValue] = useState('');
  const [secondaryValue, setSecondaryValue] = useState('');
  const [unit, setUnit] = useState('mmHg');
  const [recordedAt, setRecordedAt] = useState(localDateTime);
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [parentItems, readingItems] = await Promise.all([
        parentsApi.getAll(),
        healthApi.getReadings(parentFilter ? Number(parentFilter) : undefined, metricFilter || undefined),
      ]);
      setParents(parentItems);
      setReadings(readingItems);
      if (!parentId && parentItems.length) setParentId(String(parentItems[0].id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load health readings.');
    } finally {
      setLoading(false);
    }
  }, [metricFilter, parentFilter, parentId]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  useEffect(() => {
    if (metric === 'blood_pressure') {
      setUnit('mmHg');
      setSecondaryValue('');
    } else {
      setUnit(units[metric][0]);
    }
  }, [metric]);

  const chartReadings = useMemo(
    () => [...readings].filter((reading) => reading.metric === metricFilter || !metricFilter).slice(0, 20).reverse(),
    [readings, metricFilter],
  );
  const chartValues = chartReadings.map((reading) => reading.value);
  const chartPoints = chartValues.length > 1
    ? chartValues.map((reading, index) => {
        const min = Math.min(...chartValues);
        const max = Math.max(...chartValues);
        const y = 150 - ((reading - min) / (max - min || 1)) * 120;
        const x = 20 + (index / (chartValues.length - 1)) * 460;
        return `${x},${y}`;
      }).join(' ')
    : '';

  const submitReading = async (event: React.FormEvent) => {
    event.preventDefault();
    setFormError(null);
    const numericValue = Number(value);
    const numericSecondary = Number(secondaryValue);
    if (!parentId || !Number.isFinite(numericValue) || numericValue <= 0) {
      setFormError('Choose a parent and enter a reading greater than zero.');
      return;
    }
    if (metric === 'blood_pressure' && (!secondaryValue || !Number.isFinite(numericSecondary) || numericSecondary <= 0)) {
      setFormError('Enter both systolic and diastolic values for blood pressure.');
      return;
    }

    setSaving(true);
    try {
      await healthApi.createReading({
        parent_id: Number(parentId),
        metric,
        value: numericValue,
        ...(metric === 'blood_pressure' ? { secondary_value: numericSecondary } : {}),
        unit,
        recorded_at: new Date(recordedAt).toISOString(),
        notes: notes.trim() || undefined,
      });
      setValue('');
      setSecondaryValue('');
      setNotes('');
      setRecordedAt(localDateTime());
      await loadData();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Could not save this reading.');
    } finally {
      setSaving(false);
    }
  };

  const deleteReading = async (reading: HealthReading) => {
    if (!window.confirm('Delete this health reading?')) return;
    try {
      await healthApi.deleteReading(reading.id);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not delete this reading.');
    }
  };

  if (loading) return <LoadingSpinner message="Loading health readings..." />;

  return (
    <div className="page-container">
      <div className="page-header-row">
        <div>
          <h2>Health Monitoring</h2>
          <p className="page-subtitle">Record and review readings entered by you or your family.</p>
        </div>
        <Activity size={26} aria-hidden="true" />
      </div>

      <div className="health-safety-note" role="note">
        <HeartPulse size={20} aria-hidden="true" />
        <p>These are user-entered records, not diagnoses or verified medical measurements. Reference ranges vary by person; ask a healthcare professional how to interpret readings. For urgent concerns, contact a clinician or local emergency service.</p>
      </div>

      {error && (
        <div className="error-card" role="alert">
          <AlertCircle size={24} />
          <p>{error}</p>
          <button className="btn-primary" onClick={() => void loadData()}>Retry</button>
        </div>
      )}

      <section className="health-panel" aria-labelledby="add-reading-title">
        <h3 id="add-reading-title"><Plus size={18} /> Add a reading</h3>
        {parents.length === 0 ? (
          <p>Add a parent profile before recording readings.</p>
        ) : (
          <form className="health-reading-form" onSubmit={submitReading}>
            <label>
              Parent
              <select value={parentId} onChange={(event) => setParentId(event.target.value)} required>
                {parents.map((parent) => <option key={parent.id} value={parent.id}>{parent.name}</option>)}
              </select>
            </label>
            <label>
              Reading type
              <select value={metric} onChange={(event) => setMetric(event.target.value as HealthMetric)}>
                {Object.entries(metricLabels).map(([key, label]) => <option key={key} value={key}>{label}</option>)}
              </select>
            </label>
            <label>
              {metric === 'blood_pressure' ? 'Systolic' : 'Value'}
              <input type="number" min="0.01" step="any" value={value} onChange={(event) => setValue(event.target.value)} required />
            </label>
            {metric === 'blood_pressure' ? (
              <label>
                Diastolic
                <input type="number" min="0.01" step="any" value={secondaryValue} onChange={(event) => setSecondaryValue(event.target.value)} required />
              </label>
            ) : (
              <label>
                Unit
                <select value={unit} onChange={(event) => setUnit(event.target.value)}>
                  {units[metric].map((option) => <option key={option} value={option}>{option}</option>)}
                </select>
              </label>
            )}
            <label>
              Date and time
              <input type="datetime-local" value={recordedAt} onChange={(event) => setRecordedAt(event.target.value)} required />
            </label>
            <label className="health-notes-field">
              Notes (optional)
              <input maxLength={2000} value={notes} onChange={(event) => setNotes(event.target.value)} placeholder="Context or clinician-provided reference" />
            </label>
            {formError && <p className="health-form-error" role="alert">{formError}</p>}
            <button type="submit" className="btn-primary" disabled={saving}>
              <Plus size={16} /> {saving ? 'Saving…' : 'Save reading'}
            </button>
          </form>
        )}
      </section>

      <section className="health-panel" aria-labelledby="history-title">
        <div className="health-history-header">
          <h3 id="history-title">Reading history</h3>
          <div className="health-filters">
            <label>
              <span className="sr-only">Filter by parent</span>
              <select value={parentFilter} onChange={(event) => setParentFilter(event.target.value)}>
                <option value="">All parents</option>
                {parents.map((parent) => <option key={parent.id} value={parent.id}>{parent.name}</option>)}
              </select>
            </label>
            <label>
              <span className="sr-only">Filter by reading type</span>
              <select value={metricFilter} onChange={(event) => setMetricFilter(event.target.value as HealthMetric | '')}>
                <option value="">All reading types</option>
                {Object.entries(metricLabels).map(([key, label]) => <option key={key} value={key}>{label}</option>)}
              </select>
            </label>
          </div>
        </div>

        {metricFilter && chartReadings.length > 1 && (
          <div className="health-chart-wrap">
            <p>{metricLabels[metricFilter]} trend (latest {chartReadings.length} records; not a diagnosis)</p>
            <svg viewBox="0 0 500 180" role="img" aria-label={`${metricLabels[metricFilter]} historical trend`}>
              <line x1="20" y1="150" x2="480" y2="150" />
              <polyline points={chartPoints} />
              {chartReadings.map((reading, index) => {
                const min = Math.min(...chartValues);
                const max = Math.max(...chartValues);
                const y = 150 - ((reading.value - min) / (max - min || 1)) * 120;
                const x = 20 + (index / (chartReadings.length - 1)) * 460;
                return <circle key={reading.id} cx={x} cy={y} r="4"><title>{reading.value} {reading.unit}</title></circle>;
              })}
            </svg>
          </div>
        )}

        {readings.length === 0 ? (
          <div className="empty-state-box"><Activity size={28} /><p>No readings recorded yet.</p></div>
        ) : (
          <ul className="health-reading-list">
            {readings.map((reading) => (
              <li key={reading.id} className="health-reading-row">
                <div>
                  <strong>{metricLabels[reading.metric]}</strong>
                  <span>{reading.parent_name} · {new Date(reading.recorded_at).toLocaleString()}</span>
                  {reading.notes && <p>{reading.notes}</p>}
                </div>
                <strong className="health-reading-value">
                  {reading.value}{reading.secondary_value !== null && reading.secondary_value !== undefined ? ` / ${reading.secondary_value}` : ''} {reading.unit}
                </strong>
                <button type="button" className="btn-icon-danger" onClick={() => void deleteReading(reading)} aria-label={`Delete ${metricLabels[reading.metric]} reading`}>
                  <Trash2 size={17} />
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
};
