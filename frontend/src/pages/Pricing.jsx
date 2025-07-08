import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { CheckIcon } from '@heroicons/react/24/outline';
import { loadStripe } from '@stripe/stripe-js';
import api from '../utils/api';
import toast from 'react-hot-toast';

const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLIC_KEY || 'pk_test_xxx');

const Pricing = () => {
  const plans = [
    {
      name: 'Basic',
      id: 'basic',
      price: '$79',
      period: 'one-time',
      description: 'Perfect for small businesses and startups',
      features: [
        '1 messaging playbook',
        'Full messaging framework',
        'Ready-to-use content assets',
        'PDF download',
        'Email support',
      ],
      cta: 'Get Started',
      featured: false,
    },
    {
      name: 'Professional',
      id: 'professional',
      price: '$149',
      period: 'one-time',
      description: 'For growing businesses that need multiple playbooks',
      features: [
        '5 messaging playbooks',
        'Everything in Basic',
        'Competitor analysis',
        'Priority support',
        'Custom branding on PDFs',
        'Revision requests',
      ],
      cta: 'Get Professional',
      featured: true,
    },
    {
      name: 'Agency',
      id: 'agency',
      price: '$299',
      period: 'one-time',
      description: 'For agencies and consultants',
      features: [
        'Unlimited playbooks',
        'Everything in Professional',
        'White-label option',
        'API access',
        'Dedicated account manager',
        'Custom integrations',
      ],
      cta: 'Contact Sales',
      featured: false,
    },
  ];

  const handleCheckout = async (planId) => {
    try {
      if (planId === 'agency') {
        window.location.href = 'mailto:sales@messagecraft.com?subject=Agency Plan Inquiry';
        return;
      }

      const response = await api.post('/api/v1/create-checkout', {
        plan_type: planId,
        user_email: 'user@example.com', // Get from auth context
      });

      if (response.data.checkout_url) {
        window.location.href = response.data.checkout_url;
      }
    } catch (error) {
      toast.error('Failed to create checkout session');
    }
  };

  return (
    <div className="bg-white">
      {/* Header */}
      <div className="bg-gray-900 py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mx-auto max-w-2xl text-center"
          >
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Simple, transparent pricing
            </h2>
            <p className="mt-6 text-lg leading-8 text-gray-300">
              Choose the perfect plan for your business needs. All plans include 
              our AI-powered messaging framework generator.
            </p>
          </motion.div>
        </div>
      </div>

      {/* Pricing cards */}
      <div className="mx-auto max-w-7xl px-6 lg:px-8 -mt-16 pb-20">
        <div className="mx-auto grid max-w-md grid-cols-1 gap-8 lg:max-w-none lg:grid-cols-3">
          {plans.map((plan, index) => (
            <motion.div
              key={plan.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className={`flex flex-col justify-between rounded-3xl bg-white p-8 shadow-xl ring-1 ${
                plan.featured
                  ? 'ring-2 ring-primary-600 scale-105'
                  : 'ring-gray-200'
              }`}
            >
              {plan.featured && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <span className="inline-flex items-center rounded-full bg-primary-600 px-4 py-1 text-sm font-medium text-white">
                    Most Popular
                  </span>
                </div>
              )}
              <div>
                <div className="flex items-center justify-between gap-x-4">
                  <h3 className="text-2xl font-bold text-gray-900">
                    {plan.name}
                  </h3>
                  <p className="rounded-full bg-primary-600/10 px-2.5 py-1 text-xs font-semibold leading-5 text-primary-600">
                    {plan.period}
                  </p>
                </div>
                <p className="mt-4 text-sm leading-6 text-gray-600">
                  {plan.description}
                </p>
                <p className="mt-6 flex items-baseline gap-x-1">
                  <span className="text-4xl font-bold tracking-tight text-gray-900">
                    {plan.price}
                  </span>
                </p>
                <ul role="list" className="mt-8 space-y-3 text-sm leading-6 text-gray-600">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex gap-x-3">
                      <CheckIcon
                        className="h-6 w-5 flex-none text-primary-600"
                        aria-hidden="true"
                      />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
              <button
                onClick={() => handleCheckout(plan.id)}
                className={`mt-8 block w-full rounded-md px-3 py-2 text-center text-sm font-semibold leading-6 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 ${
                  plan.featured
                    ? 'bg-primary-600 text-white hover:bg-primary-500 focus-visible:outline-primary-600'
                    : 'bg-gray-50 text-gray-900 hover:bg-gray-100'
                }`}
              >
                {plan.cta}
              </button>
            </motion.div>
          ))}
        </div>
      </div>

      {/* FAQ Section */}
      <div className="mx-auto max-w-7xl px-6 py-16 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="mx-auto max-w-2xl text-center"
        >
          <h2 className="text-2xl font-bold leading-10 tracking-tight text-gray-900">
            Frequently asked questions
          </h2>
        </motion.div>
        <dl className="mt-10 space-y-8 divide-y divide-gray-900/10">
          {[
            {
              question: 'What is a messaging playbook?',
              answer:
                'A messaging playbook is a comprehensive guide containing your value proposition, elevator pitch, taglines, differentiators, and ready-to-use marketing content tailored specifically for your business.',
            },
            {
              question: 'How long does it take to generate a playbook?',
              answer:
                'Our AI agents typically complete your messaging playbook in 2-3 minutes. You\'ll receive a notification when it\'s ready.',
            },
            {
              question: 'Can I edit the generated content?',
              answer:
                'Yes! All generated content is provided as a starting point. You can download your playbook as a PDF and edit the content to perfectly match your needs.',
            },
            {
              question: 'What\'s the difference between plans?',
              answer:
                'The main difference is the number of playbooks you can generate. Basic gives you 1 playbook, Professional gives you 5, and Agency provides unlimited playbooks plus additional features.',
            },
          ].map((faq, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="pt-8 lg:grid lg:grid-cols-12 lg:gap-8"
            >
              <dt className="text-base font-semibold leading-7 text-gray-900 lg:col-span-5">
                {faq.question}
              </dt>
              <dd className="mt-4 lg:col-span-7 lg:mt-0">
                <p className="text-base leading-7 text-gray-600">{faq.answer}</p>
              </dd>
            </motion.div>
          ))}
        </dl>
      </div>
    </div>
  );
};

export default Pricing;