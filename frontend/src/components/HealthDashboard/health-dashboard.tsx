import React, { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api-client';
import styles from './HealthDashboard.module.css';

interface HealthCheck {
  status: 'healthy' | 'unhealthy';
  message: string;
  timestamp: string;
}

interface HealthData {
  status: 'healthy' | 'unhealthy';
  timestamp: string;
  checks: {
    [key: string]: HealthCheck;
  };
  summary: {
    total: number;
    healthy: number;
    unhealthy: number;
  };
}

<<<<<<< HEAD
interface AnalyticsHealthData {
  activity_statistics: {
    total_distance: number;
    total_calories: number;
    average_duration: number;
    activity_count: number;
  };
  inactivity_evaluation: {
    days_since_last_activity: number | null;
    inactive: boolean;
    severity: 'none' | 'mild' | 'severe';
  };
}

=======
>>>>>>> dd5a3f7e (Renamed health dashboard file to match naming convention)
interface CheckItemProps {
  name: string;
  check: HealthCheck;
}

const CheckItem: React.FC<CheckItemProps> = ({ name, check }) => {
  const isHealthy = check.status === 'healthy';
  return (
    <div className={`${styles.checkItem} ${isHealthy ? styles.healthy : styles.unhealthy}`}>
      <div className={styles.checkHeader}>
        <span className={styles.checkName}>{name}</span>
        <span className={`${styles.statusBadge} ${isHealthy ? styles.statusHealthy : styles.statusUnhealthy}`}>
          {check.status}
        </span>
      </div>
      <p className={styles.checkMessage}>{check.message}</p>
      <p className={styles.checkTime}>{new Date(check.timestamp).toLocaleTimeString()}</p>
    </div>
  );
};

export const HealthDashboard: React.FC = () => {
  const [health, setHealth] = useState<HealthData | null>(null);
<<<<<<< HEAD
  const [analytics, setAnalytics] = useState<AnalyticsHealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyticsLoading, setAnalyticsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analyticsError, setAnalyticsError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  const [analyticsLastRefresh, setAnalyticsLastRefresh] = useState<Date>(new Date());

  const fetchSystemHealth = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = (await apiClient.get('/api/v1/health/')) as unknown as HealthData;
=======
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const fetchHealth = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch('/api/v1/health/');
      
      if (!response.ok && response.status !== 503) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
>>>>>>> dd5a3f7e (Renamed health dashboard file to match naming convention)
      setHealth(data);
      setLastRefresh(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch health status');
      setHealth(null);
    } finally {
      setLoading(false);
    }
  };

<<<<<<< HEAD
  const fetchAnalyticsHealth = async () => {
    try {
      setAnalyticsLoading(true);
      setAnalyticsError(null);
      const data = (await apiClient.get('/api/v1/analytics/health-indicators/')) as unknown as AnalyticsHealthData;
      setAnalytics(data);
      setAnalyticsLastRefresh(new Date());
    } catch (err) {
      setAnalyticsError(err instanceof Error ? err.message : 'Failed to fetch analytics health indicators');
      setAnalytics(null);
    } finally {
      setAnalyticsLoading(false);
    }
  };

  useEffect(() => {
    fetchSystemHealth();
    fetchAnalyticsHealth();
    const interval = setInterval(() => {
      fetchSystemHealth();
      fetchAnalyticsHealth();
    }, 10000); // Refresh every 10 seconds
=======
  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 10000); // Refresh every 10 seconds
>>>>>>> dd5a3f7e (Renamed health dashboard file to match naming convention)
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
<<<<<<< HEAD
    fetchSystemHealth();
    fetchAnalyticsHealth();
  };

  const formatNumber = (value: number) =>
    Number.isInteger(value) ? value.toString() : value.toFixed(1);

  const formatMaybeNumber = (value: number | null) =>
    value === null ? 'No activity yet' : value.toString();

  const renderAnalyticsStatus = () => {
    if (analyticsError) {
      return (
        <div className={styles.errorBox}>
          <p>Error loading analytics health indicators: {analyticsError}</p>
          <p>You may need to sign in before viewing this section.</p>
        </div>
      );
    }

    if (analyticsLoading && !analytics) {
      return (
        <div className={styles.loadingBox}>
          <p>Loading analytics health indicators...</p>
        </div>
      );
    }

    if (!analytics) {
      return null;
    }

    return (
      <div className={styles.analyticsCardGrid}>
        <div className={styles.metricCard}>
          <span className={styles.metricLabel}>Total Distance</span>
          <span className={styles.metricValue}>{formatNumber(analytics.activity_statistics.total_distance)}</span>
        </div>
        <div className={styles.metricCard}>
          <span className={styles.metricLabel}>Total Calories</span>
          <span className={styles.metricValue}>{formatNumber(analytics.activity_statistics.total_calories)}</span>
        </div>
        <div className={styles.metricCard}>
          <span className={styles.metricLabel}>Average Duration</span>
          <span className={styles.metricValue}>{formatNumber(analytics.activity_statistics.average_duration)} min</span>
        </div>
        <div className={styles.metricCard}>
          <span className={styles.metricLabel}>Activity Count</span>
          <span className={styles.metricValue}>{analytics.activity_statistics.activity_count}</span>
        </div>
        <div className={styles.metricCard}>
          <span className={styles.metricLabel}>Days Since Last Activity</span>
          <span className={styles.metricValue}>{formatMaybeNumber(analytics.inactivity_evaluation.days_since_last_activity)}</span>
        </div>
        <div className={styles.metricCard}>
          <span className={styles.metricLabel}>Inactivity Severity</span>
          <span className={`${styles.metricValue} ${analytics.inactivity_evaluation.inactive ? styles.metricDanger : styles.metricSuccess}`}>
            {analytics.inactivity_evaluation.inactive ? 'Inactive' : 'Active'} ({analytics.inactivity_evaluation.severity})
          </span>
        </div>
      </div>
    );
=======
    fetchHealth();
>>>>>>> dd5a3f7e (Renamed health dashboard file to match naming convention)
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>System Health Dashboard</h1>
        <button 
          onClick={handleRefresh} 
          disabled={loading}
          className={styles.refreshButton}
        >
          {loading ? 'Refreshing...' : 'Refresh Now'}
        </button>
      </div>

      {error && (
        <div className={styles.errorBox}>
          <p>Error: {error}</p>
          <p>Unable to connect to health endpoint. The backend may be unavailable.</p>
        </div>
      )}

      {health && (
        <div className={styles.content}>
          {/* Status Summary */}
          <div className={`${styles.statusBox} ${health.status === 'healthy' ? styles.statusHealthy : styles.statusUnhealthy}`}>
            <div className={styles.statusSummary}>
              <h2>Overall Status: {health.status.toUpperCase()}</h2>
              <div className={styles.summary}>
                <div className={styles.summaryItem}>
                  <span className={styles.summaryLabel}>Total Checks:</span>
                  <span className={styles.summaryValue}>{health.summary.total}</span>
                </div>
                <div className={styles.summaryItem}>
                  <span className={styles.summaryLabel}>Healthy:</span>
                  <span className={styles.summaryValueHealthy}>{health.summary.healthy}</span>
                </div>
                <div className={styles.summaryItem}>
                  <span className={styles.summaryLabel}>Unhealthy:</span>
                  <span className={styles.summaryValueUnhealthy}>{health.summary.unhealthy}</span>
                </div>
              </div>
              <p className={styles.timestamp}>
                Last updated: {lastRefresh.toLocaleTimeString()} {lastRefresh.toLocaleDateString()}
              </p>
            </div>
          </div>

          {/* Individual Checks */}
          <div className={styles.checksContainer}>
            <h3>Component Status</h3>
            <div className={styles.checksGrid}>
              {Object.entries(health.checks).map(([name, check]) => (
                <CheckItem 
                  key={name} 
                  name={name.replace(/_/g, ' ').toUpperCase()} 
                  check={check} 
                />
              ))}
            </div>
          </div>
<<<<<<< HEAD

          <div className={styles.checksContainer}>
            <h3>Analytics Health Indicators</h3>
            <p className={styles.timestamp}>
              Last updated: {analyticsLastRefresh.toLocaleTimeString()} {analyticsLastRefresh.toLocaleDateString()}
            </p>
            {renderAnalyticsStatus()}
          </div>
=======
>>>>>>> dd5a3f7e (Renamed health dashboard file to match naming convention)
        </div>
      )}

      {loading && !health && (
        <div className={styles.loadingBox}>
          <p>Loading health status...</p>
        </div>
      )}
    </div>
  );
};
