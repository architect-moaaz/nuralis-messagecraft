// Utility functions for formatting data in the dashboard

export const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

export const formatDateTime = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

export const formatStatus = (status) => {
  const statusMap = {
    'completed': 'Completed',
    'processing': 'Processing',
    'failed': 'Failed',
    'pending': 'Pending'
  };
  return statusMap[status] || status;
};

export const getStatusColor = (status) => {
  const colorMap = {
    'completed': 'status-success',
    'processing': 'status-warning', 
    'failed': 'status-error',
    'pending': 'status-info'
  };
  return colorMap[status] || 'bg-gray-100 text-slate-gray';
};

export const truncateText = (text, maxLength = 100) => {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength).trim() + '...';
};

export const getCompanyName = (playbook) => {
  return playbook?.results?.business_profile?.company_name ||
         playbook?.results?.company_name ||
         'Untitled Playbook';
};

export const getQualityScore = (playbook) => {
  return playbook?.results?.quality_review?.overall_quality_score || null;
};

export const calculateProgress = (currentStep, totalSteps) => {
  return Math.round((currentStep / totalSteps) * 100);
};

export const formatScore = (score, decimals = 2) => {
  if (score === null || score === undefined || score === '') return 'N/A';
  
  // Handle objects by returning 'N/A' instead of the object itself
  if (typeof score === 'object') return 'N/A';
  
  const numScore = parseFloat(score);
  return isNaN(numScore) ? 'N/A' : numScore.toFixed(decimals);
};

export const getScoreColor = (score) => {
  // Handle objects and other non-numeric values
  if (typeof score === 'object' || score === null || score === undefined) {
    return 'text-gray-600 bg-gray-100';
  }
  
  const numScore = parseFloat(score);
  if (isNaN(numScore)) return 'text-gray-600 bg-gray-100';
  if (numScore >= 8) return 'text-green-600 bg-green-100';
  if (numScore >= 6) return 'text-yellow-600 bg-yellow-100';
  return 'text-red-600 bg-red-100';
};