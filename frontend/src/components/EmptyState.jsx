import React from 'react';
import { motion } from 'framer-motion';

const EmptyState = ({ 
  icon: Icon, 
  title, 
  description, 
  action, 
  actionText = 'Get Started',
  className = '' 
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`text-center py-12 ${className}`}
    >
      {Icon && (
        <Icon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
      )}
      <h3 className="text-lg font-medium text-gray-900 mb-2">
        {title}
      </h3>
      <p className="text-gray-500 mb-6 max-w-md mx-auto">
        {description}
      </p>
      {action && (
        <button
          onClick={action}
          className="btn-primary"
        >
          {actionText}
        </button>
      )}
    </motion.div>
  );
};

export default EmptyState;