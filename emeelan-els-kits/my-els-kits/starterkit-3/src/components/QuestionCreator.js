import React, { useState } from 'react';

export default function QuestionCreator({ onAdd }) {
    const [subject, setSubject] = useState('Science');
    const [difficulty, setDifficulty] = useState('EASY');
    const [className, setClassName] = useState('10');
    const [question, setQuestion] = useState('');
    const [options, setOptions] = useState(['', '', '', '']);

    const setOptionAt = (index, value) => {
        const newOptions = [...options];
        newOptions[index] = value;
        setOptions(newOptions);
    };

    const handleAdd = () => {
        if (!question.trim()) {
            alert('Please enter the question');
            return;
        }
        if (options.some(opt => !opt.trim())) {
            alert('Please fill all 4 options');
            return;
        }

        const newQuestion = { subject, difficulty, className, question, options };
        onAdd(newQuestion);

        // Reset form
        setQuestion('');
        setOptions(['', '', '', '']);
    };

    return (
        <div style={{
            backgroundColor: '#fff',
            padding: '30px',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
            <h3 style={{ color: '#333', marginBottom: '20px' }}>
                ➕ Add New Question {/* Change me - Form title */}
            </h3>

            {/* Dropdowns */}
            <div style={{
                display: 'flex',
                gap: '15px',
                marginBottom: '20px',
                flexWrap: 'wrap'
            }}>
                <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                        Subject {/* Change me - Add more subjects */}
                    </label>
                    <select 
                        value={subject} 
                        onChange={e => setSubject(e.target.value)}
                        style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                    >
                        <option>Science</option>
                        <option>Math</option>
                        <option>Computer</option>
                        <option>English</option> {/* Change me - Add your subjects */}
                    </select>
                </div>

                <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                        Difficulty
                    </label>
                    <select 
                        value={difficulty} 
                        onChange={e => setDifficulty(e.target.value)}
                        style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                    >
                        <option value="EASY">Easy</option>
                        <option value="MEDIUM">Medium</option>
                        <option value="HARD">Hard</option>
                    </select>
                </div>

                <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                        Class {/* Change me - Update class range */}
                    </label>
                    <select 
                        value={className} 
                        onChange={e => setClassName(e.target.value)}
                        style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                    >
                        <option>6</option>
                        <option>7</option>
                        <option>8</option>
                        <option>9</option>
                        <option>10</option>
                    </select>
                </div>
            </div>

            {/* Question Input */}
            <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
                    Question Text {/* Change me - Update label */}
                </label>
                <textarea 
                    value={question}
                    onChange={e => setQuestion(e.target.value)}
                    placeholder="Enter your question here..."
                    rows={3}
                    style={{
                        width: '100%',
                        padding: '12px',
                        borderRadius: '4px',
                        border: '1px solid #ddd',
                        fontSize: '14px',
                        boxSizing: 'border-box'
                    }}
                />
            </div>

            {/* Options */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '15px',
                marginBottom: '20px'
            }}>
                {options.map((option, index) => (
                    <div key={index}>
                        <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                            Option {index + 1} {/* Change me - Customize option labels */}
                        </label>
                        <input 
                            type="text"
                            value={option}
                            onChange={e => setOptionAt(index, e.target.value)}
                            placeholder={`Option ${index + 1}...`}
                            style={{
                                width: '100%',
                                padding: '10px',
                                borderRadius: '4px',
                                border: '1px solid #ddd',
                                boxSizing: 'border-box'
                            }}
                        />
                    </div>
                ))}
            </div>

            {/* Add Button */}
            <button 
                onClick={handleAdd}
                style={{
                    backgroundColor: '#28a745',
                    color: 'white',
                    border: 'none',
                    padding: '12px 25px',
                    borderRadius: '6px',
                    fontSize: '16px',
                    cursor: 'pointer',
                    fontWeight: 'bold'
                }}
            >
                ✅ Add Question {/* Change me - Button text */}
            </button>

            <p style={{ marginTop: '15px', fontSize: '12px', color: '#666' }}>
                💡 Look for "Change me" comments to customize this form {/* Change me - Help text */}
            </p>
        </div>
    );
}