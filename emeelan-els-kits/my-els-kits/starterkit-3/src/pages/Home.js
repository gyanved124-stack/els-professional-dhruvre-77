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
                🤖 Welcome to AI Question Creator! {/* Change me - Main title */}
            </h2>
            
            <p style={{ color: '#666', fontSize: '18px', marginBottom: '30px' }}>
                Generate quiz questions automatically using AI or create them manually. Perfect for teachers! {/* Change me - Description */}
            </p>

            {/* Features */}
            <div style={{ display: 'flex', justifyContent: 'center', gap: '30px', marginBottom: '30px' }}>
                <div style={{ backgroundColor: '#e8f5e8', padding: '20px', borderRadius: '8px', width: '200px' }}>
                    <h3 style={{ color: '#28a745', margin: '0 0 10px 0' }}>
                        🤖 AI Powered {/* Change me - Feature 1 */}
                    </h3>
                    <p style={{ color: '#666', margin: '0', fontSize: '14px' }}>
                        Enter a topic and get questions instantly {/* Change me - Feature 1 description */}
                    </p>
                </div>

                <div style={{ backgroundColor: '#f8f9fa', padding: '20px', borderRadius: '8px', width: '200px' }}>
                    <h3 style={{ color: '#333', margin: '0 0 10px 0' }}>
                        ✏️ Manual Mode {/* Change me - Feature 2 */}
                    </h3>
                    <p style={{ color: '#666', margin: '0', fontSize: '14px' }}>
                        Create custom questions your way {/* Change me - Feature 2 description */}
                    </p>
                </div>
            </div>

            <button style={{
                backgroundColor: '#28a745',
                color: 'white',
                border: 'none',
                padding: '15px 30px',
                borderRadius: '8px',
                fontSize: '16px',
                cursor: 'pointer'
            }}>
                🚀 Try AI Generator {/* Change me - Button text */}
            </button>

            {/* Quick Guide */}
            <div style={{
                marginTop: '30px',
                padding: '20px',
                backgroundColor: '#f0f8ff',
                borderRadius: '8px',
                textAlign: 'left'
            }}>
                <h4 style={{ color: '#333', marginBottom: '15px' }}>
                    📋 Quick Start Guide: {/* Change me - Guide title */}
                </h4>
                <ol style={{ color: '#666', margin: '0', paddingLeft: '20px' }}>
                    <li>Click "AI Questions" in the navigation {/* Change me - Step 1 */}</li>
                    <li>Enter a topic (like "Photosynthesis") {/* Change me - Step 2 */}</li>
                    <li>Click "Generate AI Questions" {/* Change me - Step 3 */}</li>
                    <li>Review and use your questions! {/* Change me - Step 4 */}</li>
                </ol>
            </div>

            <div style={{
                marginTop: '20px',
                fontSize: '12px',
                color: '#666'
            }}>
                💡 Look for "Change me" in code to customize everything! {/* Change me - Tip */}
            </div>
        </div>
    );
}