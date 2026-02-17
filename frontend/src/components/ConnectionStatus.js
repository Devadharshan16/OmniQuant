import React, { useState, useEffect } from 'react';
import { API_ENDPOINTS } from '../config';

function ConnectionStatus() {
  const [status, setStatus] = useState('checking');
  const [apiUrl, setApiUrl] = useState('');

  useEffect(() => {
    checkConnection();
    setApiUrl(API_ENDPOINTS.ROOT);
    
    // Check every 30 seconds
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  const checkConnection = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.HEALTH, {
        method: 'GET',
        headers: { 'Accept': 'application/json' }
      });
      
      if (response.ok) {
        setStatus('connected');
      } else {
        setStatus('error');
      }
    } catch (err) {
      console.error('Connection check failed:', err);
      setStatus('disconnected');
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'connected': return 'bg-green-500';
      case 'checking': return 'bg-yellow-500';
      case 'disconnected':
      case 'error':
      default: return 'bg-red-500';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'connected': return 'API Connected';
      case 'checking': return 'Checking...';
      case 'disconnected': return 'API Disconnected';
      case 'error': return 'API Error';
      default: return 'Unknown';
    }
  };

  return (
    <div className="flex items-center gap-2 text-xs text-gray-400">
      <div className={`w-2 h-2 rounded-full ${getStatusColor()} animate-pulse`}></div>
      <span>{getStatusText()}</span>
      {status === 'disconnected' && (
        <span className="text-red-400 ml-2">
          (Check: {apiUrl})
        </span>
      )}
    </div>
  );
}

export default ConnectionStatus;
