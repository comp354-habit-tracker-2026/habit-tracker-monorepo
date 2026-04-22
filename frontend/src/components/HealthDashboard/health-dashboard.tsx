import React, { useState, useEffect } from 'react';
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
      setHealth(data);
      setLastRefresh(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch health status');
      setHealth(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    fetchHealth();
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
