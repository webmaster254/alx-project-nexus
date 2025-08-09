import React from 'react';
import { useOnlineStatus } from '../../hooks/useOnlineStatus';
import { useResponsive } from '../../hooks';

interface OfflineIndicatorProps {
  className?: string;
  showOnlineStatus?: boolean;
}

export const OfflineIndicator: React.FC<OfflineIndicatorProps> = ({
  className = '',
  showOnlineStatus = false,
}) => {
  const isOnline = useOnlineStatus();
  const { isMobile } = useResponsive();

  if (isOnline && !showOnlineStatus) {
    return null;
  }

  return (
    <div
      className={`
        fixed z-50 rounded-lg shadow-lg transition-all duration-300 touch-manipulation
        ${isMobile 
          ? 'top-20 left-4 right-4 px-3 py-2' 
          : 'top-4 right-4 px-4 py-2'
        }
        ${isOnline 
          ? 'bg-green-100 text-green-800 border border-green-200' 
          : 'bg-red-100 text-red-800 border border-red-200'
        }
        ${className}
      `}
      role="alert"
      aria-live="polite"
    >
      <div className="flex items-center space-x-2">
        {isOnline ? (
          <svg className="h-4 w-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
          </svg>
        ) : (
          <svg className="h-4 w-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636l-12.728 12.728m0 0L1.394 9.393s5.857-5.857 21.213 0M5.636 18.364l12.728-12.728m0 0c5.857 5.857 5.857 15.355 0 21.213" />
          </svg>
        )}
        <span className={`font-medium ${isMobile ? 'text-sm' : 'text-sm'}`}>
          {isOnline ? 'Back online' : 'You\'re offline'}
        </span>
      </div>
    </div>
  );
};

// Banner version for persistent offline state
export const OfflineBanner: React.FC = () => {
  const isOnline = useOnlineStatus();

  if (isOnline) {
    return null;
  }

  return (
    <div
      className="bg-red-600 text-white px-4 py-2 text-center text-sm"
      role="alert"
      aria-live="polite"
    >
      <div className="flex items-center justify-center space-x-2">
        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636l-12.728 12.728m0 0L1.394 9.393s5.857-5.857 21.213 0M5.636 18.364l12.728-12.728m0 0c5.857 5.857 5.857 15.355 0 21.213" />
        </svg>
        <span>
          You're currently offline. Some features may not be available.
        </span>
      </div>
    </div>
  );
};