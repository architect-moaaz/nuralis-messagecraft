import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import api from '../utils/api';
import { formatScore } from '../utils/formatters';
import DiscoveryQuestionnaire from '../components/DiscoveryQuestionnaire';
import {
  ClockIcon,
  DocumentTextIcon,
  ArrowRightIcon,
  TrashIcon,
  EyeIcon,
  ArrowDownTrayIcon,
  ChartBarIcon,
  LightBulbIcon,
  PlusIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  ArrowUpRightIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  Cog6ToothIcon,
  RocketLaunchIcon,
  QueueListIcon,
  StarIcon,
  BoltIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';

// Progress indicator component
const ProgressIndicator = ({ currentStep, steps }) => {
  return (
    <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
      <div
        className="bg-clarity-blue h-2 rounded-full transition-all duration-500 ease-in-out"
        style={{ width: `${(currentStep / steps) * 100}%` }}
      />
    </div>
  );
};

// Agent activity indicator
const AgentActivity = ({ isActive, agentName, step }) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`flex items-center gap-3 p-3 rounded-lg border ${
        isActive 
          ? 'bg-clarity-blue/5 border-clarity-blue/20' 
          : 'bg-gray-50 border-gray-200'
      }`}
    >
      <div className={`w-3 h-3 rounded-full ${
        isActive ? 'bg-clarity-blue animate-pulse' : 'bg-gray-400'
      }`} />
      <div className="flex-1">
        <p className={`text-sm font-medium ${
          isActive ? 'text-midnight-navy' : 'text-gray-600'
        }`}>
          {agentName}
        </p>
        <p className="text-xs text-gray-500">{step}</p>
      </div>
      {isActive && (
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-clarity-blue" />
      )}
    </motion.div>
  );
};

// Stats card component
const StatCard = ({ icon: Icon, title, value, change, color = 'blue' }) => {
  const colors = {
    blue: 'text-clarity-blue bg-clarity-blue/10',
    green: 'text-green-600 bg-green-100',
    purple: 'text-purple-600 bg-purple-100',
    orange: 'text-orange-600 bg-orange-100',
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="card p-6"
    >
      <div className="flex items-center">
        <div className={`p-3 rounded-lg ${colors[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-slate-gray">{title}</p>
          <p className="text-2xl font-semibold text-midnight-navy">{value}</p>
          {change && (
            <p className="text-sm text-green-600 flex items-center">
              <ArrowUpRightIcon className="w-4 h-4 mr-1" />
              {change}
            </p>
          )}
        </div>
      </div>
    </motion.div>
  );
};

// Enhanced playbook card
const PlaybookCard = ({ playbook, onView, onDownload, onDelete }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'processing': return 'bg-yellow-100 text-yellow-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };


  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      whileHover={{ scale: 1.02 }}
      className="card p-6 hover:shadow-lg transition-all duration-300"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <DocumentTextIcon className="w-8 h-8 text-clarity-blue" />
          <div>
            <h3 className="font-semibold text-midnight-navy">
              {playbook.results?.business_profile?.company_name || 
               playbook.results?.company_name || 
               'Untitled Playbook'}
            </h3>
          </div>
        </div>
        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(playbook.status)}`}>
          {playbook.status}
        </span>
      </div>

      <p className="text-sm text-slate-gray mb-4 line-clamp-3">
        {playbook.business_input}
      </p>

      {/* Quality score if available */}
      {playbook.results?.quality_review?.overall_quality_score && (
        <div className="mb-4">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-gray">Quality Score</span>
            <span className="font-medium text-midnight-navy">
              {formatScore(playbook.results.quality_review.overall_quality_score)}/10
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
            <div
              className="bg-clarity-blue h-1.5 rounded-full"
              style={{
                width: `${(playbook.results.quality_review.overall_quality_score / 10) * 100}%`,
              }}
            />
          </div>
        </div>
      )}

      <div className="flex items-center justify-between text-xs text-slate-gray mb-4">
        <span>Created: {new Date(playbook.created_at).toLocaleDateString()}</span>
        {playbook.completed_at && (
          <span>Completed: {new Date(playbook.completed_at).toLocaleDateString()}</span>
        )}
      </div>

      <div className="flex gap-2">
        {playbook.status === 'completed' && (
          <>
            <button
              onClick={() => onView(playbook.id)}
              className="flex-1 btn-primary text-sm py-2 flex items-center justify-center"
            >
              <EyeIcon className="w-4 h-4 mr-1" />
              View Details
            </button>
            <button
              onClick={() => onDownload(playbook.id)}
              className="btn-secondary text-sm py-2 px-3"
              title="Download PDF"
            >
              <ArrowDownTrayIcon className="w-4 h-4" />
            </button>
          </>
        )}
        {playbook.status === 'processing' && (
          <div className="flex-1 bg-yellow-50 text-yellow-800 text-sm py-2 px-3 rounded-lg flex items-center justify-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-600 mr-2" />
            Processing...
          </div>
        )}
        {playbook.status === 'failed' && (
          <div className="flex-1 bg-red-50 text-red-800 text-sm py-2 px-3 rounded-lg flex items-center justify-center">
            <ExclamationTriangleIcon className="w-4 h-4 mr-1" />
            Failed
          </div>
        )}
        <button
          onClick={() => onDelete(playbook.id)}
          className="btn-secondary text-sm py-2 px-3 hover:bg-red-50 hover:text-red-600 transition-colors"
          title="Delete playbook"
        >
          <TrashIcon className="w-4 h-4" />
        </button>
      </div>
    </motion.div>
  );
};

