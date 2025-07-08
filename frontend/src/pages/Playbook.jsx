import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { atomDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import api from '../utils/api';
import { formatScore } from '../utils/formatters';
import {
  ArrowLeftIcon,
  ArrowDownTrayIcon,
  ClipboardDocumentIcon,
  CheckIcon,
  DocumentTextIcon,
  SparklesIcon,
  ChartBarIcon,
  LightBulbIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const Playbook = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [copiedItems, setCopiedItems] = useState({});

  const { data: playbook, isLoading, error } = useQuery({
    queryKey: ['playbook', id],
    queryFn: async () => {
      const response = await api.get(`/api/v1/playbook/${id}`);
      return response.data;
    },
  });

  const handleCopy = (text, itemId) => {
    navigator.clipboard.writeText(text);
    setCopiedItems({ ...copiedItems, [itemId]: true });
    toast.success('Copied to clipboard');
    
    setTimeout(() => {
      setCopiedItems((prev) => ({ ...prev, [itemId]: false }));
    }, 2000);
  };

  const handleDownload = async () => {
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
      toast.success('Downloading playbook...');
    } catch (error) {
      toast.error('Failed to download playbook');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-clarity-blue"></div>
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

  const results = typeof playbook.results === 'string' 
    ? JSON.parse(playbook.results) 
    : playbook.results;

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
              className="flex items-center text-slate-gray hover:text-midnight-navy"
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
            {results.company_name || 'Messaging Playbook'}
          </h1>
          <p className="mt-2 text-slate-gray">
            Generated on {new Date(playbook.created_at).toLocaleDateString()}
          </p>
        </motion.div>

        {/* Messaging Framework */}
        {results.messaging_framework && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card p-8 mb-8"
          >
            <div className="flex items-center mb-6">
              <SparklesIcon className="w-6 h-6 text-clarity-blue mr-2" />
              <h2 className="text-2xl font-semibold text-midnight-navy">
                Messaging Framework
              </h2>
            </div>

            {/* Value Proposition */}
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-midnight-navy mb-3">
                Value Proposition
              </h3>
              <div className="bg-soft-white rounded-lg p-4 relative">
                <p className="text-gray-800 pr-10">
                  {results.messaging_framework.value_proposition}
                </p>
                <button
                  onClick={() => handleCopy(results.messaging_framework.value_proposition, 'value-prop')}
                  className="absolute top-4 right-4 text-clarity-blue hover:text-clarity-blue"
                >
                  {copiedItems['value-prop'] ? (
                    <CheckIcon className="w-5 h-5" />
                  ) : (
                    <ClipboardDocumentIcon className="w-5 h-5" />
                  )}
                </button>
              </div>
            </div>

            {/* Elevator Pitch */}
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-midnight-navy mb-3">
                Elevator Pitch
              </h3>
              <div className="bg-soft-white rounded-lg p-4 relative">
                <p className="text-gray-800 pr-10">
                  {results.messaging_framework.elevator_pitch}
                </p>
                <button
                  onClick={() => handleCopy(results.messaging_framework.elevator_pitch, 'elevator-pitch')}
                  className="absolute top-4 right-4 text-slate-gray hover:text-slate-gray"
                >
                  {copiedItems['elevator-pitch'] ? (
                    <CheckIcon className="w-5 h-5" />
                  ) : (
                    <ClipboardDocumentIcon className="w-5 h-5" />
                  )}
                </button>
              </div>
            </div>

            {/* Taglines */}
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-midnight-navy mb-3">
                Tagline Options
              </h3>
              <div className="grid gap-3">
                {results.messaging_framework.tagline_options?.map((tagline, index) => (
                  <div
                    key={index}
                    className="bg-white border border-gray-200 rounded-lg p-3 flex items-center justify-between"
                  >
                    <span className="text-gray-800 font-medium">{tagline}</span>
                    <button
                      onClick={() => handleCopy(tagline, `tagline-${index}`)}
                      className="text-gray-500 hover:text-gray-700"
                    >
                      {copiedItems[`tagline-${index}`] ? (
                        <CheckIcon className="w-5 h-5" />
                      ) : (
                        <ClipboardDocumentIcon className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Differentiators */}
            <div>
              <h3 className="text-lg font-semibold text-midnight-navy mb-3">
                Key Differentiators
              </h3>
              <div className="space-y-3">
                {results.messaging_framework.differentiators?.map((diff, index) => (
                  <div key={index} className="flex items-start">
                    <div className="flex-shrink-0 w-6 h-6 bg-soft-white rounded-full flex items-center justify-center mt-0.5">
                      <span className="text-xs font-semibold text-clarity-blue">
                        {index + 1}
                      </span>
                    </div>
                    <p className="ml-3 text-slate-gray">{diff}</p>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {/* Content Assets */}
        {results.content_assets && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="card p-8 mb-8"
          >
            <div className="flex items-center mb-6">
              <DocumentTextIcon className="w-6 h-6 text-clarity-blue mr-2" />
              <h2 className="text-2xl font-semibold text-midnight-navy">
                Ready-to-Use Content
              </h2>
            </div>

            {/* Website Headlines */}
            {results.content_assets.website_headlines && (
              <div className="mb-8">
                <h3 className="text-lg font-semibold text-midnight-navy mb-3">
                  Website Headlines
                </h3>
                <div className="space-y-2">
                  {results.content_assets.website_headlines.map((headline, index) => (
                    <div
                      key={index}
                      className="bg-soft-white rounded-lg p-3 flex items-center justify-between"
                    >
                      <span className="text-gray-800">{headline}</span>
                      <button
                        onClick={() => handleCopy(headline, `headline-${index}`)}
                        className="text-gray-500 hover:text-gray-700 ml-4"
                      >
                        {copiedItems[`headline-${index}`] ? (
                          <CheckIcon className="w-5 h-5" />
                        ) : (
                          <ClipboardDocumentIcon className="w-5 h-5" />
                        )}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* LinkedIn Posts */}
            {results.content_assets.linkedin_posts && (
              <div className="mb-8">
                <h3 className="text-lg font-semibold text-midnight-navy mb-3">
                  LinkedIn Post Templates
                </h3>
                <div className="space-y-3">
                  {results.content_assets.linkedin_posts.map((post, index) => (
                    <div
                      key={index}
                      className="bg-soft-white rounded-lg p-4 relative"
                    >
                      <p className="text-gray-800 whitespace-pre-line pr-10">
                        {post}
                      </p>
                      <button
                        onClick={() => handleCopy(post, `linkedin-${index}`)}
                        className="absolute top-4 right-4 text-clarity-blue hover:text-clarity-blue"
                      >
                        {copiedItems[`linkedin-${index}`] ? (
                          <CheckIcon className="w-5 h-5" />
                        ) : (
                          <ClipboardDocumentIcon className="w-5 h-5" />
                        )}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Email Templates */}
            {results.content_assets.email_templates && (
              <div className="mb-8">
                <h3 className="text-lg font-semibold text-midnight-navy mb-3">
                  Email Templates
                </h3>
                <div className="space-y-3">
                  {results.content_assets.email_templates.map((email, index) => (
                    <div
                      key={index}
                      className="bg-soft-white rounded-lg p-4 relative"
                    >
                      <p className="text-gray-800 pr-10">{email}</p>
                      <button
                        onClick={() => handleCopy(email, `email-${index}`)}
                        className="absolute top-4 right-4 text-slate-gray hover:text-slate-gray"
                      >
                        {copiedItems[`email-${index}`] ? (
                          <CheckIcon className="w-5 h-5" />
                        ) : (
                          <ClipboardDocumentIcon className="w-5 h-5" />
                        )}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Sales One-Liners */}
            {results.content_assets.sales_one_liners && (
              <div>
                <h3 className="text-lg font-semibold text-midnight-navy mb-3">
                  Sales One-Liners
                </h3>
                <div className="grid gap-2">
                  {results.content_assets.sales_one_liners.map((line, index) => (
                    <div
                      key={index}
                      className="bg-soft-white rounded-lg p-3 flex items-center justify-between"
                    >
                      <span className="text-gray-800">{line}</span>
                      <button
                        onClick={() => handleCopy(line, `sales-${index}`)}
                        className="text-accent-mint hover:text-accent-mint ml-4"
                      >
                        {copiedItems[`sales-${index}`] ? (
                          <CheckIcon className="w-5 h-5" />
                        ) : (
                          <ClipboardDocumentIcon className="w-5 h-5" />
                        )}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}

        {/* Positioning Analysis */}
        {results.positioning_analysis && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="card p-8 mb-8"
          >
            <div className="flex items-center mb-6">
              <ChartBarIcon className="w-6 h-6 text-clarity-blue mr-2" />
              <h2 className="text-2xl font-semibold text-midnight-navy">
                Market Positioning
              </h2>
            </div>

            {results.positioning_analysis.gaps && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-midnight-navy mb-3">
                  Market Gaps
                </h3>
                <ul className="space-y-2">
                  {results.positioning_analysis.gaps.map((gap, index) => (
                    <li key={index} className="flex items-start">
                      <LightBulbIcon className="w-5 h-5 text-yellow-500 mr-2 mt-0.5 flex-shrink-0" />
                      <span className="text-slate-gray">{gap}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {results.positioning_analysis.opportunities && (
              <div>
                <h3 className="text-lg font-semibold text-midnight-navy mb-3">
                  Opportunities
                </h3>
                <ul className="space-y-2">
                  {results.positioning_analysis.opportunities.map((opp, index) => (
                    <li key={index} className="flex items-start">
                      <CheckIcon className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                      <span className="text-slate-gray">{opp}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </motion.div>
        )}

        {/* Quality Review */}
        {results.quality_review && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="card p-8"
          >
            <h2 className="text-2xl font-semibold text-midnight-navy mb-6">
              Quality Assessment
            </h2>
            
            <div className="flex items-center justify-between mb-4">
              <span className="text-slate-gray">Quality Score</span>
              <div className="flex items-center">
                <div className="w-32 bg-gray-200 rounded-full h-3 mr-3">
                  <div
                    className="bg-clarity-blue h-3 rounded-full"
                    style={{
                      width: `${(results.quality_review.quality_score / 10) * 100}%`,
                    }}
                  />
                </div>
                <span className="font-semibold text-midnight-navy">
                  {formatScore(results.quality_review.quality_score)}/10
                </span>
              </div>
            </div>

            {results.quality_review.improvements && (
              <div className="mt-6">
                <h3 className="text-lg font-semibold text-midnight-navy mb-3">
                  Suggested Improvements
                </h3>
                <ul className="space-y-2">
                  {results.quality_review.improvements.map((improvement, index) => (
                    <li key={index} className="text-slate-gray">
                      • {improvement}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default Playbook;