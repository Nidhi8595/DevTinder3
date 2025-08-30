import React, { createContext, useContext, useReducer, useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

const authReducer = (state, action) => {
  switch (action.type) {
    case 'LOGIN':
      localStorage.setItem('token', action.payload.token);
      localStorage.setItem('user', JSON.stringify(action.payload.user));
      return {
        isAuthenticated: true,
        user: action.payload.user,
        token: action.payload.token
      };
    case 'LOGOUT':
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      return {
        isAuthenticated: false,
        user: null,
        token: null
      };
    case 'UPDATE_USER':
      localStorage.setItem('user', JSON.stringify(action.payload));
      return {
        ...state,
        user: action.payload
      };
    default:
      return state;
  }
};

const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, {
    isAuthenticated: false,
    user: null,
    token: null
  });

  useEffect(() => {
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    
    if (token && user) {
      dispatch({
        type: 'LOGIN',
        payload: {
          token,
          user: JSON.parse(user)
        }
      });
    }
  }, []);

  return (
    <AuthContext.Provider value={{ state, dispatch }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { state } = useAuth();
  return state.isAuthenticated ? children : <Navigate to="/login" />;
};

// Landing Page Component
const LandingPage = () => {
  const navigate = useNavigate();
  const [currentQuote, setCurrentQuote] = useState(0);
  
  const quotes = [
    "Great code is born from great connections.",
    "Swipe right on your next coding buddy 🚀",
    "Where developers find their perfect match.",
    "Build together, grow together.",
    "Your next collaboration is just a swipe away."
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentQuote((prev) => (prev + 1) % quotes.length);
    }, 3000);
    return () => clearInterval(interval);
  }, [quotes.length]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 overflow-hidden">
      {/* Background Animation */}
      <div className="absolute inset-0">
        <div className="absolute top-10 left-10 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
        <div className="absolute top-96 right-10 w-72 h-72 bg-yellow-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse animation-delay-2000"></div>
        <div className="absolute -bottom-32 left-96 w-72 h-72 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse animation-delay-4000"></div>
      </div>

      <div className="relative z-10">
        {/* Navigation */}
        <nav className="flex justify-between items-center px-8 py-6">
          <div className="text-3xl font-bold text-white">
            Dev<span className="text-pink-400">Tinder</span>
          </div>
          <div className="space-x-4">
            <button 
              onClick={() => navigate('/login')}
              className="px-6 py-2 text-white border border-white rounded-full hover:bg-white hover:text-gray-900 transition duration-300"
            >
              Login
            </button>
            <button 
              onClick={() => navigate('/signup')}
              className="px-6 py-2 bg-pink-500 text-white rounded-full hover:bg-pink-600 transition duration-300"
            >
              Sign Up
            </button>
          </div>
        </nav>

        {/* Hero Section */}
        <div className="flex flex-col items-center justify-center min-h-[80vh] text-center px-4">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-6xl md:text-7xl font-bold text-white mb-8 leading-tight">
              Where Developers
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-pink-400 to-yellow-400">
                Connect
              </span>
            </h1>
            
            <div className="h-20 mb-12">
              <p className="text-xl md:text-2xl text-gray-200 animate-fade-in-up">
                {quotes[currentQuote]}
              </p>
            </div>

            <div className="space-y-6 mb-12">
              <button 
                onClick={() => navigate('/signup')}
                className="px-12 py-4 bg-gradient-to-r from-pink-500 to-purple-600 text-white text-xl font-semibold rounded-full hover:from-pink-600 hover:to-purple-700 transform hover:scale-105 transition duration-300 shadow-2xl"
              >
                Start Connecting
              </button>
              <div className="text-gray-300">
                Join thousands of developers building amazing things together
              </div>
            </div>

            {/* Feature Cards */}
            <div className="grid md:grid-cols-3 gap-8 mt-16">
              <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 hover:bg-white/20 transition duration-300">
                <div className="text-4xl mb-4">💻</div>
                <h3 className="text-xl font-semibold text-white mb-2">Skill Matching</h3>
                <p className="text-gray-300">Find developers with complementary skills</p>
              </div>
              
              <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 hover:bg-white/20 transition duration-300">
                <div className="text-4xl mb-4">🚀</div>
                <h3 className="text-xl font-semibold text-white mb-2">Project Partners</h3>
                <p className="text-gray-300">Discover collaborators for your next big idea</p>
              </div>
              
              <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 hover:bg-white/20 transition duration-300">
                <div className="text-4xl mb-4">💬</div>
                <h3 className="text-xl font-semibold text-white mb-2">Real-time Chat</h3>
                <p className="text-gray-300">Connect instantly with fellow developers</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Login Component
