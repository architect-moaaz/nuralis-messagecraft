import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';

const AuthCallback = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { setAuthToken } = useAuth();

  useEffect(() => {
    const token = searchParams.get('token');
    const error = searchParams.get('error');

    if (token) {
      // Store the token
      localStorage.setItem('token', token);
      
      // Set auth state
      if (setAuthToken) {
        setAuthToken(token);
      }
      
      // Redirect to dashboard
      navigate('/dashboard');
    } else if (error) {
      // Handle error
      console.error('OAuth error:', error);
      navigate('/login?error=oauth_failed');
    } else {
      // No token or error, redirect to login
      navigate('/login');
    }
  }, [searchParams, navigate, setAuthToken]);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <LoadingSpinner />
        <p className="mt-4 text-gray-600">Completing authentication...</p>
      </div>
    </div>
  );
};

export default AuthCallback;