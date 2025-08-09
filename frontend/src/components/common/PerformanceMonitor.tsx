import React, { useEffect, useState } from 'react';
import { config } from '../../config/environment';
import { usePerformanceMetrics, PerformanceMetrics } from '../../services/performanceService';

interface PerformanceMonitorProps {
  showDebugInfo?: boolean;
}

const PerformanceMonitor: React.FC<PerformanceMonitorProps> = ({ 
  showDebugInfo = config.enableDebugMode 
}) => {
  const { getMetrics, getAverageMetric } = usePerformanceMetrics();
  const [metrics, setMetrics] = useState<PerformanceMetrics[]>([]);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (!config.enablePerformanceMonitoring || !showDebugInfo) return;

    const updateMetrics = () => {
      setMetrics(getMetrics());
    };

    // Update metrics every 5 seconds
    const interval = setInterval(updateMetrics, 5000);
    updateMetrics(); // Initial update

    return () => clearInterval(interval);
  }, [getMetrics, showDebugInfo]);

  // Don't render in production unless explicitly enabled
  if (!showDebugInfo || config.environment === 'production') {
    return null;
  }

  const coreWebVitals = ['LCP', 'FID', 'CLS'];
  const otherMetrics = ['FCP', 'TTFB', 'DCL', 'Load'];

  const getRatingColor = (rating: string) => {
    switch (rating) {
      case 'good': return 'text-green-600';
      case 'needs-improvement': return 'text-yellow-600';
      case 'poor': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const formatValue = (name: string, value: number) => {
    if (name === 'CLS') {
      return value.toFixed(3);
    }
    return `${Math.round(value)}ms`;
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <button
        onClick={() => setIsVisible(!isVisible)}
        className="bg-blue-600 text-white px-3 py-2 rounded-lg shadow-lg hover:bg-blue-700 transition-colors"
        title="Performance Monitor"
      >
        📊 Perf
      </button>

      {isVisible && (
        <div className="absolute bottom-12 right-0 bg-white border border-gray-300 rounded-lg shadow-xl p-4 w-80 max-h-96 overflow-y-auto">
          <div className="flex justify-between items-center mb-3">
            <h3 className="font-semibold text-gray-800">Performance Metrics</h3>
            <button
              onClick={() => setIsVisible(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>

          {/* Core Web Vitals */}
          <div className="mb-4">
            <h4 className="font-medium text-sm text-gray-700 mb-2">Core Web Vitals</h4>
            <div className="space-y-2">
              {coreWebVitals.map(metric => {
                const avgValue = getAverageMetric(metric);
                const latestMetric = metrics
                  .filter(m => m.name === metric)
                  .sort((a, b) => b.timestamp - a.timestamp)[0];

                if (!latestMetric && avgValue === null) return null;

                const value = latestMetric?.value ?? avgValue ?? 0;
                const rating = latestMetric?.rating ?? 'good';

                return (
                  <div key={metric} className="flex justify-between items-center">
                    <span className="text-sm font-medium">{metric}</span>
                    <span className={`text-sm ${getRatingColor(rating)}`}>
                      {formatValue(metric, value)}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Other Metrics */}
          <div className="mb-4">
            <h4 className="font-medium text-sm text-gray-700 mb-2">Other Metrics</h4>
            <div className="space-y-2">
              {otherMetrics.map(metric => {
                const avgValue = getAverageMetric(metric);
                if (avgValue === null) return null;

                return (
                  <div key={metric} className="flex justify-between items-center">
                    <span className="text-sm font-medium">{metric}</span>
                    <span className="text-sm text-gray-600">
                      {formatValue(metric, avgValue)}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Performance Tips */}
          <div className="border-t pt-3">
            <h4 className="font-medium text-sm text-gray-700 mb-2">Tips</h4>
            <div className="text-xs text-gray-600 space-y-1">
              <div>• LCP &lt; 2.5s (Good)</div>
              <div>• FID &lt; 100ms (Good)</div>
              <div>• CLS &lt; 0.1 (Good)</div>
            </div>
          </div>

          {/* Environment Info */}
          <div className="border-t pt-3 mt-3">
            <div className="text-xs text-gray-500">
              Environment: {config.environment}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PerformanceMonitor;