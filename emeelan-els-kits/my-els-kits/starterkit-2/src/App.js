import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import QuestionPage from './pages/QuestionPage';

export default function App() {
    return (
        <div style={{ fontFamily: 'Arial, sans-serif', padding: '20px' }}>
            {/* Header */}
            <header style={{
                backgroundColor: '#fff',
                padding: '20px',
                borderRadius: '8px',
                marginBottom: '20px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
                <h1 style={{ margin: '0 0 15px 0', color: '#333' }}>
                    StarterKit-2 {/* Change me - Your app name */}
                </h1>
                <nav>
                    <Link 
                        to="/" 
                        style={{
                            color: '#007bff',
                            textDecoration: 'none',
                            marginRight: '20px',
                            padding: '8px 15px',
                            borderRadius: '4px',
                            backgroundColor: '#f8f9fa'
                        }}
                    >
                        🏠 Home {/* Change me - Home link text */}
                    </Link>
                    <Link 
                        to="/questions" 
                        style={{
                            color: '#007bff',
                            textDecoration: 'none',
                            padding: '8px 15px',
                            borderRadius: '4px',
                            backgroundColor: '#f8f9fa'
                        }}
                    >
                        ❓ Questions {/* Change me - Questions link text */}
                    </Link>
                </nav>
            </header>

            {/* Routes */}
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/questions" element={<QuestionPage />} />
            </Routes>
        </div>
    );
}