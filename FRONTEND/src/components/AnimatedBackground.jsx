import React, { useEffect, useRef } from 'react';

const AnimatedBackground = () => {
  const containerRef = useRef(null);

  useEffect(() => {
    const container = containerRef.current;
    container.innerHTML = ""; // Clear dots

    const dotCount = 40;
    
    // Create dots with pure CSS/JS
    for (let i = 0; i < dotCount; i++) {
      const dot = document.createElement('div');
      dot.classList.add('dot');
      
      // Random start positions
      const startX = Math.random() * 100;
      const startY = Math.random() * 100;
      
      // Random movement durations
      const duration = 10 + Math.random() * 20; // 10s to 30s
      
      dot.style.left = `${startX}%`;
      dot.style.top = `${startY}%`;
      dot.style.animationDuration = `${duration}s`;
      dot.style.animationDelay = `-${Math.random() * 10}s`; // Start at random times
      
      container.appendChild(dot);
    }
  }, []);

  return (
    <div ref={containerRef} className="fixed inset-0 -z-10 bg-gray-900 overflow-hidden">
      {/* Internal Styles for the Animation */}
      <style>{`
        .dot {
          position: absolute;
          width: 6px;
          height: 6px;
          background: rgba(99, 102, 241, 0.3); /* Blue/Purple tint */
          border-radius: 50%;
          pointer-events: none;
          box-shadow: 0 0 15px rgba(99, 102, 241, 0.5);
          animation: float linear infinite;
        }

        @keyframes float {
          0% {
            transform: translate(0, 0) scale(1);
            opacity: 0;
          }
          25% {
            opacity: 0.8;
          }
          50% {
            transform: translate(100px, 100px) scale(1.5);
            opacity: 0.4;
          }
          75% {
            opacity: 0.8;
          }
          100% {
            transform: translate(-50px, 200px) scale(1);
            opacity: 0;
          }
        }
      `}</style>
    </div>
  );
};

export default AnimatedBackground;