const EnhancedDashboard = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentSession, setCurrentSession] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [generationProgress, setGenerationProgress] = useState(0);
  const [currentAgent, setCurrentAgent] = useState('');
  const [generationMode, setGenerationMode] = useState('quick'); // 'questionnaire' or 'quick'
  
  const { register, handleSubmit, formState: { errors }, reset, watch } = useForm();
  const businessDescription = watch('business_description', '');

  // Agents for progress tracking
  const agents = [
    { name: 'Business Discovery', step: 'Analyzing your business...' },
    { name: 'Competitor Research', step: 'Researching competitors...' },
    { name: 'Positioning Analysis', step: 'Finding opportunities...' },
    { name: 'Messaging Framework', step: 'Creating messaging...' },
    { name: 'Content Generation', step: 'Generating content...' },
    { name: 'Quality Review', step: 'Reviewing quality...' },
  ];

  // Fetch user's playbooks
  const { data: playbooks, isLoading, refetch } = useQuery({
    queryKey: ['playbooks'],
    queryFn: async () => {
      const response = await api.get('/api/v1/user/playbooks');
      return response.data.playbooks || [];
    },
    refetchInterval: isGenerating ? 3000 : false, // Poll while generating
  });

  // Calculate stats
  const stats = React.useMemo(() => {
    if (!playbooks) return { total: 0, completed: 0, processing: 0, avgQuality: 0 };
    
    const completed = playbooks.filter(p => p.status === 'completed');
    const processing = playbooks.filter(p => p.status === 'processing');
    
    const qualityScores = completed
      .map(p => p.results?.quality_review?.overall_quality_score)
      .filter(score => score && !isNaN(score))
      .map(score => parseInt(score));
    
    const avgQuality = qualityScores.length > 0 
      ? Math.round(qualityScores.reduce((a, b) => a + b, 0) / qualityScores.length)
      : 0;

    return {
      total: playbooks.length,
      completed: completed.length,
      processing: processing.length,
      avgQuality
    };
  }, [playbooks]);

  // Filter playbooks
  const filteredPlaybooks = React.useMemo(() => {
    if (!playbooks) return [];
    
    return playbooks.filter(playbook => {
      const matchesSearch = !searchTerm || 
        playbook.business_input.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (playbook.results?.business_profile?.company_name || '').toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesStatus = statusFilter === 'all' || playbook.status === statusFilter;
      
      return matchesSearch && matchesStatus;
    });
  }, [playbooks, searchTerm, statusFilter]);

  // Generate playbook mutation
  const generatePlaybook = useMutation({
    mutationFn: async (data) => {
      const response = await api.post('/api/v1/generate-playbook', data);
      return response.data;
    },
    onSuccess: (data) => {
      setCurrentSession(data.session_id);
      setIsGenerating(true);
      setGenerationProgress(0);
      setCurrentAgent('Business Discovery');
      toast.success(`Starting ${data.agent_system || 'playbook'} generation...`);
      pollForCompletion(data.session_id);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to generate playbook');
    },
  });

  // Enhanced polling with progress simulation
  const pollForCompletion = async (sessionId) => {
    let step = 0;
    const maxSteps = 6;
    
    const interval = setInterval(async () => {
      try {
        const response = await api.get(`/api/v1/playbook-status/${sessionId}`);
        
        // Simulate progress through agents
        if (response.data.status === 'processing' && step < maxSteps) {
          step++;
          setGenerationProgress(step);
          setCurrentAgent(agents[step - 1]?.name || 'Processing');
        }
        
        if (response.data.status === 'completed') {
          clearInterval(interval);
          setIsGenerating(false);
          setGenerationProgress(maxSteps);
          setCurrentAgent('Completed');
          
          // Invalidate and refetch
          queryClient.invalidateQueries(['playbooks']);
          
          toast.success('Your messaging playbook is ready!');
          setTimeout(() => navigate(`/playbook/${sessionId}`), 1000);
          
        } else if (response.data.status === 'failed') {
          clearInterval(interval);
          setIsGenerating(false);
          toast.error('Failed to generate playbook. Please try again.');
        }
      } catch (error) {
        clearInterval(interval);
        setIsGenerating(false);
        console.error('Polling error:', error);
      }
    }, 3000);

    // Timeout after 5 minutes
    setTimeout(() => {
      clearInterval(interval);
      if (isGenerating) {
        setIsGenerating(false);
        toast.error('Generation timed out. Please try again.');
      }
    }, 300000);
  };

  const onSubmit = (data) => {
    generatePlaybook.mutate(data);
  };

  const handleQuestionnaireComplete = (questionnaireData) => {
    // Process questionnaire data into our API format
    const processedData = {
      business_description: questionnaireData.business_description,
      company_name: questionnaireData.business_name,
      industry: questionnaireData.business_age, // We can map this better later
      questionnaire_data: questionnaireData
    };
    
    generatePlaybook.mutate(processedData);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this playbook?')) {
      try {
        // Call the DELETE API endpoint
        await api.delete(`/api/v1/playbook/${id}`);
        
        // Update the cache after successful deletion
        queryClient.setQueryData(['playbooks'], (old) => 
          old?.filter(p => p.id !== id) || []
        );
        
        toast.success('Playbook deleted successfully');
      } catch (error) {
        console.error('Delete error:', error);
        
        if (error.response?.status === 404) {
          // Playbook doesn't exist in backend, remove from frontend cache
          queryClient.setQueryData(['playbooks'], (old) => 
            old?.filter(p => p.id !== id) || []
          );
          toast.success('Playbook removed (was already deleted)');
        } else {
          toast.error('Failed to delete playbook');
        }
      }
    }
  };

  const handleDownload = async (id) => {
    try {
      // Simulate download since endpoint may not be fully implemented
      toast.success('Download started...');
      // In a real implementation:
      // const response = await api.get(`/api/v1/download-playbook/${id}`, {
      //   responseType: 'blob',
      // });
      // ... handle download
    } catch (error) {
      toast.error('Download feature coming soon!');
    }
  };

  return (
    <div className="min-h-screen bg-soft-white py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-midnight-navy flex items-center">
            <RocketLaunchIcon className="w-8 h-8 mr-3 text-clarity-blue" />
            Dashboard
          </h1>
          <p className="mt-2 text-slate-gray">
            Generate AI-powered messaging playbooks with our LangGraph multi-agent system
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={DocumentTextIcon}
            title="Total Playbooks"
            value={stats.total}
            color="blue"
          />
          <StatCard
            icon={CheckCircleIcon}
            title="Completed"
            value={stats.completed}
            change={stats.completed > 0 ? `${Math.round((stats.completed / stats.total) * 100)}%` : null}
            color="green"
          />
          <StatCard
            icon={ChartBarIcon}
            title="Avg Quality Score"
            value={stats.avgQuality > 0 ? `${stats.avgQuality}/10` : 'N/A'}
            color="purple"
          />
          <StatCard
            icon={ClockIcon}
            title="Processing"
            value={stats.processing}
            color="orange"
          />
        </div>

        {/* Generation Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card p-8 mb-8"
        >
          <div className="flex items-center mb-6">
            <div className="w-12 h-12 bg-gradient-to-br from-clarity-blue to-midnight-navy rounded-xl flex items-center justify-center mr-4">
              <SparklesIcon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-semibold text-midnight-navy">
                Generate New Messaging Playbook
              </h2>
              <p className="text-slate-gray">
                Powered by LangGraph multi-agent AI system
              </p>
            </div>
          </div>

          {/* Generation Mode Selector */}
          <div className="mb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => setGenerationMode('questionnaire')}
                disabled={isGenerating}
                className={`p-6 rounded-xl border-2 transition-all text-left ${
                  generationMode === 'questionnaire'
                    ? 'border-clarity-blue bg-clarity-blue/5 ring-2 ring-clarity-blue ring-opacity-20'
                    : 'border-gray-200 bg-white hover:border-gray-300'
                } ${isGenerating ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
              >
                <div className="flex items-start">
                  <QueueListIcon className={`w-6 h-6 mr-3 mt-1 ${
                    generationMode === 'questionnaire' ? 'text-clarity-blue' : 'text-gray-600'
                  }`} />
                  <div>
                    <h3 className="font-semibold text-midnight-navy mb-2">
                      Discovery Questionnaire (Recommended)
                    </h3>
                    <p className="text-sm text-slate-gray mb-3">
                      Complete our comprehensive 30-question discovery process for the most targeted and effective messaging. Takes 10-15 minutes.
                    </p>
                    <div className="flex items-center text-xs text-clarity-blue">
                      <StarIcon className="w-4 h-4 mr-1" />
                      Premium quality results
                    </div>
                  </div>
                </div>
              </button>

              <button
                type="button"
                onClick={() => setGenerationMode('quick')}
                disabled={isGenerating}
                className={`p-6 rounded-xl border-2 transition-all text-left ${
                  generationMode === 'quick'
                    ? 'border-clarity-blue bg-clarity-blue/5 ring-2 ring-clarity-blue ring-opacity-20'
                    : 'border-gray-200 bg-white hover:border-gray-300'
                } ${isGenerating ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
              >
                <div className="flex items-start">
                  <RocketLaunchIcon className={`w-6 h-6 mr-3 mt-1 ${
                    generationMode === 'quick' ? 'text-clarity-blue' : 'text-gray-600'
                  }`} />
                  <div>
                    <h3 className="font-semibold text-midnight-navy mb-2">
                      Quick Generation
                    </h3>
                    <p className="text-sm text-slate-gray mb-3">
                      Generate messaging with just a business description. Faster but less comprehensive than the full questionnaire.
                    </p>
                    <div className="flex items-center text-xs text-slate-gray">
                      <BoltIcon className="w-4 h-4 mr-1" />
                      Fast & efficient
                    </div>
                  </div>
                </div>
              </button>
            </div>
          </div>

          {/* Generation in progress */}
          <AnimatePresence>
            {isGenerating && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mb-6 p-6 bg-clarity-blue/5 rounded-xl border border-clarity-blue/20"
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-midnight-navy">
                    Generating Your Playbook
                  </h3>
                  <span className="text-sm text-clarity-blue">
                    {generationProgress}/{agents.length} agents completed
                  </span>
                </div>
                
                <ProgressIndicator currentStep={generationProgress} steps={agents.length} />
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {agents.map((agent, index) => (
                    <AgentActivity
                      key={agent.name}
                      isActive={index === generationProgress - 1}
                      agentName={agent.name}
                      step={agent.step}
                    />
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Content based on generation mode */}
          <AnimatePresence mode="wait">
            {generationMode === 'quick' ? (
              <motion.form
                key="quick-form"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3 }}
                onSubmit={handleSubmit(onSubmit)}
                className="space-y-6"
              >
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label htmlFor="company_name" className="label">
                      Company Name <span className="text-slate-gray">(optional)</span>
                    </label>
                    <input
                      type="text"
                      id="company_name"
                      {...register('company_name')}
                      className="input"
                      placeholder="e.g., Acme Inc."
                      disabled={isGenerating}
                    />
                  </div>

                  <div>
                    <label htmlFor="industry" className="label">
                      Industry <span className="text-slate-gray">(optional)</span>
                    </label>
                    <input
                      type="text"
                      id="industry"
                      {...register('industry')}
                      className="input"
                      placeholder="e.g., B2B SaaS, E-commerce, Healthcare"
                      disabled={isGenerating}
                    />
                  </div>
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
                    placeholder="Tell us about your business: what you do, who you serve, your unique value proposition, and what makes you different from competitors..."
                    disabled={isGenerating}
                  />
                  <div className="flex justify-between mt-1">
                    {errors.business_description && (
                      <p className="text-sm text-red-600">
                        {errors.business_description.message}
                      </p>
                    )}
                    <p className="text-sm text-slate-gray ml-auto">
                      {businessDescription?.length || 0} characters
                    </p>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                  <div className="flex items-center gap-4 text-sm text-slate-gray">
                    <div className="flex items-center">
                      <ClockIcon className="w-4 h-4 mr-1" />
                      2-3 minutes
                    </div>
                    <div className="flex items-center">
                      <Cog6ToothIcon className="w-4 h-4 mr-1" />
                      6 AI agents
                    </div>
                    <div className="flex items-center">
                      <StarIcon className="w-4 h-4 mr-1" />
                      Professional quality
                    </div>
                  </div>
                  
                  <button
                    type="submit"
                    disabled={isGenerating || generatePlaybook.isLoading}
                    className="btn-primary px-8 py-3 text-lg"
                  >
                    {isGenerating || generatePlaybook.isLoading ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                        Generating...
                      </>
                    ) : (
                      <>
                        <RocketLaunchIcon className="w-5 h-5 mr-2" />
                        Generate Quick Playbook
                        <ArrowRightIcon className="w-5 h-5 ml-2" />
                      </>
                    )}
                  </button>
                </div>
              </motion.form>
            ) : (
              <motion.div
                key="questionnaire-form"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
                className="space-y-6"
              >
                <div className="bg-gradient-to-r from-clarity-blue/5 to-accent-mint/5 rounded-xl p-6 border border-clarity-blue/20">
                  <div className="flex items-center mb-4">
                    <div className="w-10 h-10 bg-clarity-blue/10 rounded-lg flex items-center justify-center mr-3">
                      <QueueListIcon className="w-6 h-6 text-clarity-blue" />
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold text-midnight-navy">
                        Messaging & Differentiation Discovery
                      </h3>
                      <p className="text-slate-gray text-sm">
                        Complete our comprehensive discovery process for the most targeted messaging
                      </p>
                    </div>
                  </div>
                  
                  <div className="grid md:grid-cols-3 gap-4 text-sm">
                    <div className="flex items-center text-clarity-blue">
                      <DocumentTextIcon className="w-4 h-4 mr-2" />
                      31 strategic questions
                    </div>
                    <div className="flex items-center text-clarity-blue">
                      <ChartBarIcon className="w-4 h-4 mr-2" />
                      8 business sections
                    </div>
                    <div className="flex items-center text-clarity-blue">
                      <StarIcon className="w-4 h-4 mr-2" />
                      Professional results
                    </div>
                  </div>
                </div>

                <DiscoveryQuestionnaire
                  onComplete={handleQuestionnaireComplete}
                  onCancel={() => setGenerationMode('quick')}
                  embedded={true}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Playbooks Section */}
        <div>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-semibold text-midnight-navy">
              Your Playbooks ({stats.total})
            </h2>
            
            {/* Search and Filter */}
            <div className="flex gap-4">
              <div className="relative">
                <MagnifyingGlassIcon className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search playbooks..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-clarity-blue focus:border-transparent"
                />
              </div>
              
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-clarity-blue focus:border-transparent"
              >
                <option value="all">All Status</option>
                <option value="completed">Completed</option>
                <option value="processing">Processing</option>
                <option value="failed">Failed</option>
              </select>
            </div>
          </div>

          {isLoading ? (
            <div className="flex justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-clarity-blue"></div>
            </div>
          ) : filteredPlaybooks.length > 0 ? (
            <motion.div 
              layout
              className="grid gap-6 md:grid-cols-2 lg:grid-cols-3"
            >
              <AnimatePresence>
                {filteredPlaybooks.map((playbook) => (
                  <PlaybookCard
                    key={playbook.id}
                    playbook={playbook}
                    onView={(id) => navigate(`/playbook/${id}`)}
                    onDownload={handleDownload}
                    onDelete={handleDelete}
                  />
                ))}
              </AnimatePresence>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-12 card"
            >
              <DocumentTextIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-midnight-navy mb-2">
                {searchTerm || statusFilter !== 'all' ? 'No matching playbooks' : 'No playbooks yet'}
              </h3>
              <p className="text-slate-gray mb-6">
                {searchTerm || statusFilter !== 'all' 
                  ? 'Try adjusting your search or filter criteria'
                  : 'Generate your first messaging playbook to get started'
                }
              </p>
              {(!searchTerm && statusFilter === 'all') && (
                <button
                  onClick={() => document.getElementById('business_description')?.focus()}
                  className="btn-primary"
                >
                  <PlusIcon className="w-5 h-5 mr-2" />
                  Create Your First Playbook
                </button>
              )}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EnhancedDashboard;