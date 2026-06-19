import { useEffect, useRef, useCallback } from 'react';

export function usePolling(callback, interval = 5000, isActive = true) {
  const timeoutRef = useRef(null);
  const callbackRef = useRef(callback);

  // Keep callback ref updated
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  const poll = useCallback(() => {
    if (!isActive) return;

    callbackRef.current();

    if (isActive) {
      timeoutRef.current = setTimeout(poll, interval);
    }
  }, [interval, isActive]);

  useEffect(() => {
    if (!isActive) return;

    // Start polling
    poll();

    // Cleanup
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [poll, isActive]);

  return { timeoutRef };
}
