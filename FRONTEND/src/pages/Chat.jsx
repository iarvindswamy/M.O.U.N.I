import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { BsGlobe, BsSendFill, BsPersonCircle, BsRobot } from 'react-icons/bs';
import { BiLogOut, BiTrash } from 'react-icons/bi';
import ReactMarkdown from 'react-markdown';
import AnimatedBackground from '../components/AnimatedBackground';

export default function Chat() {
  const navigate = useNavigate();
  const scrollRef = useRef();

  // --- FIX 1: Initialize User State DIRECTLY from LocalStorage ---
  // This prevents the "setState in useEffect" error and makes loading faster.
  const [user,] = useState(() => {
    const stored = localStorage.getItem("vignan_user");
    return stored ? JSON.parse(stored) : null;
  });

  // --- FIX 2: Initialize Messages DIRECTLY from LocalStorage ---
  const [messages, setMessages] = useState(() => {
    const storedChats = localStorage.getItem("chat_history");
    return storedChats ? JSON.parse(storedChats) : [];
  });

  const [input, setInput] = useState('');
  const [isWebSearch, setIsWebSearch] = useState(false);
  const [loading, setLoading] = useState(false);

  // --- Security Check Only ---
  // If user is null (not logged in), kick them back to Login page
  useEffect(() => {
    if (!user) {
      navigate('/');
    }
  }, [user, navigate]);

  // Auto-scroll to bottom
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Helper to save messages locally
  const saveMessages = (newMessages) => {
    setMessages(newMessages);
    localStorage.setItem("chat_history", JSON.stringify(newMessages));
  };

  const handleLogout = () => {
    localStorage.removeItem("vignan_user");
    navigate('/');
  };

  const clearChat = () => {
    if(confirm("Delete all chat history?")) {
      saveMessages([]);
      localStorage.removeItem("chat_history");
    }
  }

  // Send Message Logic
  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsgText = input;
    setInput(''); // Clear input immediately
    setLoading(true);

    // Add User Message
    const newMsg = { text: userMsgText, sender: 'user', timestamp: new Date().toISOString() };
    const updatedMessages = [...messages, newMsg];
    saveMessages(updatedMessages);

    try {
      // Determine Mode
      const mode = isWebSearch ? "general" : "university";

      // Call Python Backend
      // Ensure your backend is running at http://127.0.0.1:8000
      const res = await axios.post('http://127.0.0.1:8000/api/chat', {
        message: userMsgText,
        mode: mode
      });

      // Add Bot Response
      const botMsg = { text: res.data.response, sender: 'bot', timestamp: new Date().toISOString() };
      saveMessages([...updatedMessages, botMsg]);

    } catch (error) {
      console.error("API Error", error);
      const errorMsg = { 
        text: "⚠️ Server Error: Make sure backend is running (uvicorn main:app).", 
        sender: 'bot', 
        timestamp: new Date().toISOString() 
      };
      saveMessages([...updatedMessages, errorMsg]);
    }
    setLoading(false);
  };

  // If user is null (during redirect), show nothing to prevent flickering
  if (!user) return null;

  return (
    <div className="h-screen w-screen flex flex-col relative overflow-hidden bg-gray-900 text-white font-sans">
      <AnimatedBackground />
      
      {/* Header */}
      <header className="bg-gray-900/80 backdrop-blur-md p-4 flex justify-between items-center border-b border-gray-800 z-10 shadow-md">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center font-bold text-sm shadow-lg">
            VU
          </div>
          <div>
            <h1 className="font-bold text-md tracking-wide">Vignan Assistant</h1>
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${isWebSearch ? 'bg-green-400' : 'bg-blue-400'} animate-pulse`}></span>
              <p className="text-xs text-gray-400">
                {isWebSearch ? "Global Search Mode" : "University Database Mode"}
              </p>
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
            <div className="hidden md:flex flex-col items-end">
              <span className="text-sm font-medium text-gray-200">{user.name}</span>
              <span className="text-xs text-gray-500">{user.regNo}</span>
            </div>
            <button onClick={clearChat} title="Clear Chat" className="text-gray-500 hover:text-red-400 transition-colors">
               <BiTrash size={20}/>
            </button>
            <button onClick={handleLogout} title="Logout" className="text-gray-500 hover:text-white transition-colors">
               <BiLogOut size={24}/>
            </button>
        </div>
      </header>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 z-10 pb-40 scroll-smooth">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 opacity-50">
            <BsRobot size={50} className="mb-4"/>
            <p>Ask me anything about Vignan University...</p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`flex w-full ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex max-w-[85%] md:max-w-[70%] gap-3 ${msg.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
              
              {/* Avatar */}
              <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                msg.sender === 'user' ? 'bg-blue-600' : 'bg-purple-600'
              }`}>
                {msg.sender === 'user' ? <BsPersonCircle size={16}/> : <BsRobot size={16}/>}
              </div>

              {/* Bubble */}
              <div className={`p-4 rounded-2xl text-sm md:text-base shadow-md leading-relaxed ${
                msg.sender === 'user' 
                  ? 'bg-blue-600 text-white rounded-tr-none' 
                  : 'bg-gray-800 border border-gray-700 text-gray-200 rounded-tl-none'
              }`}>
                {msg.sender === 'bot' ? (
                    /* Markdown support for code blocks/lists */
                    <div className="prose prose-invert prose-sm max-w-none">
                      <ReactMarkdown>{msg.text}</ReactMarkdown>
                    </div>
                ) : (
                    msg.text
                )}
                <div className={`text-[10px] mt-2 opacity-50 ${msg.sender === 'user' ? 'text-right' : 'text-left'}`}>
                  {new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                </div>
              </div>

            </div>
          </div>
        ))}
        {loading && (
           <div className="flex justify-start w-full">
             <div className="bg-gray-800 px-4 py-2 rounded-full text-xs text-gray-400 animate-pulse ml-10">
               Generating response...
             </div>
           </div>
        )}
        <div ref={scrollRef} />
      </div>

      {/* Input Area */}
      <div className="absolute bottom-0 w-full p-4 z-20 bg-gradient-to-t from-gray-900 via-gray-900/90 to-transparent">
        <div className="max-w-4xl mx-auto bg-gray-800/60 backdrop-blur-xl border border-gray-700/50 rounded-3xl p-2 flex flex-col gap-2 shadow-2xl ring-1 ring-white/10">
            
            {/* Text Area */}
            <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                placeholder={isWebSearch ? "Ask Python to write code..." : "Ask about Exam Fees, Syllabus..."}
                className="w-full bg-transparent text-white resize-none outline-none p-3 min-h-[50px] max-h-[120px] placeholder-gray-500 text-sm md:text-base"
            />

            {/* Controls Bar */}
            <div className="flex justify-between items-center px-2 pb-1">
                
                <button 
                    onClick={() => setIsWebSearch(!isWebSearch)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-full text-xs md:text-sm font-medium transition-all duration-300 ${
                        isWebSearch 
                        ? 'bg-green-500/10 text-green-400 border border-green-500/30 hover:bg-green-500/20' 
                        : 'bg-blue-500/10 text-blue-400 border border-blue-500/30 hover:bg-blue-500/20'
                    }`}
                >
                    <BsGlobe size={14} />
                    {isWebSearch ? "Web Search ON" : "University Search"}
                </button>

                <button 
                    onClick={sendMessage}
                    disabled={loading || !input.trim()}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white p-3 rounded-full transition-all transform active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
                >
                    <BsSendFill size={18} />
                </button>
            </div>
        </div>
      </div>
    </div>
  );
}