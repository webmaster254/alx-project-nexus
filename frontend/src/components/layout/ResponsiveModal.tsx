import React, { useEffect } from 'react';
import { useResponsive, useSwipeGesture } from '../../hooks';

interface ResponsiveModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  title?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  showCloseButton?: boolean;
  closeOnBackdrop?: boolean;
  className?: string;
}

const ResponsiveModal: React.FC<ResponsiveModalProps> = ({
  isOpen,
  onClose,
  children,
  title,
  size = 'md',
  showCloseButton = true,
  closeOnBackdrop = true,
  className = ''
}) => {
  const { isMobile, isTablet } = useResponsive();

  // Swipe gesture for mobile modal dismissal
  const { attachSwipeListeners } = useSwipeGesture({
    onSwipeDown: () => {
      if (isMobile) {
        onClose();
      }
    },
    threshold: 100,
  });

  // Handle escape key and body scroll
  useEffect(() => {
    if (!isOpen) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    document.body.style.overflow = 'hidden';

    // Attach swipe listeners for mobile
    if (isMobile) {
      const modalContent = document.getElementById('modal-content');
      if (modalContent) {
        const cleanup = attachSwipeListeners(modalContent);
        return () => {
          document.removeEventListener('keydown', handleEscape);
          document.body.style.overflow = 'unset';
          cleanup?.();
        };
      }
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose, isMobile, attachSwipeListeners]);

  const getSizeClasses = () => {
    if (isMobile) {
      return 'w-full h-full max-w-none max-h-none rounded-none';
    }

    const sizeMap = {
      'sm': 'max-w-sm',
      'md': 'max-w-md',
      'lg': 'max-w-lg',
      'xl': 'max-w-xl',
      'full': 'max-w-full max-h-full'
    };

    return `${sizeMap[size]} max-h-[90vh] rounded-lg`;
  };

  const getPositionClasses = () => {
    if (isMobile) {
      return 'fixed inset-0 flex flex-col';
    }
    return 'fixed inset-0 flex items-center justify-center p-4';
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={closeOnBackdrop ? onClose : undefined}
        aria-hidden="true"
      />

      {/* Modal */}
      <div className={getPositionClasses()}>
        <div
          id="modal-content"
          className={`relative bg-white shadow-xl ${getSizeClasses()} ${className} ${
            isMobile ? 'animate-slide-up-mobile' : 'animate-fade-in'
          }`}
          role="dialog"
          aria-modal="true"
          aria-labelledby={title ? 'modal-title' : undefined}
        >
          {/* Mobile swipe indicator */}
          {isMobile && (
            <div className="flex justify-center pt-2 pb-1">
              <div className="w-12 h-1 bg-gray-300 rounded-full" aria-hidden="true" />
            </div>
          )}

          {/* Header */}
          {(title || showCloseButton) && (
            <div className="flex items-center justify-between p-4 sm:p-6 border-b border-gray-200">
              {title && (
                <h2 id="modal-title" className="text-lg sm:text-xl font-semibold text-gray-900">
                  {title}
                </h2>
              )}
              {showCloseButton && (
                <button
                  onClick={onClose}
                  className="p-2 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md touch-manipulation"
                  aria-label="Close modal"
                  style={{ minHeight: '44px', minWidth: '44px' }}
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>
          )}

          {/* Content */}
          <div className={`${isMobile ? 'flex-1 overflow-y-auto' : ''} p-4 sm:p-6`}>
            {children}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResponsiveModal;