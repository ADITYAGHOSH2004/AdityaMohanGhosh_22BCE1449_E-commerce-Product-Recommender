import React, { useState, useEffect } from 'react';
import { ShoppingCart, TrendingUp, Star, User, RefreshCw } from 'lucide-react';
import axios from 'axios';
import './App.css';

const API_URL =  "http://localhost:8080";


function App() {
  const [selectedUser, setSelectedUser] = useState('user1');
  const [recommendations, setRecommendations] = useState([]);
  const [allProducts, setAllProducts] = useState([]);
  const [userBehavior, setUserBehavior] = useState({ viewed: [], purchased: [] });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const userProfiles = {
    user1: { name: "Fitness Enthusiast", icon: "🏃" },
    user2: { name: "Tech Professional", icon: "💻" },
    user3: { name: "Home Enthusiast", icon: "🏠" }
  };

  // Fetch all products on mount
  useEffect(() => {
    fetchProducts();
  }, []);

  // Fetch recommendations when user changes
  useEffect(() => {
    loadRecommendations();
    loadUserBehavior();
  }, [selectedUser]);

  const fetchProducts = async () => {
    try {
      const response = await axios.get(`${API_URL}/products`);
      setAllProducts(response.data);
    } catch (err) {
      console.error('Error fetching products:', err);
      setError('Failed to load products');
    }
  };

  const loadUserBehavior = async () => {
    try {
      const response = await axios.get(`${API_URL}/user/${selectedUser}/behavior`);
      setUserBehavior(response.data);
    } catch (err) {
      console.error('Error loading behavior:', err);
    }
  };

  const loadRecommendations = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`${API_URL}/recommendations/${selectedUser}`);
      setRecommendations(response.data);
    } catch (err) {
      console.error('Error loading recommendations:', err);
      setError('Failed to load recommendations. Make sure backend is running on port 5000.');
    } finally {
      setIsLoading(false);
    }
  };

  const getProductById = (id) => {
    return allProducts.find(p => p.id === id) || {};
  };

  const viewedProducts = userBehavior.viewed.map(id => getProductById(id)).filter(p => p.id);
  const purchasedProducts = userBehavior.purchased.map(id => getProductById(id)).filter(p => p.id);

  return (
    <div className="App">
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-3">
                <ShoppingCart className="w-8 h-8 text-indigo-600" />
                <h1 className="text-3xl font-bold text-gray-800">
                  AI Product Recommender
                </h1>
              </div>
              <div className="flex items-center gap-2">
                <User className="w-5 h-5 text-gray-600" />
                <select
                  value={selectedUser}
                  onChange={(e) => setSelectedUser(e.target.value)}
                  className="border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                >
                  {Object.entries(userProfiles).map(([key, profile]) => (
                    <option key={key} value={key}>
                      {profile.icon} {profile.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-700 text-sm">{error}</p>
                <p className="text-red-600 text-xs mt-1">
                  Tip: Run "python app.py" in the backend folder
                </p>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* User Activity Panel */}
            <div className="lg:col-span-1 space-y-4">
              {/* User Stats */}
              <div className="bg-white rounded-lg shadow p-5">
                <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-indigo-600" />
                  User Activity
                </h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Products Viewed</span>
                    <span className="font-semibold text-indigo-600">
                      {userBehavior.viewed.length}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Products Purchased</span>
                    <span className="font-semibold text-green-600">
                      {userBehavior.purchased.length}
                    </span>
                  </div>
                </div>
              </div>

              {/* Viewed Products */}
              {viewedProducts.length > 0 && (
                <div className="bg-white rounded-lg shadow p-5">
                  <h3 className="font-semibold text-gray-800 mb-3">
                    Recently Viewed
                  </h3>
                  <div className="space-y-2">
                    {viewedProducts.slice(0, 5).map(product => (
                      <div key={product.id} className="text-sm p-2 bg-gray-50 rounded">
                        <div className="font-medium text-gray-700">{product.name}</div>
                        <div className="text-xs text-gray-500">${product.price}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Purchased Products */}
              {purchasedProducts.length > 0 && (
                <div className="bg-white rounded-lg shadow p-5">
                  <h3 className="font-semibold text-gray-800 mb-3">
                    Purchase History
                  </h3>
                  <div className="space-y-2">
                    {purchasedProducts.map(product => (
                      <div key={product.id} className="text-sm p-2 bg-green-50 rounded border border-green-200">
                        <div className="font-medium text-gray-700">{product.name}</div>
                        <div className="text-xs text-gray-500">${product.price}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Recommendations Panel */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow-lg p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-gray-800">
                    Recommended For You
                  </h2>
                  <button
                    onClick={loadRecommendations}
                    disabled={isLoading}
                    className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2 disabled:opacity-50"
                  >
                    <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                    Refresh
                  </button>
                </div>

                {isLoading ? (
                  <div className="flex justify-center items-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
                  </div>
                ) : recommendations.length === 0 ? (
                  <div className="text-center py-12">
                    <p className="text-gray-600">No recommendations available yet.</p>
                    <p className="text-sm text-gray-500 mt-2">
                      Run seed_data.py to populate user behavior data.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-6">
                    {recommendations.map((product, index) => (
                      <div
                        key={product.id}
                        className="border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow"
                      >
                        <div className="flex justify-between items-start mb-3">
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <h3 className="text-xl font-semibold text-gray-800">
                                {product.name}
                              </h3>
                              <span className="bg-indigo-100 text-indigo-800 text-xs px-2 py-1 rounded">
                                #{index + 1}
                              </span>
                            </div>
                            <p className="text-sm text-gray-600">{product.category}</p>
                          </div>
                          <div className="text-right">
                            <div className="text-2xl font-bold text-indigo-600">
                              ${product.price}
                            </div>
                            <div className="flex items-center gap-1 text-yellow-500 text-sm">
                              <Star className="w-4 h-4 fill-current" />
                              <span>{product.rating}</span>
                            </div>
                          </div>
                        </div>
                        
                        <div className="bg-blue-50 border-l-4 border-indigo-500 p-4 rounded mb-4">
                          <div className="flex items-start gap-2">
                            <div className="text-indigo-600 font-semibold text-sm mt-1 whitespace-nowrap">
                              Why recommend?
                            </div>
                            <p className="text-sm text-gray-700 leading-relaxed">
                              {product.explanation}
                            </p>
                          </div>
                        </div>
                        
                        {product.score && (
                          <div className="text-xs text-gray-500 mb-3">
                            Relevance Score: <span className="font-semibold">{product.score.toFixed(1)}</span>
                          </div>
                        )}
                        
                        <div className="flex gap-2 flex-wrap mb-4">
                          {product.tags && product.tags.map(tag => (
                            <span
                              key={tag}
                              className="bg-gray-100 text-gray-700 text-xs px-3 py-1 rounded-full"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                        
                        <button className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 transition-colors font-medium">
                          Add to Cart
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
