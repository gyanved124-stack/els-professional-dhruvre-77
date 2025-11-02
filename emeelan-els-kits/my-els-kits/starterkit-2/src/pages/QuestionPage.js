import React, { useState } from 'react';
import QuestionCreator from '../components/QuestionCreator';

export default function QuestionPage() {
    const [questions, setQuestions] = useState([]);

    const addQuestion = (newQuestion) => {
        setQuestions([...questions, newQuestion]);
    };

    return (
        <div>
            <h2 style={{ color: '#333', marginBottom: '20px' }}>
                Create Your Questions {/* Change me - Page title */}
            </h2>

            {/* Question Form */}
            <QuestionCreator onAdd={addQuestion} />

            {/* Questions List */}
            <div style={{
                backgroundColor: '#fff',
                padding: '30px',
                borderRadius: '8px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                marginTop: '20px'
            }}>
                <h3 style={{ color: '#333', marginBottom: '20px' }}>
                    📋 Your Questions ({questions.length}) {/* Change me - List title */}
                </h3>

                {questions.length === 0 ? (
                    <p style={{ color: '#666', textAlign: 'center', padding: '20px' }}>
                        No questions yet. Create your first question above! {/* Change me - Empty message */}
                    </p>
                ) : (
                    questions.map((question, index) => (
                        <div key={index} style={{
                            border: '1px solid #ddd',
                            borderRadius: '6px',
                            padding: '20px',
                            marginBottom: '15px',
                            backgroundColor: '#f9f9f9'
                        }}>
                            <div style={{ 
                                marginBottom: '10px',
                                fontSize: '14px',
                                color: '#666'
                            }}>
                                <strong>{question.subject}</strong> • {question.difficulty} • Class {question.className}
                            </div>
                            
                            <h4 style={{ color: '#333', marginBottom: '15px' }}>
                                {question.question}
                            </h4>

                            <div style={{
                                display: 'grid',
                                gridTemplateColumns: '1fr 1fr',
                                gap: '10px'
                            }}>
                                {question.options.map((option, i) => (
                                    <div key={i} style={{
                                        padding: '10px',
                                        backgroundColor: '#fff',
                                        border: '1px solid #ddd',
                                        borderRadius: '4px',
                                        fontSize: '14px'
                                    }}>
                                        {String.fromCharCode(65 + i)}. {option}
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))
                )}
            </div>

            <div style={{
                marginTop: '20px',
                padding: '15px',
                backgroundColor: '#fff3cd',
                borderRadius: '6px',
                fontSize: '14px',
                color: '#856404'
            }}>
                💡 Tip: Questions are saved in memory. Refresh will clear them. {/* Change me - Info message */}
            </div>
        </div>
    );
}