import React from 'react';

// App component renders a professional welcome page
export default function App() {
    return (
        <div style={{
            fontFamily: 'Arial, sans-serif',
            maxWidth: '600px',
            margin: '0 auto',
            padding: '20px',
            backgroundColor: '#f9f9f9',
            minHeight: '100vh'
        }}>
            {/* Header */}
            <div style={{
                backgroundColor: '#ffffff',
                padding: '20px',
                borderRadius: '8px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                marginBottom: '20px',
                textAlign: 'center'
            }}>
                <h1 style={{margin: '0', color: '#333', fontSize: '28px'}}>
                    StarterKit-1
                </h1>
                <p style={{margin: '10px 0 0 0', color: '#666'}}>
                    React + Capacitor Mobile App Template
                </p>
            </div>

            {/* Welcome Section */}
            <div style={{
                backgroundColor: '#ffffff',
                padding: '30px',
                borderRadius: '8px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                marginBottom: '20px'
            }}>
                <h2 style={{color: '#333', marginTop: '0'}}>
                    Welcome to Your Mobile App! <span style={{color: '#007bff'}}>Change me</span>
                </h2>
                <p style={{color: '#666', lineHeight: '1.6'}}>
                    This is a professional starter template ready for mobile deployment. 
                    Edit this text by finding <strong>"Change me"</strong> in your code.
                </p>
            </div>

            {/* Instructions */}
            <div style={{
                backgroundColor: '#ffffff',
                padding: '30px',
                borderRadius: '8px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
                <h3 style={{color: '#333', marginTop: '0'}}>
                    📱 How to Create Your Android APK
                </h3>
                
                <div style={{marginBottom: '20px'}}>
                    <h4 style={{color: '#555', margin: '15px 0 10px 0'}}>Steps:</h4>
                    <ol style={{color: '#666', lineHeight: '1.8', paddingLeft: '20px'}}>
                        <li><code style={{backgroundColor: '#f1f1f1', padding: '2px 4px', borderRadius: '3px'}}>npm install</code></li>
                        <li><code style={{backgroundColor: '#f1f1f1', padding: '2px 4px', borderRadius: '3px'}}>npm run cap:add:android</code> (only once)</li>
                        <li><code style={{backgroundColor: '#f1f1f1', padding: '2px 4px', borderRadius: '3px'}}>npm run cap:sync</code></li>
                        <li><code style={{backgroundColor: '#f1f1f1', padding: '2px 4px', borderRadius: '3px'}}>cd android && ./gradlew assembleDebug</code></li>
                    </ol>
                </div>

                <div style={{
                    backgroundColor: '#e8f4fd',
                    padding: '15px',
                    borderRadius: '5px',
                    border: '1px solid #bee5eb'
                }}>
                    <strong style={{color: '#0c5460'}}>📁 Find Your APK:</strong>
                    <p style={{margin: '5px 0 0 0', color: '#0c5460', fontSize: '14px'}}>
                        StarterKitSystem/dist
                        <br/>
                        or
                        <br/>
                        StarterKitSystem/emeelan-starterkit-app/android/app/build/outputs/apk/debug/
                    </p>
                </div>

                <div style={{marginTop: '20px', textAlign: 'center'}}>
                    <p style={{color: '#666', fontSize: '14px', margin: '0'}}>
                        <span style={{color: '#28a745'}}>✓</span> Requires Android SDK & Gradle installed
                    </p>
                </div>
            </div>
        </div>
    );
}