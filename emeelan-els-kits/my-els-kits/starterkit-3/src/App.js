import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import QuestionPage from './pages/QuestionPage';

export default function App() {
    return (
        <div style={{ fontFamily: 'Arial, sans-serif', padding: '20px' }}>
            {/* AI Banner */}
            <div style={{
                background: '#e8f5e8',
                padding: '15px',
                borderRadius: '8px',
                marginBottom: '20px',
                border: '2px solid #28a745'
            }}>
                <strong style={{ color: '#155724' }}>
                    🤖 StarterKit-3 - Now with AI Question Generator! {/* Change me - Banner text */}
                </strong>
                <div style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
                    Generate questions automatically using AI technology {/* Change me - Description */}
                </div>
            </div>

            {/* Navigation */}
            <nav style={{ marginBottom: '20px' }}>
                <Link to="/" style={{
                    color: '#007bff',
                    textDecoration: 'none',
                    marginRight: '20px',
                    padding: '8px 15px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '4px'
                }}>
                    🏠 Home {/* Change me - Home link */}
                </Link>
                <Link to="/questions" style={{
                    color: '#007bff',
                    textDecoration: 'none',
                    padding: '8px 15px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '4px'
                }}>
                    🤖 AI Questions {/* Change me - Questions link */}
                </Link>
            </nav>

            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/questions" element={<QuestionPage />} />
            </Routes>
        </div>
    );
}   