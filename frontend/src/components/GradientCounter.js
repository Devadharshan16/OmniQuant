import React, { useEffect, useRef, useState } from 'react';

/**
 * Animated counter with gradient text — inspired by React Bits <Counter /> + <GradientText />.
 *
 * Props:
 *   value      – target number
 *   decimals   – decimal places (default 0)
 *   duration   – animation ms (default 1200)
 *   suffix     – text appended after the number (e.g. "ms", "%")
 *   gradient   – CSS gradient string (default: purple→violet like the React Bits example)
 *   className  – extra classes on the wrapper
 */
function GradientCounter({
  value = 0,
  decimals = 0,
  duration = 1200,
  suffix = '',
  gradient = 'linear-gradient(135deg, #c084fc 0%, #a78bfa 40%, #818cf8 100%)',
  className = '',
}) {
  const [display, setDisplay] = useState(0);
  const prevValue = useRef(0);
  const rafId = useRef(null);

  useEffect(() => {
    const start = prevValue.current;
    const end = typeof value === 'number' ? value : parseFloat(value) || 0;
    const startTime = performance.now();

    const animate = (now) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = start + (end - start) * eased;
      setDisplay(current);

      if (progress < 1) {
        rafId.current = requestAnimationFrame(animate);
      } else {
        prevValue.current = end;
      }
    };

    rafId.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(rafId.current);
  }, [value, duration]);

  const formatted = decimals > 0 ? display.toFixed(decimals) : Math.round(display);

  return (
    <span
      className={`gradient-counter ${className}`}
      style={{
        background: gradient,
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        backgroundClip: 'text',
      }}
    >
      {formatted}{suffix}
    </span>
  );
}

export default GradientCounter;
