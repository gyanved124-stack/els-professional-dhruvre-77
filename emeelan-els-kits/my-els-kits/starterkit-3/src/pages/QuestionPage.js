import React, { useState } from 'react';
import QuestionCreator from '../components/QuestionCreator';
import AIQuestionGenerator from '../components/AIQuestionGenerator';

export default function QuestionPage() {
    const [questions, setQuestions] = useState([]);
    const [showAI, setShowAI] = useState(true);

    const addQuestion = (q) => setQuestions(prev => [...prev, q]);
    const addAIQuestions = (qs) => setQuestions(prev => [...prev, ...qs]);

    return (
        <div>
            <h2 style={{ color: '#333', marginBottom: '20px' }}>
                🤖 Question Creator with AI {/* Change me - Page title */}
            </h2>

            {/* Toggle Buttons */}
            <div style={{ marginBottom: '20px' }}>
                <button
                    onClick={() => setShowAI(true)}
                    style={{
                        backgroundColor: showAI ? '#28a745' : '#f8f9fa',
                        color: showAI ? 'white' : '#28a745',
                        border: '1px solid #28a745',
                        padding: '8px 15px',
                        borderRadius: '4px',
                        marginRight: '10px',
                        cursor: 'pointer'
                    }}
                >
                    🤖 AI Mode {/* Change me - AI button */}
                </button>
                <button
                    onClick={() => setShowAI(false)}
                    style={{
                        backgroundColor: !showAI ? '#007bff' : '#f8f9fa',
                        color: !showAI ? 'white' : '#007bff',
                        border: '1px solid #007bff',
                        padding: '8px 15px',
                        borderRadius: '4px',
                        cursor: 'pointer'
                    }}
                >
                    ✏️ Manual {/* Change me - Manual button */}
                </button>
            </div>

            {/* Form */}
            {showAI ? 
                <AIQuestionGenerator onQuestionsGenerated={addAIQuestions} /> : 
                <QuestionCreator onAdd={addQuestion} />
            }

            {/* Questions List */}
            <div style={{
                backgroundColor: '#fff',
                padding: '20px',
                borderRadius: '8px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
                <h3 style={{ marginBottom: '15px' }}>
                    📋 Questions ({questions.length}) {/* Change me - List title */}
                </h3>

                {questions.length === 0 ? (
                    <p style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
                        No questions yet. Try the AI generator! {/* Change me - Empty message */}
                    </p>
                ) : (
                    questions.map((q, i) => (
                        <div key={i} style={{
                            border: '1px solid #ddd',
                            borderRadius: '4px',
                            padding: '15px',
                            marginBottom: '10px',
                            backgroundColor: q.isGenerated ? '#f0f8ff' : '#f9f9f9'
                        }}>
                            <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px' }}>
                                {q.subject} • {q.difficulty} • Class {q.className}
                                {q.isGenerated && <span style={{
                                    backgroundColor: '#28a745', 
                                    color: 'white', 
                                    padding: '2px 6px', 
                                    borderRadius: '3px',
                                    marginLeft: '10px',
                                    fontSize: '10px'
                                }}>🤖 AI</span>}
                            </div>
                            
                            <h4 style={{ marginBottom: '10px', color: '#333' }}>
                                {q.question}
                            </h4>

                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '5px' }}>
                                {q.options.map((opt, j) => (
                                    <div key={j} style={{
                                        padding: '8px',
                                        backgroundColor: '#fff',
                                        border: '1px solid #ddd',
                                        borderRadius: '3px',
                                        fontSize: '14px'
                                    }}>
                                        {String.fromCharCode(65 + j)}. {opt}
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}