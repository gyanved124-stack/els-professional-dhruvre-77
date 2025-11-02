import React, { useState } from 'react';
import { generateQuestions, testAPIConnection } from '../utils/api'; // Added testAPIConnection import

export default function AIQuestionGenerator({ onQuestionsGenerated }) {
    const [subject, setSubject] = useState('Science');
    const [difficulty, setDifficulty] = useState('EASY');
    const [className, setClassName] = useState('10');
    const [topic, setTopic] = useState('');
    const [count, setCount] = useState(3);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [status, setStatus] = useState(''); // Added status state

    const handleGenerate = async () => {
        if (!topic.trim()) {
            setError('Please enter a topic');
            return;
        }

        setLoading(true);
        setError('');
        setStatus('Testing connection to server...');

        try {
            // Test connection first
            const isConnected = await testAPIConnection();
            if (!isConnected) {
                setError('Cannot connect to API server. Please check:\n1. Your internet connection\n2. The server is running at http://202.38.182.170:8002\n3. Your device can access the server network');
                setStatus('');
                return;
            }

            setStatus('Generating questions...');

            const requestData = {
                subject: subject,
                difficulty: difficulty,
                class: className,
                question_type: 'SC',
                count: parseInt(count),
                topic: topic.trim()
            };

            console.log('Sending request:', requestData);

            const questions = await generateQuestions(requestData);
            console.log('Generated questions:', questions);

            if (!questions || questions.length === 0) {
                setError('No questions generated. Try again with a different topic.');
                setStatus('');
                return;
            }

            onQuestionsGenerated(questions);
            setTopic(''); // Reset topic after success
            setStatus('Questions generated successfully!');
            
        } catch (err) {
            console.error('Generate error:', err);
            
            if (err.message.includes('timed out')) {
                setError('Request timed out. The AI model might be taking too long or the server is busy.');
            } else if (err.message.includes('network') || err.message.includes('connection')) {
                setError('Network error. Please check your internet connection and try again.');
            } else {
                setError(err.message || 'Failed to generate questions');
            }
            
            setStatus('');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{
            backgroundColor: '#e8f5e8',
            border: '2px solid #28a745',
            borderRadius: '8px',
            padding: '20px',
            marginBottom: '20px'
        }}>
            <h3 style={{ color: '#155724', marginBottom: '20px' }}>
                🤖 AI Question Generator
            </h3>

            {/* Status Display - ADDED THIS SECTION */}
            {status && (
                <div style={{
                    backgroundColor: '#d1ecf1',
                    color: '#0c5460',
                    padding: '10px',
                    borderRadius: '4px',
                    marginBottom: '15px',
                    fontSize: '14px'
                }}>
                    ⏳ {status}
                </div>
            )}

            {/* Form Fields Grid */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
                gap: '15px',
                marginBottom: '15px'
            }}>
                <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#155724' }}>
                        Subject
                    </label>
                    <select 
                        value={subject}
                        onChange={e => setSubject(e.target.value)}
                        style={{ 
                            width: '100%',
                            padding: '8px', 
                            borderRadius: '4px', 
                            border: '1px solid #28a745'
                        }}
                    >
                        <option value="Science">Science</option>
                        <option value="Math">Math</option>
                        <option value="Computer">Computer</option>
                        <option value="English">English</option>
                        <option value="History">History</option>
                    </select>
                </div>

                <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#155724' }}>
                        Difficulty
                    </label>
                    <select 
                        value={difficulty}
                        onChange={e => setDifficulty(e.target.value)}
                        style={{ 
                            width: '100%',
                            padding: '8px', 
                            borderRadius: '4px', 
                            border: '1px solid #28a745'
                        }}
                    >
                        <option value="EASY">Easy</option>
                        <option value="MEDIUM">Medium</option>
                        <option value="HARD">Hard</option>
                        <option value="EXPERT">Expert</option>
                    </select>
                </div>

                <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#155724' }}>
                        Class
                    </label>
                    <select 
                        value={className}
                        onChange={e => setClassName(e.target.value)}
                        style={{ 
                            width: '100%',
                            padding: '8px', 
                            borderRadius: '4px', 
                            border: '1px solid #28a745'
                        }}
                    >
                        <option value="6">Class 6</option>
                        <option value="7">Class 7</option>
                        <option value="8">Class 8</option>
                        <option value="9">Class 9</option>
                        <option value="10">Class 10</option>
                        <option value="11">Class 11</option>
                        <option value="12">Class 12</option>
                    </select>
                </div>

                <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#155724' }}>
                        Questions
                    </label>
                    <select 
                        value={count}
                        onChange={e => setCount(e.target.value)}
                        style={{ 
                            width: '100%',
                            padding: '8px', 
                            borderRadius: '4px', 
                            border: '1px solid #28a745'
                        }}
                    >
                        <option value={1}>1 Question</option>
                        <option value={2}>2 Questions</option>
                        <option value={3}>3 Questions</option>
                        <option value={4}>4 Questions</option>
                        <option value={5}>5 Questions</option>
                    </select>
                </div>
            </div>

            {/* Topic Input */}
            <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold', color: '#155724' }}>
                    Topic
                </label>
                <input 
                    type="text"
                    value={topic}
                    onChange={e => setTopic(e.target.value)}
                    placeholder="Enter topic (e.g., Light, Photosynthesis, Fractions)"
                    style={{
                        width: '100%',
                        padding: '10px',
                        borderRadius: '4px',
                        border: '1px solid #28a745',
                        boxSizing: 'border-box'
                    }}
                />
            </div>

            {/* Error Display */}
            {error && (
                <div style={{
                    backgroundColor: '#f8d7da',
                    color: '#721c24',
                    padding: '10px',
                    borderRadius: '4px',
                    marginBottom: '15px',
                    fontSize: '14px'
                }}>
                    ⚠️ {error}
                </div>
            )}

            {/* Generate Button */}
            <button 
                onClick={handleGenerate}
                disabled={loading}
                style={{
                    backgroundColor: loading ? '#6c757d' : '#28a745',
                    color: 'white',
                    border: 'none',
                    padding: '12px 20px',
                    borderRadius: '4px',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    fontSize: '16px',
                    fontWeight: 'bold'
                }}
            >
                {loading ? '⏳ Generating...' : `🎯 Generate ${count} Questions`}
            </button>

            <p style={{ fontSize: '12px', color: '#155724', margin: '10px 0 0 0' }}>
                💡 Will generate {count} {difficulty.toLowerCase()} {subject.toLowerCase()} questions about "{topic}" for Class {className}
            </p>
        </div>
    );
}