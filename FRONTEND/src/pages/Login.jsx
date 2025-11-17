import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BsCpu } from 'react-icons/bs'; // You might need to install react-icons if not done
import AnimatedBackground from '../components/AnimatedBackground';

export default function Login() {
  const [name, setName] = useState('');
  const [regNo, setRegNo] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    // If already logged in, go to chat
    const user = localStorage.getItem("vignan_user");
    if (user) navigate('/chat');
  }, [navigate]);

  const handleLogin = (e) => {
    e.preventDefault();
    if (!name || !regNo) return alert("Please enter details!");

    const userData = { name, regNo };
    localStorage.setItem("vignan_user", JSON.stringify(userData));
    navigate('/chat');
  };

  return (
    <div className="h-screen w-screen flex items-center justify-center text-white relative overflow-hidden font-sans">
      <AnimatedBackground />
      
      <div className="bg-gray-900/60 backdrop-blur-xl p-8 rounded-3xl border border-gray-700 shadow-2xl text-center max-w-sm w-full mx-4 z-10">
        
        {/* Logo */}
        <div className="w-20 h-20 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl mx-auto mb-6 flex items-center justify-center shadow-lg transform rotate-3 hover:rotate-0 transition-all">
          <BsCpu size={40} />
        </div>
        
        <h1 className="text-3xl font-bold mb-1 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">
          Vignan AI
        </h1>
        <p className="text-gray-400 mb-8 text-sm">Student Assistant Portal</p>

        <form onSubmit={handleLogin} className="flex flex-col gap-4">
          <input 
            type="text" 
            placeholder="Student Name" 
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="bg-gray-800/50 border border-gray-600 text-white rounded-xl px-4 py-3 focus:outline-none focus:border-blue-500 transition-colors"
          />
          <input 
            type="text" 
            placeholder="Register Number" 
            value={regNo}
            onChange={(e) => setRegNo(e.target.value)}
            className="bg-gray-800/50 border border-gray-600 text-white rounded-xl px-4 py-3 focus:outline-none focus:border-blue-500 transition-colors"
          />
          
          <button 
            type="submit"
            className="mt-2 bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 px-6 rounded-xl shadow-lg shadow-blue-500/30 transition-all transform active:scale-95"
          >
            Enter Dashboard
          </button>
        </form>
      </div>
    </div>
  );
}