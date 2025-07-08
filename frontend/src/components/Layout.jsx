import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { motion } from 'framer-motion';
import {
  Bars3Icon,
  XMarkIcon,
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
  HomeIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';
import { Disclosure, Menu, Transition } from '@headlessui/react';
import { Fragment } from 'react';

const Layout = ({ children }) => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const navigation = [
    { name: 'Home', href: '/', auth: false, icon: HomeIcon },
    { name: 'Pricing', href: '/pricing', auth: false, icon: CurrencyDollarIcon },
    { name: 'Dashboard', href: '/dashboard', auth: true, icon: ChartBarIcon },
  ];

  const userNavigation = [
    { name: 'Dashboard', href: '/dashboard', icon: ChartBarIcon },
    { name: 'Sign out', action: handleLogout, icon: ArrowRightOnRectangleIcon },
  ];

  return (
    <div className="min-h-screen bg-soft-white">
      <Disclosure as="nav" className="bg-white shadow-sm sticky top-0 z-50">
        {({ open }) => (
          <>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16">
                <div className="flex">
                  <Link to="/" className="flex items-center">
                    <motion.div
                      whileHover={{ scale: 1.05 }}
                      className="flex items-center"
                    >
                      <div className="w-8 h-8 bg-clarity-blue rounded-lg mr-3 flex items-center justify-center">
                        <SparklesIcon className="w-5 h-5 text-white" />
                      </div>
                      <span className="text-xl font-bold text-midnight-navy">
                        MessageCraft
                      </span>
                    </motion.div>
                  </Link>
                  <div className="hidden sm:ml-8 sm:flex sm:space-x-8">
                    {navigation.map((item) => {
                      const Icon = item.icon;
                      return !item.auth || isAuthenticated ? (
                        <Link
                          key={item.name}
                          to={item.href}
                          className="inline-flex items-center px-1 pt-1 text-sm font-medium text-midnight-navy hover:text-clarity-blue transition-colors duration-200"
                        >
                          <Icon className="w-4 h-4 mr-2" />
                          {item.name}
                        </Link>
                      ) : null;
                    })}
                  </div>
                </div>
                <div className="hidden sm:ml-6 sm:flex sm:items-center">
                  {isAuthenticated ? (
                    <Menu as="div" className="ml-3 relative">
                      <div>
                        <Menu.Button className="flex text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-clarity-blue">
                          <span className="sr-only">Open user menu</span>
                          <UserCircleIcon className="h-8 w-8 text-gray-400" />
                        </Menu.Button>
                      </div>
                      <Transition
                        as={Fragment}
                        enter="transition ease-out duration-200"
                        enterFrom="transform opacity-0 scale-95"
                        enterTo="transform opacity-100 scale-100"
                        leave="transition ease-in duration-75"
                        leaveFrom="transform opacity-100 scale-100"
                        leaveTo="transform opacity-0 scale-95"
                      >
                        <Menu.Items className="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white ring-1 ring-black ring-opacity-5 focus:outline-none">
                          <Menu.Item>
                            <div className="px-4 py-2 text-sm text-slate-gray border-b">
                              {user?.email}
                            </div>
                          </Menu.Item>
                          {userNavigation.map((item) => {
                            const Icon = item.icon;
                            return (
                              <Menu.Item key={item.name}>
                                {({ active }) =>
                                  item.action ? (
                                    <button
                                      onClick={item.action}
                                      className={`${
                                        active ? 'bg-gray-100' : ''
                                      } block w-full text-left px-4 py-2 text-sm text-slate-gray flex items-center`}
                                    >
                                      <Icon className="w-4 h-4 mr-2" />
                                      {item.name}
                                    </button>
                                  ) : (
                                    <Link
                                      to={item.href}
                                      className={`${
                                        active ? 'bg-gray-100' : ''
                                      } block px-4 py-2 text-sm text-slate-gray flex items-center`}
                                    >
                                      <Icon className="w-4 h-4 mr-2" />
                                      {item.name}
                                    </Link>
                                  )
                                }
                              </Menu.Item>
                            );
                          })}
                        </Menu.Items>
                      </Transition>
                    </Menu>
                  ) : (
                    <div className="flex items-center space-x-4">
                      <Link
                        to="/login"
                        className="text-midnight-navy hover:text-clarity-blue px-3 py-2 text-sm font-medium"
                      >
                        Sign in
                      </Link>
                      <Link to="/register" className="btn-primary text-sm">
                        Get Started
                      </Link>
                    </div>
                  )}
                </div>
                <div className="-mr-2 flex items-center sm:hidden">
                  <Disclosure.Button className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-clarity-blue">
                    <span className="sr-only">Open main menu</span>
                    {open ? (
                      <XMarkIcon className="block h-6 w-6" aria-hidden="true" />
                    ) : (
                      <Bars3Icon className="block h-6 w-6" aria-hidden="true" />
                    )}
                  </Disclosure.Button>
                </div>
              </div>
            </div>

            <Disclosure.Panel className="sm:hidden">
              <div className="pt-2 pb-3 space-y-1">
                {navigation.map((item) => {
                  const Icon = item.icon;
                  return !item.auth || isAuthenticated ? (
                    <Disclosure.Button
                      key={item.name}
                      as={Link}
                      to={item.href}
                      className="flex items-center pl-3 pr-4 py-2 text-base font-medium text-slate-gray hover:text-midnight-navy hover:bg-gray-50"
                    >
                      <Icon className="w-5 h-5 mr-2" />
                      {item.name}
                    </Disclosure.Button>
                  ) : null;
                })}
              </div>
              <div className="pt-4 pb-3 border-t border-gray-200">
                {isAuthenticated ? (
                  <>
                    <div className="flex items-center px-4">
                      <div className="flex-shrink-0">
                        <UserCircleIcon className="h-10 w-10 text-gray-400" />
                      </div>
                      <div className="ml-3">
                        <div className="text-base font-medium text-slate-gray">
                          {user?.name || 'User'}
                        </div>
                        <div className="text-sm font-medium text-slate-gray">
                          {user?.email}
                        </div>
                      </div>
                    </div>
                    <div className="mt-3 space-y-1">
                      <Disclosure.Button
                        as={Link}
                        to="/dashboard"
                        className="flex items-center px-4 py-2 text-base font-medium text-slate-gray hover:text-midnight-navy hover:bg-gray-100"
                      >
                        <ChartBarIcon className="w-5 h-5 mr-2" />
                        Dashboard
                      </Disclosure.Button>
                      <Disclosure.Button
                        as="button"
                        onClick={handleLogout}
                        className="flex items-center w-full text-left px-4 py-2 text-base font-medium text-slate-gray hover:text-midnight-navy hover:bg-gray-100"
                      >
                        <ArrowRightOnRectangleIcon className="w-5 h-5 mr-2" />
                        Sign out
                      </Disclosure.Button>
                    </div>
                  </>
                ) : (
                  <div className="space-y-1">
                    <Disclosure.Button
                      as={Link}
                      to="/login"
                      className="block px-4 py-2 text-base font-medium text-slate-gray hover:text-midnight-navy hover:bg-gray-100"
                    >
                      Sign in
                    </Disclosure.Button>
                    <Disclosure.Button
                      as={Link}
                      to="/register"
                      className="block px-4 py-2 text-base font-medium text-slate-gray hover:text-midnight-navy hover:bg-gray-100"
                    >
                      Get Started
                    </Disclosure.Button>
                  </div>
                )}
              </div>
            </Disclosure.Panel>
          </>
        )}
      </Disclosure>

      <main>{children}</main>

      {/* Footer */}
      <footer className="bg-white mt-auto">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-primary-600 rounded-lg mr-3 flex items-center justify-center">
                <SparklesIcon className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-semibold text-midnight-navy">
                MessageCraft
              </span>
            </div>
            <p className="text-sm text-slate-gray">
              © 2024 MessageCraft. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;