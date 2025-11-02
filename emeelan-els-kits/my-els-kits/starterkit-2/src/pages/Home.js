import React from 'react';

export default function Home() {
    return (
        <div style={{
            backgroundColor: '#fff',
            padding: '40px',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            textAlign: 'center'
        }}>
            <h2 style={{ color: '#333', marginBottom: '20px' }}>
                Welcome to Question Creator! {/* Change me - Main title */}
            </h2>
            
            <p style={{ color: '#666', fontSize: '18px', marginBottom: '30px' }}>
                Create and manage quiz questions easily. Perfect for teachers and students! {/* Change me - Description */}
            </p>

            <div style={{
                display: 'flex',
                justifyContent: 'center',
                gap: '20px',
                marginBottom: '40px'
            }}>
                <div style={{
                    backgroundColor: '#f8f9fa',
                    padding: '20px',
                    borderRadius: '8px',
                    width: '200px'
                }}>
                    <h3 style={{ color: '#333', margin: '0 0 10px 0' }}>
                        ⚡ Easy to Use {/* Change me - Feature 1 */}
                    </h3>
                    <p style={{ color: '#666', margin: '0', fontSize: '14px' }}>
                        Simple form to create questions {/* Change me - Feature 1 description */}
                    </p>
                </div>

                <div style={{
                    backgroundColor: '#f8f9fa',
                    padding: '20px',
                    borderRadius: '8px',
                    width: '200px'
                }}>
                    <h3 style={{ color: '#333', margin: '0 0 10px 0' }}>
                        🎯 Organized {/* Change me - Feature 2 */}
                    </h3>
                    <p style={{ color: '#666', margin: '0', fontSize: '14px' }}>
                        Sort by subject and difficulty {/* Change me - Feature 2 description */}
                    </p>
                </div>
            </div>

            <button style={{
                backgroundColor: '#007bff',
                color: 'white',
                border: 'none',
                padding: '15px 30px',
                borderRadius: '8px',
                fontSize: '16px',
                cursor: 'pointer'
            }}>
                🚀 Get Started {/* Change me - Button text */}
            </button>

            <div style={{
                marginTop: '30px',
                padding: '20px',
                backgroundColor: '#e8f4fd',
                borderRadius: '8px',
                fontSize: '14px',
                color: '#0c5460'
            }}>
                💡 Look for "Change me" comments in the code to customize everything! {/* Change me - Tip message */}
            </div>
        </div>
    );
}