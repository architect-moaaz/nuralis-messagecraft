import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import api from '../utils/api';
import {
  ClockIcon,
  DocumentTextIcon,
  SparklesIcon,
  ArrowRightIcon,
  TrashIcon,
  EyeIcon,
  ArrowDownTrayIcon,
} from '@heroicons/react/24/outline';

const Dashboard = () => {
  const navigate = useNavigate();
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentSession, setCurrentSession] = useState(null);
  const { register, handleSubmit, formState: { errors }, reset } = useForm();

  // Fetch user's playbooks
  const { data: playbooks, isLoading, refetch } = useQuery({
    queryKey: ['playbooks'],
    queryFn: async () => {
      const response = await api.get('/api/v1/user/playbooks');
      return response.data.playbooks;
    },
  });

  // Generate playbook mutation
  const generatePlaybook = useMutation({
    mutationFn: async (data) => {
      const response = await api.post('/api/v1/generate-playbook', data);
      return response.data;
    },
    onSuccess: (data) => {
      setCurrentSession(data.session_id);
      setIsGenerating(true);
      toast.success('Generating your messaging playbook...');
      pollForCompletion(data.session_id);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to generate playbook');
    },
  });

  // Poll for completion
  const pollForCompletion = async (sessionId) => {
    const interval = setInterval(async () => {
      try {
        const response = await api.get(`/api/v1/playbook-status/${sessionId}`);
        if (response.data.status === 'completed') {
          clearInterval(interval);
          setIsGenerating(false);
          refetch();
          toast.success('Your playbook is ready!');
          navigate(`/playbook/${sessionId}`);
        } else if (response.data.status === 'failed') {
          clearInterval(interval);
          setIsGenerating(false);
          toast.error('Failed to generate playbook. Please try again.');
        }
      } catch (error) {
        clearInterval(interval);
        setIsGenerating(false);
      }
    }, 3000);
  };

  const onSubmit = (data) => {
    generatePlaybook.mutate(data);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this playbook?')) {
      try {
        await api.delete(`/api/v1/playbook/${id}`);
        toast.success('Playbook deleted');
        refetch();
      } catch (error) {
        toast.error('Failed to delete playbook');
      }
    }
  };

  const handleDownload = async (id) => {
    try {
      const response = await api.get(`/api/v1/download-playbook/${id}`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `playbook-${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      toast.error('Failed to download playbook');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-gray-600">
            Generate AI-powered messaging playbooks for your business
          </p>
        </div>

        {/* Generation Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card p-6 mb-8"
        >
          <div className="flex items-center mb-6">
            <SparklesIcon className="w-6 h-6 text-primary-600 mr-2" />
            <h2 className="text-xl font-semibold text-gray-900">
              Generate New Playbook
            </h2>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <label htmlFor="company_name" className="label">
                Company Name (optional)
              </label>
              <input
                type="text"
                id="company_name"
                {...register('company_name')}
                className="input"
                placeholder="e.g., Acme Inc."
              />
            </div>

            <div>
              <label htmlFor="industry" className="label">
                Industry (optional)
              </label>
              <input
                type="text"
                id="industry"
                {...register('industry')}
                className="input"
                placeholder="e.g., B2B SaaS, E-commerce, Healthcare"
              />
            </div>

            <div>
              <label htmlFor="business_description" className="label">
                Business Description <span className="text-red-500">*</span>
              </label>
              <textarea
                id="business_description"
                {...register('business_description', {
                  required: 'Business description is required',
                  minLength: {
                    value: 50,
                    message: 'Please provide at least 50 characters',
                  },
                })}
                className="input min-h-[120px]"
                placeholder="Tell us about your business, what you do, who you serve, and what makes you unique..."
              />
              {errors.business_description && (
                <p className="mt-1 text-sm text-red-600">
                  {errors.business_description.message}
                </p>
              )}
            </div>

            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-600">
                <ClockIcon className="w-4 h-4 inline mr-1" />
                Generation takes 2-3 minutes
              </div>
              <button
                type="submit"
                disabled={isGenerating || generatePlaybook.isLoading}
                className="btn-primary"
              >
                {isGenerating || generatePlaybook.isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Generating...
                  </>
                ) : (
                  <>
                    Generate Playbook
                    <ArrowRightIcon className="w-4 h-4 ml-2" />
                  </>
                )}
              </button>
            </div>
          </form>
        </motion.div>

        {/* Previous Playbooks */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Your Playbooks
          </h2>

          {isLoading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            </div>
          ) : playbooks && playbooks.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {playbooks.map((playbook) => (
                <motion.div
                  key={playbook.id}
                  whileHover={{ scale: 1.02 }}
                  className="card p-6 hover:shadow-lg transition-shadow duration-300"
                >
                  <div className="flex items-start justify-between mb-4">
                    <DocumentTextIcon className="w-8 h-8 text-primary-600" />
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded-full ${
                        playbook.status === 'completed'
                          ? 'bg-green-100 text-green-800'
                          : playbook.status === 'processing'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {playbook.status}
                    </span>
                  </div>

                  <h3 className="font-semibold text-gray-900 mb-2">
                    {playbook.results?.company_name || 'Untitled Playbook'}
                  </h3>

                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                    {playbook.business_input}
                  </p>

                  <div className="text-xs text-gray-500 mb-4">
                    Created: {new Date(playbook.created_at).toLocaleDateString()}
                  </div>

                  <div className="flex gap-2">
                    {playbook.status === 'completed' && (
                      <>
                        <button
                          onClick={() => navigate(`/playbook/${playbook.id}`)}
                          className="flex-1 btn-secondary text-sm py-2"
                        >
                          <EyeIcon className="w-4 h-4 mr-1" />
                          View
                        </button>
                        <button
                          onClick={() => handleDownload(playbook.id)}
                          className="btn-secondary text-sm py-2 px-3"
                        >
                          <ArrowDownTrayIcon className="w-4 h-4" />
                        </button>
                      </>
                    )}
                    <button
                      onClick={() => handleDelete(playbook.id)}
                      className="btn-secondary text-sm py-2 px-3 hover:bg-red-50 hover:text-red-600"
                    >
                      <TrashIcon className="w-4 h-4" />
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 card">
              <DocumentTextIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No playbooks yet</p>
              <p className="text-sm text-gray-400 mt-2">
                Generate your first messaging playbook above
              </p>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;