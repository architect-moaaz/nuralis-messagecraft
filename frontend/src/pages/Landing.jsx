import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  SparklesIcon, 
  ChartBarIcon, 
  DocumentTextIcon,
  LightBulbIcon,
  RocketLaunchIcon,
  CheckCircleIcon,
  BoltIcon,
  GlobeAltIcon,
  TrophyIcon,
  ShieldCheckIcon,
  UsersIcon,
  BeakerIcon,
  ArrowRightIcon,
  StarIcon,
  ClockIcon,
  ChatBubbleBottomCenterTextIcon
} from '@heroicons/react/24/outline';

const Landing = () => {
  const features = [
    {
      icon: SparklesIcon,
      title: "AI-Powered Discovery",
      description: "Advanced multi-agent AI system analyzes your business with 31 strategic questions across 8 key areas for deep insights.",
      gradient: "from-clarity-blue to-primary-800"
    },
    {
      icon: BeakerIcon,
      title: "Reflection & Refinement",
      description: "Our AI agents critique and refine content iteratively until it meets premium quality standards.",
      gradient: "from-accent-400 to-accent-600"
    },
    {
      icon: TrophyIcon,
      title: "Strategic Positioning",
      description: "Discover unique market positioning and differentiation strategies that set you apart from competitors.",
      gradient: "from-green-500 to-green-700"
    },
    {
      icon: BoltIcon,
      title: "Lightning Fast",
      description: "Generate comprehensive messaging playbooks in just 2-3 minutes with our optimized AI pipeline.",
      gradient: "from-accent-mint to-accent-500"
    },
    {
      icon: ShieldCheckIcon,
      title: "Quality Assured",
      description: "Every output is scored and validated for consistency, clarity, and market effectiveness.",
      gradient: "from-primary-600 to-clarity-blue"
    },
    {
      icon: GlobeAltIcon,
      title: "Enterprise Ready",
      description: "Scalable platform trusted by startups to Fortune 500 companies for their messaging needs.",
      gradient: "from-slate-gray to-gray-700"
    }
  ];

  const process = [
    {
      step: "1",
      title: "Business Discovery",
      description: "Choose between our quick 2-minute form or comprehensive 31-question discovery questionnaire for deeper insights.",
      icon: ChatBubbleBottomCenterTextIcon
    },
    {
      step: "2",
      title: "Multi-Agent AI Processing",
      description: "11 specialized AI agents work in parallel - from competitor analysis to content creation and quality review.",
      icon: UsersIcon
    },
    {
      step: "3",
      title: "Your Complete Playbook",
      description: "Download your PDF playbook with messaging framework, content assets, and strategic positioning guidance.",
      icon: DocumentTextIcon
    }
  ];

  const stats = [
    { number: "2-3", label: "Minutes to generate", suffix: "min" },
    { number: "11", label: "AI agents working", suffix: "" },
    { number: "31", label: "Strategic questions", suffix: "" },
    { number: "95%", label: "Quality score average", suffix: "" }
  ];

  return (
    <div className="bg-white">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-soft-white via-white to-primary-50">
        {/* Background Elements */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary-50/50 via-transparent to-accent-50/30" />
        <div className="absolute top-0 right-0 w-1/3 h-1/3 bg-gradient-to-bl from-primary-100/40 to-transparent rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-1/4 h-1/4 bg-gradient-to-tr from-accent-100/40 to-transparent rounded-full blur-3xl" />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16 lg:pt-32 lg:pb-24">
          <div className="lg:grid lg:grid-cols-2 lg:gap-16 items-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              {/* Badge */}
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: 0.1 }}
                className="inline-flex items-center gap-2 px-4 py-2 bg-primary-100 text-clarity-blue rounded-full text-sm font-medium mb-6"
              >
                <SparklesIcon className="w-4 h-4" />
                MessageCraft by MarketSmith • 11 AI Agents
              </motion.div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-midnight-navy leading-tight">
                AI-Powered{' '}
                <span className="gradient-text">
                  Messaging
                </span>{' '}
                That Converts
              </h1>
              
              <p className="mt-6 text-xl text-slate-gray leading-relaxed">
                Transform your business messaging with our advanced multi-agent AI system. 
                Get professional-quality playbooks with positioning strategies, value propositions, 
                and ready-to-use content in minutes, not months.
              </p>

              {/* Stats Preview */}
              <div className="mt-8 grid grid-cols-2 sm:grid-cols-4 gap-4">
                {stats.map((stat, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.3 + index * 0.1 }}
                    className="text-center"
                  >
                    <div className="text-2xl font-bold text-midnight-navy">
                      {stat.number}
                      <span className="text-sm text-slate-gray">{stat.suffix}</span>
                    </div>
                    <div className="text-xs text-slate-gray mt-1">{stat.label}</div>
                  </motion.div>
                ))}
              </div>
              
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.4 }}
                className="mt-8 flex flex-col sm:flex-row gap-4"
              >
                <Link 
                  to="/register" 
                  className="group btn-primary text-lg px-8 py-4 rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105"
                >
                  Start Free Trial
                  <ArrowRightIcon className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Link>
                <Link 
                  to="/pricing" 
                  className="btn-secondary text-lg px-8 py-4 rounded-xl"
                >
                  View Pricing
                </Link>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.5 }}
                className="mt-8 flex items-center gap-6 text-sm text-slate-gray"
              >
                <div className="flex items-center gap-2">
                  <CheckCircleIcon className="w-5 h-5 text-green-500" />
                  <span>No credit card required</span>
                </div>
                <div className="flex items-center gap-2">
                  <ClockIcon className="w-5 h-5 text-clarity-blue" />
                  <span>2-3 minute setup</span>
                </div>
                <div className="flex items-center gap-2">
                  <StarIcon className="w-5 h-5 text-accent-mint" />
                  <span>Enterprise quality</span>
                </div>
              </motion.div>
            </motion.div>
            
            {/* Hero Visual */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="hidden lg:block relative"
            >
              <div className="relative">
                {/* Floating Elements */}
                <motion.div
                  animate={{ y: [-10, 10, -10] }}
                  transition={{ duration: 4, repeat: Infinity }}
                  className="absolute -top-4 -left-4 w-20 h-20 bg-gradient-to-br from-clarity-blue to-accent-mint rounded-2xl opacity-80 blur-sm"
                />
                <motion.div
                  animate={{ y: [10, -10, 10] }}
                  transition={{ duration: 3, repeat: Infinity }}
                  className="absolute -bottom-4 -right-4 w-16 h-16 bg-gradient-to-br from-accent-mint to-clarity-blue rounded-2xl opacity-60 blur-sm"
                />
                
                {/* Main Visual - MessageCraft Interface */}
                <div className="relative bg-white rounded-3xl shadow-2xl overflow-hidden border border-gray-100">
                  <img 
                    src="/images/Banner1.png" 
                    alt="MessageCraft interface showing business profile generation for Premier Fitness & Wellness Center"
                    className="w-full h-auto"
                  />
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center"
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-midnight-navy">
              Why Choose MessageCraft by MarketSmith?
            </h2>
            <p className="mt-4 text-xl text-slate-gray max-w-3xl mx-auto">
              MarketSmith's advanced multi-agent AI system delivers enterprise-quality messaging strategies 
              with the speed and precision your business demands.
            </p>
          </motion.div>

          <div className="mt-16 grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="group relative bg-white rounded-2xl p-8 border border-gray-100 hover:border-gray-200 transition-all duration-300 hover:shadow-xl hover:-translate-y-1"
              >
                {/* Gradient Background */}
                <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-300 rounded-2xl`} />
                
                {/* Icon */}
                <div className={`relative w-14 h-14 bg-gradient-to-br ${feature.gradient} rounded-xl flex items-center justify-center mb-6 shadow-lg`}>
                  <feature.icon className="w-7 h-7 text-white" />
                </div>
                
                {/* Content */}
                <h3 className="text-xl font-bold text-midnight-navy mb-3 group-hover:text-clarity-blue transition-colors">
                  {feature.title}
                </h3>
                <p className="text-slate-gray leading-relaxed">
                  {feature.description}
                </p>
                
                {/* Hover Arrow */}
                <ArrowRightIcon className="w-5 h-5 text-slate-gray mt-4 opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all duration-300" />
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Process Section */}
      <section className="py-20 bg-gradient-to-b from-soft-white to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center"
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-midnight-navy">
              How It Works
            </h2>
            <p className="mt-4 text-xl text-slate-gray max-w-3xl mx-auto">
              From business description to complete messaging playbook in three simple steps
            </p>
          </motion.div>

          <div className="mt-16 grid lg:grid-cols-3 gap-12">
            {process.map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
                viewport={{ once: true }}
                className="relative text-center group"
              >
                {/* Connection Line */}
                {index < process.length - 1 && (
                  <div className="hidden lg:block absolute top-16 left-full w-full h-0.5 bg-gradient-to-r from-clarity-blue to-accent-mint z-0">
                    <div className="absolute -right-2 -top-2 w-4 h-4 gradient-accent rounded-full shadow-lg" />
                  </div>
                )}

                {/* Step Icon */}
                <div className="relative mb-6">
                  <div className="w-20 h-20 mx-auto gradient-bg rounded-2xl flex items-center justify-center shadow-xl group-hover:shadow-2xl transition-shadow duration-300">
                    <item.icon className="w-10 h-10 text-white" />
                  </div>
                  <div className="absolute -top-2 -right-2 w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-lg border-2 border-clarity-blue">
                    <span className="text-sm font-bold text-clarity-blue">{item.step}</span>
                  </div>
                </div>

                {/* Content */}
                <h3 className="text-2xl font-bold text-midnight-navy mb-4 group-hover:text-clarity-blue transition-colors">
                  {item.title}
                </h3>
                <p className="text-slate-gray leading-relaxed text-lg">
                  {item.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Results Preview */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center"
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-midnight-navy">
              Your Complete Messaging Arsenal
            </h2>
            <p className="mt-4 text-xl text-slate-gray max-w-3xl mx-auto">
              Everything you need to communicate your value effectively across all channels, 
              delivered as a professional PDF playbook
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            viewport={{ once: true }}
            className="mt-16"
          >
            <div className="grid lg:grid-cols-3 gap-8">
              {/* Strategic Foundation */}
              <div className="bg-gradient-to-br from-primary-50 to-primary-100 rounded-2xl p-8 border border-primary-200">
                <div className="w-12 h-12 bg-gradient-to-br from-clarity-blue to-primary-800 rounded-xl flex items-center justify-center mb-6">
                  <TrophyIcon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-bold text-midnight-navy mb-4">Strategic Foundation</h3>
                <ul className="space-y-3">
                  <li className="flex items-start gap-3">
                    <CheckCircleIcon className="w-5 h-5 text-clarity-blue mt-0.5 flex-shrink-0" />
                    <span className="text-slate-gray">Unique positioning strategy</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircleIcon className="w-5 h-5 text-clarity-blue mt-0.5 flex-shrink-0" />
                    <span className="text-slate-gray">Competitive differentiation</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircleIcon className="w-5 h-5 text-clarity-blue mt-0.5 flex-shrink-0" />
                    <span className="text-slate-gray">Target audience insights</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircleIcon className="w-5 h-5 text-clarity-blue mt-0.5 flex-shrink-0" />
                    <span className="text-slate-gray">Market opportunity analysis</span>
                  </li>
                </ul>
              </div>

              {/* Messaging Framework */}
              <div className="bg-gradient-to-br from-accent-50 to-accent-100 rounded-2xl p-8 border border-accent-200">
                <div className="w-12 h-12 bg-gradient-to-br from-accent-mint to-accent-600 rounded-xl flex items-center justify-center mb-6">
                  <ChatBubbleBottomCenterTextIcon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-bold text-midnight-navy mb-4">Messaging Framework</h3>
                <ul className="space-y-3">
                  <li className="flex items-start gap-3">
                    <CheckCircleIcon className="w-5 h-5 text-accent-mint mt-0.5 flex-shrink-0" />
                    <span className="text-slate-gray">Compelling value proposition</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircleIcon className="w-5 h-5 text-accent-mint mt-0.5 flex-shrink-0" />
                    <span className="text-slate-gray">Perfect elevator pitch</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircleIcon className="w-5 h-5 text-accent-mint mt-0.5 flex-shrink-0" />
                    <span className="text-slate-gray">Multiple tagline options</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircleIcon className="w-5 h-5 text-accent-mint mt-0.5 flex-shrink-0" />
                    <span className="text-slate-gray">Objection responses</span>
                  </li>
                </ul>
              </div>

              {/* Ready-to-Use Content */}
              <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-2xl p-8 border border-green-200">
                <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-700 rounded-xl flex items-center justify-center mb-6">
                  <DocumentTextIcon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-bold text-midnight-navy mb-4">Content Library</h3>
                <ul className="space-y-3">
                  <li className="flex items-start gap-3">
                    <CheckCircleIcon className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                    <span className="text-slate-gray">Website headlines & copy</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircleIcon className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                    <span className="text-slate-gray">LinkedIn post templates</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircleIcon className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                    <span className="text-slate-gray">Email campaign templates</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <CheckCircleIcon className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                    <span className="text-slate-gray">Sales one-liners & scripts</span>
                  </li>
                </ul>
              </div>
            </div>

            {/* Quality Assurance Banner */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              viewport={{ once: true }}
              className="mt-12 gradient-bg rounded-2xl p-8 text-center"
            >
              <div className="flex items-center justify-center gap-4 mb-4">
                <ShieldCheckIcon className="w-8 h-8 text-accent-mint" />
                <h3 className="text-2xl font-bold text-white">Quality Guaranteed</h3>
              </div>
              <p className="text-gray-200 text-lg max-w-3xl mx-auto">
                Every playbook is scored for consistency, clarity, and market effectiveness. 
                MarketSmith's AI reflection system ensures enterprise-quality output every time.
              </p>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative py-20 gradient-bg overflow-hidden">
        {/* Background Elements */}
        <div className="absolute inset-0 bg-gradient-to-br from-clarity-blue/20 to-accent-mint/20" />
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-accent-mint/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-clarity-blue/10 rounded-full blur-3xl" />
        
        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 text-white/90 rounded-full text-sm font-medium mb-6 backdrop-blur-sm"
            >
              <RocketLaunchIcon className="w-4 h-4" />
              Powered by MarketSmith • No Credit Card Required
            </motion.div>

            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-6">
              Ready to Transform Your{' '}
              <span className="text-accent-mint">
                Messaging Strategy?
              </span>
            </h2>
            
            <p className="text-xl text-gray-300 max-w-3xl mx-auto mb-8 leading-relaxed">
              Join forward-thinking businesses that trust MarketSmith's MessageCraft to create messaging 
              that resonates, converts, and drives growth. Start your transformation today.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-8">
              <Link
                to="/register"
                className="group inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-midnight-navy bg-white rounded-xl hover:bg-soft-white transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                Get Started Free
                <ArrowRightIcon className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                to="/pricing"
                className="inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-white border-2 border-white/30 rounded-xl hover:border-white/50 hover:bg-white/5 transition-all duration-200 backdrop-blur-sm"
              >
                View Pricing
              </Link>
            </div>

            {/* Trust Indicators */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-6 text-sm text-gray-400">
              <div className="flex items-center gap-2">
                <CheckCircleIcon className="w-5 h-5 text-green-400" />
                <span>Instant access</span>
              </div>
              <div className="flex items-center gap-2">
                <ShieldCheckIcon className="w-5 h-5 text-accent-mint" />
                <span>Enterprise security</span>
              </div>
              <div className="flex items-center gap-2">
                <StarIcon className="w-5 h-5 text-accent-mint" />
                <span>Premium quality guaranteed</span>
              </div>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default Landing;