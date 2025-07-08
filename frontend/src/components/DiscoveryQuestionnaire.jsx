import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useForm } from 'react-hook-form';
import {
  ChevronLeftIcon,
  ChevronRightIcon,
  CheckCircleIcon,
  QuestionMarkCircleIcon,
  BuildingOfficeIcon,
  UsersIcon,
  RocketLaunchIcon,
  ScaleIcon,
  MegaphoneIcon,
  SparklesIcon,
  DocumentTextIcon,
  ChatBubbleLeftRightIcon,
  LightBulbIcon
} from '@heroicons/react/24/outline';

const DiscoveryQuestionnaire = ({ onComplete, onCancel, embedded = false }) => {
  const [currentSection, setCurrentSection] = useState(0);
  const [completedSections, setCompletedSections] = useState(new Set());
  const { register, handleSubmit, watch, formState: { errors }, setValue, getValues } = useForm();

  const watchedValues = watch();

  // Define questionnaire sections
  const sections = [
    {
      id: 'business-overview',
      title: 'Business Overview',
      icon: BuildingOfficeIcon,
      description: 'Tell us about your business fundamentals',
      color: 'blue',
      questions: [
        {
          id: 'business_name',
          label: 'What is the name of your business?',
          type: 'text',
          required: true,
          placeholder: 'Enter your business name'
        },
        {
          id: 'business_description',
          label: 'How would you describe what your business does—in one sentence?',
          type: 'textarea',
          required: true,
          placeholder: 'We help [target customer] achieve [outcome] through [solution/method]'
        },
        {
          id: 'products_services',
          label: 'What products or services do you offer?',
          type: 'textarea',
          required: true,
          placeholder: 'List your main products or services'
        },
        {
          id: 'business_age',
          label: 'How long have you been in business?',
          type: 'select',
          required: true,
          options: [
            { value: '', label: 'Select duration' },
            { value: 'startup', label: 'Just starting (0-1 years)' },
            { value: 'early', label: 'Early stage (1-3 years)' },
            { value: 'growth', label: 'Growth stage (3-5 years)' },
            { value: 'established', label: 'Established (5+ years)' }
          ]
        },
        {
          id: 'operating_locations',
          label: 'Where do you currently operate (locations, markets)?',
          type: 'textarea',
          required: true,
          placeholder: 'e.g., Local (City, State), National (USA), International'
        }
      ]
    },
    {
      id: 'ideal-customer',
      title: 'Ideal Customer Profile',
      icon: UsersIcon,
      description: 'Define your target audience and their needs',
      color: 'green',
      questions: [
        {
          id: 'primary_customer',
          label: 'Who is your primary customer (describe job role, industry, or lifestyle)?',
          type: 'textarea',
          required: true,
          placeholder: 'e.g., Marketing managers at mid-size tech companies, Small business owners in retail'
        },
        {
          id: 'customer_problems',
          label: 'What specific problems or pain points does your customer have before they work with you?',
          type: 'textarea',
          required: true,
          placeholder: 'List 3-5 specific problems your customers face'
        },
        {
          id: 'customer_success',
          label: 'What does success look like for them after working with you?',
          type: 'textarea',
          required: true,
          placeholder: 'Describe the ideal outcome or transformation'
        },
        {
          id: 'customer_emotions',
          label: 'What emotions or frustrations drive them to search for a solution like yours?',
          type: 'textarea',
          required: true,
          placeholder: 'e.g., Feeling overwhelmed, frustrated with current process, fear of falling behind'
        }
      ]
    },
    {
      id: 'value-outcomes',
      title: 'Value & Outcomes',
      icon: RocketLaunchIcon,
      description: 'What transformation do you create?',
      color: 'purple',
      questions: [
        {
          id: 'specific_outcomes',
          label: 'What are 3–5 specific outcomes or results your product/service creates for your customer?',
          type: 'textarea',
          required: true,
          placeholder: 'List measurable outcomes (e.g., save 10 hours/week, increase revenue by 25%)'
        },
        {
          id: 'transformation',
          label: 'What is the transformation you help your customer go through? (Before → After)',
          type: 'textarea',
          required: true,
          placeholder: 'Before: [current state] → After: [desired state]'
        },
        {
          id: 'top_benefits',
          label: 'What are the top 3 benefits your best customers usually talk about?',
          type: 'textarea',
          required: true,
          placeholder: 'What do your customers say they love most about working with you?'
        },
        {
          id: 'differentiators',
          label: 'What makes your solution better or different than other options out there?',
          type: 'textarea',
          required: true,
          placeholder: 'What unique approach, feature, or methodology sets you apart?'
        }
      ]
    },
    {
      id: 'competitors',
      title: 'Competitor Landscape',
      icon: ScaleIcon,
      description: 'Understanding your competitive environment',
      color: 'orange',
      questions: [
        {
          id: 'top_competitors',
          label: 'Who are your top 3 competitors (by name or website)?',
          type: 'textarea',
          required: true,
          placeholder: 'List competitor names, websites, or descriptions'
        },
        {
          id: 'competitor_positioning',
          label: 'How do they position themselves (in your words or theirs)?',
          type: 'textarea',
          required: true,
          placeholder: 'What messaging or positioning do your competitors use?'
        },
        {
          id: 'competitive_difference',
          label: 'What do you do differently than them?',
          type: 'textarea',
          required: true,
          placeholder: 'Your unique approach, methodology, or advantage'
        },
        {
          id: 'market_misconceptions',
          label: 'What do customers misunderstand about your category, or get wrong?',
          type: 'textarea',
          required: false,
          placeholder: 'Common myths or misconceptions in your industry'
        }
      ]
    },
    {
      id: 'current-messaging',
      title: 'Current Messaging',
      icon: MegaphoneIcon,
      description: 'Your existing communication approach',
      color: 'red',
      questions: [
        {
          id: 'current_headline',
          label: 'What is the main headline or tagline you currently use on your website?',
          type: 'text',
          required: false,
          placeholder: 'Your current main headline or tagline'
        },
        {
          id: 'messaging_clarity',
          label: 'Do you feel your current messaging clearly explains your value?',
          type: 'radio',
          required: true,
          options: [
            { value: 'yes', label: 'Yes, it\'s clear and compelling' },
            { value: 'somewhat', label: 'Somewhat, but could be clearer' },
            { value: 'no', label: 'No, it\'s confusing or generic' }
          ]
        },
        {
          id: 'messaging_clarity_why',
          label: 'Why do you feel that way about your current messaging?',
          type: 'textarea',
          required: false,
          placeholder: 'Explain what works or doesn\'t work about your current messaging'
        },
        {
          id: 'communication_platforms',
          label: 'What platforms do you use most to communicate your message?',
          type: 'checkbox',
          required: true,
          options: [
            { value: 'website', label: 'Website' },
            { value: 'linkedin', label: 'LinkedIn' },
            { value: 'instagram', label: 'Instagram' },
            { value: 'email', label: 'Email Marketing' },
            { value: 'sales_calls', label: 'Sales Calls' },
            { value: 'facebook', label: 'Facebook' },
            { value: 'twitter', label: 'Twitter/X' },
            { value: 'other', label: 'Other' }
          ]
        }
      ]
    },
    {
      id: 'brand-voice',
      title: 'Brand Voice & Style',
      icon: SparklesIcon,
      description: 'How your brand should sound and feel',
      color: 'indigo',
      questions: [
        {
          id: 'brand_tone',
          label: 'How would you describe your brand\'s tone of voice?',
          type: 'checkbox',
          required: true,
          options: [
            { value: 'professional', label: 'Professional' },
            { value: 'friendly', label: 'Friendly' },
            { value: 'bold', label: 'Bold' },
            { value: 'calm', label: 'Calm' },
            { value: 'energetic', label: 'Energetic' },
            { value: 'witty', label: 'Witty' },
            { value: 'authoritative', label: 'Authoritative' },
            { value: 'conversational', label: 'Conversational' }
          ]
        },
        {
          id: 'avoid_words',
          label: 'Are there any words, phrases, or tones you want to avoid?',
          type: 'textarea',
          required: false,
          placeholder: 'e.g., Too technical, overly sales-y, too casual'
        },
        {
          id: 'brand_personality',
          label: 'If your brand were a person, how would it speak?',
          type: 'select',
          required: true,
          options: [
            { value: '', label: 'Select personality type' },
            { value: 'coach', label: 'Supportive Coach' },
            { value: 'teacher', label: 'Knowledgeable Teacher' },
            { value: 'friend', label: 'Trusted Best Friend' },
            { value: 'expert', label: 'Industry Expert' },
            { value: 'consultant', label: 'Strategic Consultant' },
            { value: 'innovator', label: 'Forward-thinking Innovator' }
          ]
        },
        {
          id: 'admired_brands',
          label: 'Are there any brands you admire for their messaging or tone? Why?',
          type: 'textarea',
          required: false,
          placeholder: 'Name brands and what you admire about their communication style'
        }
      ]
    },
    {
      id: 'sales-objections',
      title: 'Sales & Objections',
      icon: ChatBubbleLeftRightIcon,
      description: 'Common challenges in your sales process',
      color: 'yellow',
      questions: [
        {
          id: 'common_objections',
          label: 'What are the most common objections you hear during sales conversations?',
          type: 'textarea',
          required: true,
          placeholder: 'e.g., "Too expensive", "Too complex", "Not sure if it fits our needs"'
        },
        {
          id: 'audience_beliefs',
          label: 'What does your audience believe that you disagree with?',
          type: 'textarea',
          required: false,
          placeholder: 'Common misconceptions or beliefs in your industry that you challenge'
        },
        {
          id: 'trust_signals',
          label: 'What guarantees, proof, or trust signals do you use to overcome doubt?',
          type: 'textarea',
          required: false,
          placeholder: 'e.g., Money-back guarantee, case studies, certifications, testimonials'
        }
      ]
    },
    {
      id: 'testimonials',
      title: 'Testimonials & Social Proof',
      icon: DocumentTextIcon,
      description: 'Customer feedback and validation',
      color: 'teal',
      questions: [
        {
          id: 'existing_testimonials',
          label: 'Do you have existing testimonials, reviews, or case studies?',
          type: 'radio',
          required: true,
          options: [
            { value: 'yes', label: 'Yes, we have several' },
            { value: 'few', label: 'Yes, but only a few' },
            { value: 'no', label: 'No, not yet' }
          ]
        },
        {
          id: 'customer_quotes',
          label: 'Are there any real customer quotes you believe reflect your brand well?',
          type: 'textarea',
          required: false,
          placeholder: 'Share any testimonials or customer feedback that captures your value'
        },
        {
          id: 'additional_info',
          label: 'Anything else you want us to know before we begin building your messaging?',
          type: 'textarea',
          required: false,
          placeholder: 'Any additional context, goals, or specific requirements'
        }
      ]
    }
  ];

  const currentSectionData = sections[currentSection];

  const getSectionColor = (color, type = 'bg') => {
    const colors = {
      blue: type === 'bg' ? 'bg-blue-100 text-blue-800' : 'text-blue-600',
      green: type === 'bg' ? 'bg-green-100 text-green-800' : 'text-green-600',
      purple: type === 'bg' ? 'bg-purple-100 text-purple-800' : 'text-purple-600',
      orange: type === 'bg' ? 'bg-orange-100 text-orange-800' : 'text-orange-600',
      red: type === 'bg' ? 'bg-red-100 text-red-800' : 'text-red-600',
      indigo: type === 'bg' ? 'bg-indigo-100 text-indigo-800' : 'text-indigo-600',
      yellow: type === 'bg' ? 'bg-yellow-100 text-yellow-800' : 'text-yellow-600',
      teal: type === 'bg' ? 'bg-teal-100 text-teal-800' : 'text-teal-600'
    };
    return colors[color] || colors.blue;
  };

  const validateSection = (sectionIndex) => {
    const section = sections[sectionIndex];
    const values = getValues();
    
    return section.questions.every(question => {
      if (!question.required) return true;
      const value = values[question.id];
      
      if (question.type === 'checkbox') {
        return value && Object.values(value).some(v => v);
      }
      
      return value && value.trim() !== '';
    });
  };

  const handleNext = () => {
    if (validateSection(currentSection)) {
      setCompletedSections(prev => new Set([...prev, currentSection]));
      if (currentSection < sections.length - 1) {
        setCurrentSection(currentSection + 1);
      }
    }
  };

  const handlePrevious = () => {
    if (currentSection > 0) {
      setCurrentSection(currentSection - 1);
    }
  };

  const handleSectionClick = (index) => {
    if (index <= currentSection || completedSections.has(index)) {
      setCurrentSection(index);
    }
  };

  const onSubmit = (data) => {
    // Process checkbox arrays
    const processedData = { ...data };
    
    sections.forEach(section => {
      section.questions.forEach(question => {
        if (question.type === 'checkbox' && processedData[question.id]) {
          processedData[question.id] = Object.keys(processedData[question.id]).filter(
            key => processedData[question.id][key]
          );
        }
      });
    });

    onComplete(processedData);
  };

  const renderQuestion = (question) => {
    const fieldName = question.id;
    const error = errors[fieldName];

    switch (question.type) {
      case 'text':
        return (
          <input
            {...register(fieldName, { required: question.required })}
            type="text"
            className="input"
            placeholder={question.placeholder}
          />
        );

      case 'textarea':
        return (
          <textarea
            {...register(fieldName, { required: question.required })}
            rows={4}
            className="input resize-none"
            placeholder={question.placeholder}
          />
        );

      case 'select':
        return (
          <select
            {...register(fieldName, { required: question.required })}
            className="input"
          >
            {question.options.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );

      case 'radio':
        return (
          <div className="space-y-3">
            {question.options.map(option => (
              <label key={option.value} className="flex items-center">
                <input
                  {...register(fieldName, { required: question.required })}
                  type="radio"
                  value={option.value}
                  className="w-4 h-4 text-clarity-blue border-gray-300 focus:ring-clarity-blue"
                />
                <span className="ml-3 text-midnight-navy">{option.label}</span>
              </label>
            ))}
          </div>
        );

      case 'checkbox':
        return (
          <div className="space-y-3">
            {question.options.map(option => (
              <label key={option.value} className="flex items-center">
                <input
                  {...register(`${fieldName}.${option.value}`)}
                  type="checkbox"
                  className="w-4 h-4 text-clarity-blue border-gray-300 rounded focus:ring-clarity-blue"
                />
                <span className="ml-3 text-midnight-navy">{option.label}</span>
              </label>
            ))}
          </div>
        );

      default:
        return null;
    }
  };

  const progress = ((currentSection + 1) / sections.length) * 100;
  const isLastSection = currentSection === sections.length - 1;
  const canProceed = validateSection(currentSection);

  return (
    <div className={embedded ? "" : "min-h-screen bg-soft-white py-8"}>
      <div className={embedded ? "" : "max-w-4xl mx-auto px-4 sm:px-6 lg:px-8"}>
        {/* Header - only show if not embedded */}
        {!embedded && (
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-midnight-navy mb-2">
              Messaging & Differentiation Discovery
            </h1>
            <p className="text-lg text-slate-gray">
              Help us understand your business to craft strong, clear, and differentiated messaging
            </p>
          </div>
        )}

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between text-sm font-medium text-slate-gray mb-2">
            <span>Section {currentSection + 1} of {sections.length}</span>
            <span>{Math.round(progress)}% Complete</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-clarity-blue h-2 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Section Navigation */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-8">
          {sections.map((section, index) => {
            const Icon = section.icon;
            const isActive = index === currentSection;
            const isCompleted = completedSections.has(index);
            const isAccessible = index <= currentSection || completedSections.has(index);

            return (
              <button
                key={section.id}
                onClick={() => handleSectionClick(index)}
                disabled={!isAccessible}
                className={`p-3 rounded-lg border-2 transition-all text-sm ${
                  isActive
                    ? `border-${section.color}-500 ${getSectionColor(section.color)} shadow-md`
                    : isCompleted
                    ? `border-green-500 bg-green-50 text-green-800`
                    : isAccessible
                    ? 'border-gray-200 bg-white text-slate-gray hover:border-gray-300'
                    : 'border-gray-200 bg-gray-100 text-gray-400 cursor-not-allowed'
                }`}
              >
                <div className="flex items-center">
                  {isCompleted ? (
                    <CheckCircleIcon className="w-5 h-5 mr-2 text-green-600" />
                  ) : (
                    <Icon className={`w-5 h-5 mr-2 ${isActive ? getSectionColor(section.color, 'text') : ''}`} />
                  )}
                  <span className="font-medium truncate">{section.title}</span>
                </div>
              </button>
            );
          })}
        </div>

        {/* Current Section */}
        <motion.div
          key={currentSection}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          className="card p-8"
        >
          {/* Section Header */}
          <div className="flex items-center mb-6">
            <div className={`w-12 h-12 rounded-lg flex items-center justify-center mr-4 ${getSectionColor(currentSectionData.color)}`}>
              <currentSectionData.icon className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-midnight-navy">
                {currentSectionData.title}
              </h2>
              <p className="text-slate-gray">{currentSectionData.description}</p>
            </div>
          </div>

          {/* Questions */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {currentSectionData.questions.map((question, index) => (
              <motion.div
                key={question.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="space-y-2"
              >
                <label className="label flex items-center">
                  {question.label}
                  {question.required && <span className="text-red-500 ml-1">*</span>}
                  {question.help && (
                    <QuestionMarkCircleIcon className="w-4 h-4 text-gray-400 ml-2" title={question.help} />
                  )}
                </label>
                {renderQuestion(question)}
                {errors[question.id] && (
                  <p className="text-sm text-red-600">This field is required</p>
                )}
              </motion.div>
            ))}

            {/* Navigation Buttons */}
            <div className="flex justify-between pt-8 border-t">
              <button
                type="button"
                onClick={onCancel}
                className="btn-secondary flex items-center"
              >
                Cancel
              </button>

              <div className="flex gap-3">
                {currentSection > 0 && (
                  <button
                    type="button"
                    onClick={handlePrevious}
                    className="btn-secondary flex items-center"
                  >
                    <ChevronLeftIcon className="w-4 h-4 mr-1" />
                    Previous
                  </button>
                )}

                {isLastSection ? (
                  <button
                    type="submit"
                    disabled={!canProceed}
                    className="btn-primary flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <RocketLaunchIcon className="w-4 h-4 mr-1" />
                    Generate Enhanced Playbook
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={handleNext}
                    disabled={!canProceed}
                    className="btn-primary flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next Section
                    <ChevronRightIcon className="w-4 h-4 ml-1" />
                  </button>
                )}
              </div>
            </div>
          </form>
        </motion.div>

        {/* Help Text */}
        <div className="mt-6 text-center text-sm text-slate-gray">
          <div className="flex items-center justify-center">
            <LightBulbIcon className="w-4 h-4 text-amber-500 mr-2" />
            <p>Take your time - this information helps us create better, more targeted messaging for your business</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DiscoveryQuestionnaire;