import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../utils/api';
import { formatScore, getScoreColor } from '../utils/formatters';
import {
  ArrowLeftIcon,
  ArrowDownTrayIcon,
  ClipboardDocumentIcon,
  CheckIcon,
  DocumentTextIcon,
  SparklesIcon,
  ChartBarIcon,
  LightBulbIcon,
  BuildingOfficeIcon,
  UsersIcon,
  ExclamationCircleIcon,
  ChatBubbleLeftRightIcon,
  MegaphoneIcon,
  EyeIcon,
  StarIcon,
  TrophyIcon,
  BoltIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

// Helper function to safely render values that might be objects
const renderValue = (value) => {
  if (!value) return 'Not specified';
  
  if (typeof value === 'object') {
    // Handle common object structures from questionnaire
    if (value.primary) return value.primary;
    if (value.primary_segments) return value.primary_segments;
    if (value.characteristics) return value.characteristics;
    if (Array.isArray(value)) return value.join(', ');
    
    // Fallback for other objects
    return Object.values(value).filter(v => v && typeof v === 'string').join(', ') || 'Not specified';
  }
  
  return value;
};

const CopyableContent = ({ content, label, itemId }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    toast.success(`${label} copied to clipboard`);
    
    setTimeout(() => {
      setCopied(false);
    }, 2000);
  };

  return (
    <div className="bg-soft-white rounded-lg p-4 relative group">
      <p className="text-midnight-navy pr-10 whitespace-pre-line">
        {content}
      </p>
      <button
        onClick={handleCopy}
        className="absolute top-4 right-4 text-slate-gray hover:text-midnight-navy opacity-0 group-hover:opacity-100 transition-opacity"
        title={`Copy ${label}`}
      >
        {copied ? (
          <CheckIcon className="w-5 h-5 text-green-500" />
        ) : (
          <ClipboardDocumentIcon className="w-5 h-5" />
        )}
      </button>
    </div>
  );
};

const SectionCard = ({ icon: Icon, title, children, className = '' }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`card p-8 ${className}`}
    >
      <div className="flex items-center mb-6">
        <div className="w-10 h-10 bg-clarity-blue-100 rounded-lg flex items-center justify-center mr-3">
          <Icon className="w-6 h-6 text-clarity-blue-600" />
        </div>
        <h2 className="text-2xl font-semibold text-midnight-navy">
          {title}
        </h2>
      </div>
      {children}
    </motion.div>
  );
};

const QualityIndicator = ({ score, label }) => {
  return (
    <div className="flex items-center justify-between p-3 bg-soft-white rounded-lg">
      <span className="text-sm font-medium text-slate-gray">{label}</span>
      <span className={`px-2 py-1 rounded-full text-sm font-medium ${getScoreColor(score)}`}>
        {formatScore(score)}/10
      </span>
    </div>
  );
};