const Login = () => {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { dispatch } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API}/auth/login`, formData);
      dispatch({
        type: 'LOGIN',
        payload: {
          token: response.data.access_token,
          user: response.data.user
        }
      });
      navigate('/feed');
    } catch (error) {
      setError(error.response?.data?.detail || 'Login failed');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 flex items-center justify-center px-4">
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 w-full max-w-md">
        <h2 className="text-3xl font-bold text-white text-center mb-8">Welcome Back</h2>
        
        {error && (
          <div className="bg-red-500/20 border border-red-500 text-red-100 px-4 py-2 rounded-lg mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-white mb-2">Email</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:border-pink-400 focus:outline-none"
              placeholder="Enter your email"
              required
            />
          </div>
          
          <div>
            <label className="block text-white mb-2">Password</label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:border-pink-400 focus:outline-none"
              placeholder="Enter your password"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white font-semibold rounded-lg hover:from-pink-600 hover:to-purple-700 disabled:opacity-50 transition duration-300"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        
        <div className="text-center mt-6">
          <span className="text-gray-300">Don't have an account? </span>
          <button
            onClick={() => navigate('/signup')}
            className="text-pink-400 hover:text-pink-300 font-semibold"
          >
            Sign up
          </button>
        </div>
      </div>
    </div>
  );
};

// Signup Component
const Signup = () => {
  const [formData, setFormData] = useState({ name: '', email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { dispatch } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API}/auth/signup`, formData);
      dispatch({
        type: 'LOGIN',
        payload: {
          token: response.data.access_token,
          user: response.data.user
        }
      });
      navigate('/profile');
    } catch (error) {
      setError(error.response?.data?.detail || 'Signup failed');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 flex items-center justify-center px-4">
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 w-full max-w-md">
        <h2 className="text-3xl font-bold text-white text-center mb-8">Join DevTinder</h2>
        
        {error && (
          <div className="bg-red-500/20 border border-red-500 text-red-100 px-4 py-2 rounded-lg mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-white mb-2">Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:border-pink-400 focus:outline-none"
              placeholder="Enter your name"
              required
            />
          </div>
          
          <div>
            <label className="block text-white mb-2">Email</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:border-pink-400 focus:outline-none"
              placeholder="Enter your email"
              required
            />
          </div>
          
          <div>
            <label className="block text-white mb-2">Password</label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:border-pink-400 focus:outline-none"
              placeholder="Enter your password"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white font-semibold rounded-lg hover:from-pink-600 hover:to-purple-700 disabled:opacity-50 transition duration-300"
          >
            {loading ? 'Creating account...' : 'Sign Up'}
          </button>
        </form>
        
        <div className="text-center mt-6">
          <span className="text-gray-300">Already have an account? </span>
          <button
            onClick={() => navigate('/login')}
            className="text-pink-400 hover:text-pink-300 font-semibold"
          >
            Login
          </button>
        </div>
      </div>
    </div>
  );
};

// Profile Component
const Profile = () => {
  const { state, dispatch } = useAuth();
  const [profileData, setProfileData] = useState({
    name: state.user?.name || '',
    bio: state.user?.bio || '',
    skills: state.user?.skills || [],
    interests: state.user?.interests || [],
    profile_pic: state.user?.profile_pic || ''
  });
  const [newSkill, setNewSkill] = useState('');
  const [newInterest, setNewInterest] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.put(
        `${API}/profile`,
        profileData,
        {
          headers: {
            Authorization: `Bearer ${state.token}`
          }
        }
      );
      
      dispatch({
        type: 'UPDATE_USER',
        payload: response.data
      });
      
      navigate('/feed');
    } catch (error) {
      console.error('Profile update failed:', error);
    }
    setLoading(false);
  };

  const addSkill = () => {
    if (newSkill.trim() && !profileData.skills.includes(newSkill.trim())) {
      setProfileData({
        ...profileData,
        skills: [...profileData.skills, newSkill.trim()]
      });
      setNewSkill('');
    }
  };

  const removeSkill = (skill) => {
    setProfileData({
      ...profileData,
      skills: profileData.skills.filter(s => s !== skill)
    });
  };

  const addInterest = () => {
    if (newInterest.trim() && !profileData.interests.includes(newInterest.trim())) {
      setProfileData({
        ...profileData,
        interests: [...profileData.interests, newInterest.trim()]
      });
      setNewInterest('');
    }
  };

  const removeInterest = (interest) => {
    setProfileData({
      ...profileData,
      interests: profileData.interests.filter(i => i !== interest)
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8">
          <h2 className="text-3xl font-bold text-white text-center mb-8">Complete Your Profile</h2>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-white mb-2">Name</label>
              <input
                type="text"
                value={profileData.name}
                onChange={(e) => setProfileData({...profileData, name: e.target.value})}
                className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:border-pink-400 focus:outline-none"
                required
              />
            </div>
            
            <div>
              <label className="block text-white mb-2">Bio</label>
              <textarea
                value={profileData.bio}
                onChange={(e) => setProfileData({...profileData, bio: e.target.value})}
                className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:border-pink-400 focus:outline-none"
                rows="3"
                placeholder="Tell us about yourself..."
              />
            </div>
            
            <div>
              <label className="block text-white mb-2">Profile Picture URL</label>
              <input
                type="url"
                value={profileData.profile_pic}
                onChange={(e) => setProfileData({...profileData, profile_pic: e.target.value})}
                className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:border-pink-400 focus:outline-none"
                placeholder="https://example.com/your-photo.jpg"
              />
            </div>
            
            <div>
              <label className="block text-white mb-2">Skills</label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={newSkill}
                  onChange={(e) => setNewSkill(e.target.value)}
                  className="flex-1 px-4 py-2 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:border-pink-400 focus:outline-none"
                  placeholder="Add a skill"
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
                />
                <button
                  type="button"
                  onClick={addSkill}
                  className="px-4 py-2 bg-pink-500 text-white rounded-lg hover:bg-pink-600 transition duration-300"
                >
                  Add
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {profileData.skills.map((skill, index) => (
                  <span
                    key={index}
                    className="bg-pink-500/20 text-pink-200 px-3 py-1 rounded-full text-sm flex items-center gap-2"
                  >
                    {skill}
                    <button
                      type="button"
                      onClick={() => removeSkill(skill)}
                      className="text-pink-300 hover:text-pink-100"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>
            
            <div>
              <label className="block text-white mb-2">Interests</label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={newInterest}
                  onChange={(e) => setNewInterest(e.target.value)}
                  className="flex-1 px-4 py-2 bg-white/20 border border-white/30 rounded-lg text-white placeholder-gray-300 focus:border-pink-400 focus:outline-none"
                  placeholder="Add an interest"
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addInterest())}
                />
                <button
                  type="button"
                  onClick={addInterest}
                  className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition duration-300"
                >
                  Add
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {profileData.interests.map((interest, index) => (
                  <span
                    key={index}
                    className="bg-purple-500/20 text-purple-200 px-3 py-1 rounded-full text-sm flex items-center gap-2"
                  >
                    {interest}
                    <button
                      type="button"
                      onClick={() => removeInterest(interest)}
                      className="text-purple-300 hover:text-purple-100"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>
            
            <div className="flex gap-4">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white font-semibold rounded-lg hover:from-pink-600 hover:to-purple-700 disabled:opacity-50 transition duration-300"
              >
                {loading ? 'Saving...' : 'Save Profile'}
              </button>
              <button
                type="button"
                onClick={() => navigate('/feed')}
                className="px-6 py-3 bg-white/20 text-white rounded-lg hover:bg-white/30 transition duration-300"
              >
                Skip
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

// Feed Component (Placeholder for now)
const Feed = () => {
  const { state } = useAuth();
  const navigate = useNavigate();

  const logout = () => {
    const { dispatch } = useAuth();
    dispatch({ type: 'LOGOUT' });
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-white">Welcome, {state.user?.name}!</h1>
          <div className="space-x-4">
            <button
              onClick={() => navigate('/profile')}
              className="px-4 py-2 bg-white/20 text-white rounded-lg hover:bg-white/30 transition duration-300"
            >
              Profile
            </button>
            <button
              onClick={() => navigate('/chat')}
              className="px-4 py-2 bg-pink-500 text-white rounded-lg hover:bg-pink-600 transition duration-300"
            >
              Chat
            </button>
            <button
              onClick={logout}
              className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition duration-300"
            >
              Logout
            </button>
          </div>
        </div>
        
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 text-center">
          <h2 className="text-2xl font-bold text-white mb-4">Feed Coming Soon!</h2>
          <p className="text-gray-300">
            This is where you'll swipe through developer profiles. 
            The swipe functionality will be implemented next!
          </p>
        </div>
      </div>
    </div>
  );
};

// Chat Component (Placeholder for now)
const Chat = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-white">Chat</h1>
          <button
            onClick={() => navigate('/feed')}
            className="px-4 py-2 bg-white/20 text-white rounded-lg hover:bg-white/30 transition duration-300"
          >
            Back to Feed
          </button>
        </div>
        
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 text-center">
          <h2 className="text-2xl font-bold text-white mb-4">Chat Coming Soon!</h2>
          <p className="text-gray-300">
            Real-time chat with your connections will be implemented next!
          </p>
        </div>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
          <Route path="/feed" element={<ProtectedRoute><Feed /></ProtectedRoute>} />
          <Route path="/chat" element={<ProtectedRoute><Chat /></ProtectedRoute>} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;