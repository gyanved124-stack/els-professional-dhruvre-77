let API_URL;

if (typeof process !== 'undefined' && process.env.REACT_APP_API_BASE_URL) {
    // Web environment with environment variables
    API_URL = process.env.REACT_APP_API_BASE_URL;
} else if (window.capacitor && window.capacitor.platform === 'android') {
    // Android app environment - use hardcoded URL
    API_URL = 'https://hphtechnology.in/qai';
} else {
    // Fallback for other environments
    API_URL = 'https://hphtechnology.in/qai';
}

console.log('🌐 API Configuration:');
console.log('   - API_URL:', API_URL);
console.log('   - Platform:', window.capacitor ? window.capacitor.platform : 'Web');
console.log('   - Environment:', typeof process !== 'undefined' ? 'React' : 'Capacitor');

export const generateQuestions = async (data) => {
    console.log('📤 Request Data:', data);
    console.log('🌐 Using API URL:', API_URL);
    
    if (!API_URL) {
        throw new Error('API URL not configured');
    }
    
    try {
        // Add timeout to fetch request
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout

        const response = await fetch(`${API_URL}/generate-and-refine`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ data }),
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        console.log('📊 Response Status:', response.status);
        console.log('📊 Response OK:', response.ok);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ API Error Response:', errorText);
            
            if (response.status === 404) {
                throw new Error('API endpoint not found. Please check if the server is running correctly.');
            }
            
            if (response.status === 500) {
                throw new Error('Server error. Please check if the AI model is properly configured on the server.');
            }
            
            throw new Error(`API Error (${response.status}): ${errorText.substring(0, 100)}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            console.error('❌ Non-JSON response:', text.substring(0, 200));
            throw new Error('API returned non-JSON response');
        }
        
        const rawResponse = await response.json();
        console.log('📥 Raw API Response:', rawResponse);
        
        // Check if response is an array
        if (!Array.isArray(rawResponse)) {
            console.error('❌ Response is not an array:', rawResponse);
            throw new Error('Invalid response format: expected array');
        }

        const processedQuestions = rawResponse.map((item, index) => {
            console.log(`🔄 Processing question ${index + 1}:`, item);
            
            // Extract final_question from the response structure
            const question = item.final_question || item;
            
            if (!question) {
                console.warn(`⚠️ No question data in item ${index + 1}`);
                return null;
            }
            
            // Handle different field names that might come from the AI
            const title = question.title_en || question.title || question.question;
            if (!title) {
                console.warn(`⚠️ No title in question ${index + 1}`);
                return null;
            }
            
            // Process options safely
            const options = [];
            const optionsData = question.options_en || question.options || [];
            
            for (let i = 0; i < 4; i++) {
                const optionData = optionsData[i];
                if (optionData) {
                    // Handle different option formats
                    const optionText = optionData.option || optionData.text || optionData;
                    options.push(optionText || `Option ${i + 1}`);
                } else {
                    options.push(`Option ${i + 1}`);
                    console.warn(`⚠️ Missing option ${i + 1}, using default`);
                }
            }

            const processedQuestion = {
                subject: question.category_type || question.subject || data.subject || 'Science',
                difficulty: question.difficulty_option || question.difficulty || data.difficulty || 'EASY', 
                className: data.class || '10',
                question: title,
                options,
                explanation: question.explination_description_en || question.explanation || question.explination || '',
                topic: question.topic || data.topic || '',
                isGenerated: true
            };

            console.log(`✅ Processed question ${index + 1}:`, processedQuestion);
            return processedQuestion;
        }).filter(q => q !== null);
        
        console.log('✅ Final processed questions:', processedQuestions);
        console.log(`📈 Generated ${processedQuestions.length} out of ${rawResponse.length} questions`);
        
        if (processedQuestions.length === 0) {
            throw new Error('No valid questions could be processed from API response');
        }
        
        return processedQuestions;
        
    } catch (error) {
        console.error('❌ API Error:', error);
        
        if (error.name === 'AbortError') {
            throw new Error('API request timed out. The AI model might be taking too long to generate questions.');
        }
        
        if (error.message.includes('NetworkError') || error.message.includes('Failed to fetch')) {
            throw new Error(`Cannot connect to API server at ${API_URL}. Please check:
1. Your internet connection
2. The server is running at ${API_URL}
3. Firewall settings allow connections to port 8002
4. Server is accessible from your network`);
        }
        
        throw new Error(error.message || 'Failed to generate questions');
    }
};

export const testAPIConnection = async () => {
    try {
        console.log('🧪 Testing API connection to:', API_URL);
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000);
        
        // Use a simpler GET request to test connectivity
        const response = await fetch(`${API_URL}/health`, {
            method: 'GET',
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        // Even a 404 response means the server is reachable
        console.log('✅ API Connection test successful - server responded with status:', response.status);
        return true;
        
    } catch (error) {
        console.error('❌ API Connection test failed:', error);
        
        if (error.name === 'AbortError') {
            console.error('🕒 Connection timed out - server may be offline or unreachable');
            return false;
        }
        
        if (error.message.includes('NetworkError') || error.message.includes('Failed to fetch')) {
            console.error('🌐 Network error - check internet connection and server accessibility');
            return false;
        }
        
        return false;
    }
};

// Function to get server status
export const getServerStatus = async () => {
    try {
        const response = await fetch(API_URL, {
            method: 'GET',
            signal: AbortSignal.timeout(5000)
        });
        
        return {
            online: true,
            status: response.status,
            statusText: response.statusText
        };
    } catch (error) {
        return {
            online: false,
            error: error.message
        };
    }
};