const EnhancedPlaybook = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: playbook, isLoading, error } = useQuery({
    queryKey: ['playbook', id],
    queryFn: async () => {
      const response = await api.get(`/api/v1/playbook/${id}`);
      return response.data;
    },
  });

  const handleDownload = async () => {
    try {
      toast.success('Preparing PDF download...');
      
      // Make API call to download PDF
      const response = await api.get(`/api/v1/download-playbook/${id}`, {
        responseType: 'blob',
      });
      
      // Create blob URL and trigger download
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      
      // Extract filename from response headers or use default
      const contentDisposition = response.headers['content-disposition'];
      let filename = 'Messaging_Playbook.pdf';
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '');
        }
      }
      
      // Create download link and trigger click
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.success('PDF downloaded successfully!');
    } catch (error) {
      console.error('Download error:', error);
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          'Failed to download PDF';
      toast.error(errorMessage);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-clarity-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-gray">Loading your playbook...</p>
        </div>
      </div>
    );
  }

  if (error || !playbook) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <DocumentTextIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-semibold text-midnight-navy mb-2">
            Playbook not found
          </h2>
          <p className="text-slate-gray mb-4">
            The playbook you're looking for doesn't exist or has been deleted.
          </p>
          <button onClick={() => navigate('/dashboard')} className="btn-primary">
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const results = playbook.results;
  const businessProfile = results?.business_profile;
  const messagingFramework = results?.messaging_framework;
  const contentAssets = results?.content_assets;
  const qualityReview = results?.quality_review;
  const competitorAnalysis = results?.competitor_analysis;
  const positioningStrategy = results?.positioning_strategy;

  return (
    <div className="min-h-screen bg-soft-white py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="flex items-center text-slate-gray hover:text-midnight-navy transition-colors"
            >
              <ArrowLeftIcon className="w-5 h-5 mr-2" />
              Back to Dashboard
            </button>
            <button
              onClick={handleDownload}
              className="btn-secondary flex items-center"
            >
              <ArrowDownTrayIcon className="w-5 h-5 mr-2" />
              Download PDF
            </button>
          </div>
          
          <h1 className="text-3xl font-bold text-midnight-navy">
            {businessProfile?.company_name || 'Messaging Playbook'}
          </h1>
          <div className="flex items-center gap-4 mt-2 text-sm text-slate-gray">
            <span>Generated on {new Date(playbook.created_at).toLocaleDateString()}</span>
            {playbook.completed_at && (
              <span>• Completed {new Date(playbook.completed_at).toLocaleDateString()}</span>
            )}
            {qualityReview?.overall_quality_score && (
              <span className="flex items-center">
                • Quality Score: 
                <span className="ml-1 font-medium text-clarity-blue-600">
                  {formatScore(qualityReview.overall_quality_score)}/10
                </span>
              </span>
            )}
          </div>
        </motion.div>

        {/* Business Profile */}
        {businessProfile && (
          <SectionCard icon={BuildingOfficeIcon} title="Business Profile" className="mb-8">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-midnight-navy mb-4">Company Overview</h3>
                <div className="space-y-3">
                  <div>
                    <span className="text-sm font-medium text-slate-gray">Industry</span>
                    <p className="text-midnight-navy">{renderValue(businessProfile.industry)}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-slate-gray">Target Audience</span>
                    <p className="text-midnight-navy">{renderValue(businessProfile.target_audience)}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-slate-gray">Tone Preference</span>
                    <p className="text-midnight-navy">{renderValue(businessProfile.tone_preference)}</p>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-midnight-navy mb-4">Key Details</h3>
                <div className="space-y-4">
                  {businessProfile.pain_points && businessProfile.pain_points.length > 0 && (
                    <div>
                      <span className="text-sm font-medium text-slate-gray">Pain Points</span>
                      <ul className="mt-1 space-y-1">
                        {businessProfile.pain_points.map((point, index) => (
                          <li key={index} className="text-midnight-navy text-sm flex items-start">
                            <span className="w-2 h-2 bg-red-400 rounded-full mt-2 mr-2 flex-shrink-0" />
                            {point}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {businessProfile.unique_features && businessProfile.unique_features.length > 0 && (
                    <div>
                      <span className="text-sm font-medium text-slate-gray">Unique Features</span>
                      <ul className="mt-1 space-y-1">
                        {businessProfile.unique_features.map((feature, index) => (
                          <li key={index} className="text-midnight-navy text-sm flex items-start">
                            <span className="w-2 h-2 bg-green-400 rounded-full mt-2 mr-2 flex-shrink-0" />
                            {feature}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </SectionCard>
        )}

        {/* Positioning Strategy */}
        {positioningStrategy && (
          <SectionCard icon={TrophyIcon} title="Strategic Positioning" className="mb-8">
            <div className="space-y-6">
              {positioningStrategy.unique_positioning && (
                <CopyableContent
                  content={positioningStrategy.unique_positioning}
                  label="Unique Positioning"
                />
              )}
              
              <div className="grid md:grid-cols-2 gap-6">
                {positioningStrategy.target_segments && (
                  <div>
                    <h3 className="text-lg font-semibold text-midnight-navy mb-3">Target Segments</h3>
                    <ul className="space-y-2">
                      {positioningStrategy.target_segments.map((segment, index) => (
                        <li key={index} className="flex items-start">
                          <UsersIcon className="w-5 h-5 text-clarity-blue-600 mr-2 mt-0.5 flex-shrink-0" />
                          <span className="text-slate-gray">{segment}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {positioningStrategy.differentiation_strategy && (
                  <div>
                    <h3 className="text-lg font-semibold text-midnight-navy mb-3">Differentiation Strategy</h3>
                    <ul className="space-y-2">
                      {positioningStrategy.differentiation_strategy.map((strategy, index) => (
                        <li key={index} className="flex items-start">
                          <BoltIcon className="w-5 h-5 text-yellow-600 mr-2 mt-0.5 flex-shrink-0" />
                          <span className="text-slate-gray">{strategy}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </SectionCard>
        )}

        {/* Messaging Framework */}
        {messagingFramework && (
          <SectionCard icon={MegaphoneIcon} title="Messaging Framework" className="mb-8">
            {/* Value Proposition */}
            {messagingFramework.value_proposition && (
              <div className="mb-8">
                <h3 className="text-lg font-semibold text-midnight-navy mb-3">Value Proposition</h3>
                <CopyableContent
                  content={messagingFramework.value_proposition}
                  label="Value Proposition"
                />
              </div>
            )}

            {/* Elevator Pitch */}
            {messagingFramework.elevator_pitch && (
              <div className="mb-8">
                <h3 className="text-lg font-semibold text-midnight-navy mb-3">Elevator Pitch</h3>
                <CopyableContent
                  content={messagingFramework.elevator_pitch}
                  label="Elevator Pitch"
                />
              </div>
            )}

            {/* Taglines */}
            {messagingFramework.tagline_options && messagingFramework.tagline_options.length > 0 && (
              <div className="mb-8">
                <h3 className="text-lg font-semibold text-midnight-navy mb-3">Tagline Options</h3>
                <div className="grid gap-3">
                  {messagingFramework.tagline_options.map((tagline, index) => (
                    <div
                      key={index}
                      className="bg-white border border-gray-200 rounded-lg p-4 flex items-center justify-between hover:shadow-sm transition-shadow"
                    >
                      <span className="text-midnight-navy font-medium text-lg">{tagline}</span>
                      <button
                        onClick={() => {
                          navigator.clipboard.writeText(tagline);
                          toast.success('Tagline copied!');
                        }}
                        className="text-slate-gray hover:text-midnight-navy"
                      >
                        <ClipboardDocumentIcon className="w-5 h-5" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Differentiators */}
            {messagingFramework.differentiators && messagingFramework.differentiators.length > 0 && (
              <div className="mb-8">
                <h3 className="text-lg font-semibold text-midnight-navy mb-3">Key Differentiators</h3>
                <div className="space-y-3">
                  {messagingFramework.differentiators.map((diff, index) => (
                    <div key={index} className="flex items-start bg-clarity-blue-50 p-4 rounded-lg">
                      <div className="flex-shrink-0 w-8 h-8 bg-clarity-blue-600 rounded-full flex items-center justify-center mr-3">
                        <span className="text-sm font-semibold text-white">
                          {index + 1}
                        </span>
                      </div>
                      <p className="text-midnight-navy flex-1">{diff}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Objection Responses */}
            {messagingFramework.objection_responses && messagingFramework.objection_responses.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-midnight-navy mb-3">Objection Responses</h3>
                <div className="space-y-4">
                  {messagingFramework.objection_responses.map((item, index) => (
                    <div key={index} className="bg-soft-white p-4 rounded-lg">
                      <div className="flex items-start mb-2">
                        <ExclamationCircleIcon className="w-5 h-5 text-red-500 mr-2 mt-0.5 flex-shrink-0" />
                        <p className="font-medium text-midnight-navy">{item.objection}</p>
                      </div>
                      <div className="flex items-start ml-7">
                        <ChatBubbleLeftRightIcon className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                        <p className="text-slate-gray">{item.response}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </SectionCard>
        )}

        {/* Content Assets */}
        {contentAssets && (
          <SectionCard icon={DocumentTextIcon} title="Ready-to-Use Content" className="mb-8">
            {/* Website Headlines */}
            {contentAssets.website_headlines && contentAssets.website_headlines.length > 0 && (
              <div className="mb-8">
                <h3 className="text-lg font-semibold text-midnight-navy mb-3">Website Headlines</h3>
                <div className="space-y-2">
                  {contentAssets.website_headlines.map((headline, index) => (
                    <CopyableContent
                      key={index}
                      content={headline}
                      label="Website Headline"
                    />
                  ))}
                </div>
              </div>
            )}

            {/* LinkedIn Posts */}
            {contentAssets.linkedin_posts && contentAssets.linkedin_posts.length > 0 && (
              <div className="mb-8">
                <h3 className="text-lg font-semibold text-midnight-navy mb-3">LinkedIn Post Templates</h3>
                <div className="space-y-4">
                  {contentAssets.linkedin_posts.map((post, index) => (
                    <CopyableContent
                      key={index}
                      content={post}
                      label="LinkedIn Post"
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Email Templates */}
            {contentAssets.email_templates && contentAssets.email_templates.length > 0 && (
              <div className="mb-8">
                <h3 className="text-lg font-semibold text-midnight-navy mb-3">Email Templates</h3>
                <div className="space-y-4">
                  {contentAssets.email_templates.map((email, index) => (
                    <div key={index} className="bg-blue-50 p-4 rounded-lg">
                      {typeof email === 'object' ? (
                        <>
                          <div className="mb-2">
                            <span className="text-sm font-medium text-blue-800">Subject:</span>
                            <p className="text-blue-900 font-medium">{email.subject}</p>
                          </div>
                          <div>
                            <span className="text-sm font-medium text-blue-800">Opening:</span>
                            <p className="text-blue-900">{email.opening}</p>
                          </div>
                        </>
                      ) : (
                        <p className="text-blue-900">{email}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Sales One-Liners */}
            {contentAssets.sales_one_liners && contentAssets.sales_one_liners.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-midnight-navy mb-3">Sales One-Liners</h3>
                <div className="grid gap-2">
                  {contentAssets.sales_one_liners.map((line, index) => (
                    <CopyableContent
                      key={index}
                      content={line}
                      label="Sales One-Liner"
                    />
                  ))}
                </div>
              </div>
            )}
          </SectionCard>
        )}

        {/* Reflection Metadata */}
        {results?.reflection_metadata && (
          <SectionCard icon={LightBulbIcon} title="AI Reflection Process" className="mb-8">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-midnight-navy mb-4">Process Overview</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                    <span className="text-sm font-medium text-blue-800">Reflection Cycles</span>
                    <span className="px-2 py-1 rounded-full text-sm font-medium bg-blue-200 text-blue-900">
                      {results.reflection_metadata.total_reflection_cycles}
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <span className="text-sm font-medium text-green-800">Quality Improvement</span>
                    <span className="px-2 py-1 rounded-full text-sm font-medium bg-green-200 text-green-900">
                      {results.reflection_metadata.improvement_achieved ? 'Enhanced' : 'First Pass'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                    <span className="text-sm font-medium text-purple-800">Final Score</span>
                    <span className="px-2 py-1 rounded-full text-sm font-medium bg-purple-200 text-purple-900">
                      {formatScore(results.reflection_metadata.final_quality_score)}/10
                    </span>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-midnight-navy mb-4">Refinement Areas</h3>
                {results.reflection_metadata.refinement_areas_addressed?.length > 0 ? (
                  <ul className="space-y-2">
                    {results.reflection_metadata.refinement_areas_addressed.map((area, index) => (
                      <li key={index} className="flex items-start">
                        <BoltIcon className="w-4 h-4 text-yellow-500 mr-2 mt-0.5 flex-shrink-0" />
                        <span className="text-sm text-slate-gray">{area}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="text-center py-4">
                    <CheckIcon className="w-8 h-8 text-green-500 mx-auto mb-2" />
                    <p className="text-sm text-slate-gray">Quality threshold met on first attempt!</p>
                  </div>
                )}
              </div>
            </div>
            
            {results.reflection_metadata.total_reflection_cycles > 0 && (
              <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
                <div className="flex items-center mb-2">
                  <SparklesIcon className="w-5 h-5 text-purple-600 mr-2" />
                  <h4 className="font-medium text-midnight-navy">AI Reflection Enhancement</h4>
                </div>
                <p className="text-sm text-slate-gray">
                  This playbook was enhanced through our AI reflection process, where multiple AI agents 
                  critiqued and refined the content iteratively to achieve higher quality standards.
                </p>
              </div>
            )}
          </SectionCard>
        )}

        {/* Quality Review */}
        {qualityReview && (
          <SectionCard icon={StarIcon} title="Quality Assessment" className="mb-8">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-midnight-navy mb-4">Quality Scores</h3>
                <div className="space-y-3">
                  <QualityIndicator 
                    score={qualityReview.overall_quality_score} 
                    label="Overall Quality" 
                  />
                  {qualityReview.consistency_score && (
                    <QualityIndicator 
                      score={qualityReview.consistency_score} 
                      label="Consistency" 
                    />
                  )}
                  {qualityReview.clarity_score && (
                    <QualityIndicator 
                      score={qualityReview.clarity_score} 
                      label="Clarity" 
                    />
                  )}
                  {qualityReview.actionability_score && (
                    <QualityIndicator 
                      score={qualityReview.actionability_score} 
                      label="Actionability" 
                    />
                  )}
                </div>
              </div>
              
              <div>
                {qualityReview.strengths && qualityReview.strengths.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold text-midnight-navy mb-3">Strengths</h3>
                    <ul className="space-y-2">
                      {qualityReview.strengths.map((strength, index) => (
                        <li key={index} className="flex items-start">
                          <CheckIcon className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                          <span className="text-slate-gray">{strength}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {qualityReview.improvements && qualityReview.improvements.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-midnight-navy mb-3">Suggestions</h3>
                    <ul className="space-y-2">
                      {qualityReview.improvements.map((improvement, index) => (
                        <li key={index} className="flex items-start">
                          <LightBulbIcon className="w-5 h-5 text-yellow-500 mr-2 mt-0.5 flex-shrink-0" />
                          <span className="text-slate-gray">{improvement}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
            
            {qualityReview.approval_status && (
              <div className="mt-6 p-4 bg-green-50 rounded-lg">
                <div className="flex items-center">
                  <CheckIcon className="w-5 h-5 text-green-500 mr-2" />
                  <span className="font-medium text-green-800">
                    Status: {qualityReview.approval_status}
                  </span>
                </div>
              </div>
            )}
          </SectionCard>
        )}
      </div>
    </div>
  );
};

export default EnhancedPlaybook;