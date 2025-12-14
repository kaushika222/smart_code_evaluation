// TEST: Git should detect this

const codeInput = document.getElementById('code-input');
const languageSelect = document.getElementById('language');
const analyzeBtn = document.getElementById('analyze-btn');
const clearBtn = document.getElementById('clear-btn');
const exampleBtn = document.getElementById('example-btn');
const loadingDiv = document.getElementById('loading');
const resultsDiv = document.getElementById('results');
const welcomeDiv = document.getElementById('welcome-message');

// Example codes for each language
const exampleCodes = {
    python: `# Python Example - Calculate Fibonacci
def fibonacci(n):
    """Calculate Fibonacci sequence up to n terms."""
    sequence = []
    a, b = 0, 1
    
    for i in range(n):
        sequence.append(a)
        a, b = b, a + b
    
    return sequence

# Main execution
if __name__ == "__main__":
    terms = 10
    result = fibonacci(terms)
    print(f"First {terms} Fibonacci numbers:")
    for num in result:
        print(num, end=" ")`,
    
    c: `// C Example - Calculate Factorial
#include <stdio.h>

int factorial(int n) {
    // Calculate factorial recursively
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

int main() {
    int number = 5;
    int result = factorial(number);
    
    printf("Factorial of %d is: %d\\n", number, result);
    return 0;
}`,
    
    cpp: `// C++ Example - Simple Calculator
#include <iostream>
using namespace std;

class Calculator {
public:
    int add(int a, int b) {
        return a + b;
    }
    
    int subtract(int a, int b) {
        return a - b;
    }
    
    int multiply(int a, int b) {
        return a * b;
    }
    
    float divide(int a, int b) {
        if (b == 0) {
            cout << "Error: Division by zero!" << endl;
            return 0;
        }
        return static_cast<float>(a) / b;
    }
};

int main() {
    Calculator calc;
    int x = 10, y = 3;
    
    cout << "x = " << x << ", y = " << y << endl;
    cout << "x + y = " << calc.add(x, y) << endl;
    cout << "x - y = " << calc.subtract(x, y) << endl;
    cout << "x * y = " << calc.multiply(x, y) << endl;
    cout << "x / y = " << calc.divide(x, y) << endl;
    
    return 0;
}`
};

// Event Listeners
analyzeBtn.addEventListener('click', analyzeCode);
clearBtn.addEventListener('click', clearCode);
exampleBtn.addEventListener('click', loadExampleCode);

// Load example code based on selected language
function loadExampleCode() {
    const lang = languageSelect.value;
    codeInput.value = exampleCodes[lang] || '';
    codeInput.focus();
    
    // Show success message
    showToast('Example code loaded!', 'success');
}

// Clear the code editor
function clearCode() {
    codeInput.value = '';
    codeInput.focus();
    showToast('Code cleared!', 'info');
}

// Show toast notification
function showToast(message, type = 'info') {
    // Remove existing toasts
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    // Style the toast
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 24px;
        background: ${type === 'success' ? '#4CAF50' : 
                     type === 'error' ? '#f44336' : '#2196F3'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    // Remove toast after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Analyze the code
async function analyzeCode() {
    const code = codeInput.value.trim();
    const language = languageSelect.value;
    
    // Validate input
    if (!code) {
        showToast('Please enter some code first!', 'error');
        return;
    }
    
    if (code.length < 10) {
        showToast('Code seems too short. Please enter more code!', 'warning');
        return;
    }
    
    // Show loading
    loadingDiv.classList.remove('hidden');
    resultsDiv.classList.add('hidden');
    welcomeDiv.classList.add('hidden');
    
    try {
        // Send request to backend
        const response = await fetch('http://localhost:5000/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                code: code,
                language: language
            })
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Hide loading, show results
        loadingDiv.classList.add('hidden');
        resultsDiv.classList.remove('hidden');
        
        // Display results
        displayResults(data);
        
        // Save to history
        saveToHistory(data);
        
    } catch (error) {
        console.error('Error:', error);
        loadingDiv.classList.add('hidden');
        showToast(`Error: ${error.message}`, 'error');
        
        // Show fallback mock results for testing
        if (error.message.includes('fetch')) {
            showMockResults(code, language);
        }
    }
}

// Display results in the UI
function displayResults(data) {
    const resultsHTML = generateResultsHTML(data);
    resultsDiv.innerHTML = resultsHTML;
    
    // Add animation to result cards
    const cards = resultsDiv.querySelectorAll('.result-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
}

// Generate HTML for results
function generateResultsHTML(data) {
    return `
        <!-- Summary Card -->
        <div class="result-card card-summary">
            <h3>📋 Summary</h3>
            <p>${data.summary || 'Analysis complete!'}</p>
            <div class="stat-grid">
                <div class="stat-item">
                    <span class="stat-value">${data.score?.score || 0}/100</span>
                    <span class="stat-label">Score</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${data.skill_level?.toUpperCase() || 'N/A'}</span>
                    <span class="stat-label">Skill Level</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${data.language?.toUpperCase() || 'N/A'}</span>
                    <span class="stat-label">Language</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${data.mistakes?.length || 0}</span>
                    <span class="stat-label">Mistakes Found</span>
                </div>
            </div>
        </div>

        <!-- Statistics Card -->
        <div class="result-card card-stats">
            <h3>📊 Code Statistics</h3>
            ${generateStatsHTML(data.analysis)}
        </div>

        <!-- Mistakes Card -->
        <div class="result-card card-mistakes">
            <h3>⚠️ Mistakes Detected</h3>
            ${generateMistakesHTML(data.mistakes)}
        </div>

        <!-- Feedback Card -->
        <div class="result-card card-feedback">
            <h3>🎯 Personalized Feedback</h3>
            ${generateFeedbackHTML(data.detailed_feedback, data.positive_points)}
        </div>

        <!-- Learning Card -->
        <div class="result-card card-learning">
            <h3>📚 Learning Path</h3>
            ${generateLearningHTML(data.learning_path, data.next_steps)}
        </div>

        <!-- AI Detection Card -->
        ${data.ai_detection?.is_suspicious ? `
        <div class="result-card card-ai">
            <h3>🤖 AI Code Detection</h3>
            <p><strong>⚠️ Warning:</strong> Code shows patterns similar to AI-generated content.</p>
            <p><strong>Confidence:</strong> ${Math.round((data.ai_detection.confidence || 0) * 100)}%</p>
            <p><strong>Patterns detected:</strong> ${data.ai_detection.detected_patterns?.join(', ') || 'None'}</p>
            <div class="feedback-item">
                <strong>Recommendations:</strong>
                <ul>
                    ${data.ai_detection.recommendations?.map(rec => `<li>${rec}</li>`).join('') || ''}
                </ul>
            </div>
        </div>
        ` : ''}
    `;
}

// Generate statistics HTML
function generateStatsHTML(analysis) {
    if (!analysis) return '<p>No analysis data available.</p>';
    
    return `
        <div class="stat-grid">
            <div class="stat-item">
                <span class="stat-value">${analysis.total_lines || 0}</span>
                <span class="stat-label">Lines of Code</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">${analysis.loops || 0}</span>
                <span class="stat-label">Loops</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">${analysis.functions || 0}</span>
                <span class="stat-label">Functions</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">${analysis.complexity || 'O(1)'}</span>
                <span class="stat-label">Complexity</span>
            </div>
        </div>
    `;
}

// Generate mistakes HTML
function generateMistakesHTML(mistakes) {
    if (!mistakes || mistakes.length === 0) {
        return '<p class="success-message">✅ Great job! No beginner mistakes found.</p>';
    }
    
    let html = `<p>Found ${mistakes.length} issue(s) to improve:</p>`;
    
    mistakes.forEach((mistake, index) => {
        html += `
            <div class="mistake-item">
                <strong>${index + 1}. ${mistake.problem || 'Issue'}</strong>
                <p><em>Why it's bad:</em> ${mistake.why_bad || 'Needs improvement'}</p>
                <p><em>Solution:</em> ${mistake.solution || 'Fix this issue'}</p>
            </div>
        `;
    });
    
    return html;
}

// Generate feedback HTML
function generateFeedbackHTML(detailedFeedback, positivePoints) {
    let html = '';
    
    if (positivePoints && positivePoints.length > 0) {
        html += '<div class="feedback-item">';
        html += '<strong>✅ Things you did well:</strong>';
        html += '<ul>';
        positivePoints.forEach(point => {
            html += `<li>${point}</li>`;
        });
        html += '</ul>';
        html += '</div>';
    }
    
    if (detailedFeedback && detailedFeedback.length > 0) {
        html += '<div class="feedback-item">';
        html += '<strong>📝 Detailed feedback:</strong>';
        html += '<ul>';
        detailedFeedback.forEach(feedback => {
            html += `<li>${feedback}</li>`;
        });
        html += '</ul>';
        html += '</div>';
    }
    
    return html || '<p>No detailed feedback available.</p>';
}

// Generate learning path HTML
function generateLearningHTML(learningPath, nextSteps) {
    let html = '';
    
    if (learningPath && learningPath.length > 0) {
        html += '<div class="learning-item">';
        html += '<strong>🎓 Recommended topics to learn:</strong>';
        learningPath.forEach(topic => {
            html += `<p><strong>${topic.topic}</strong> (${topic.priority} Priority)</p>`;
            if (topic.resources) {
                html += '<ul>';
                topic.resources.slice(0, 2).forEach(resource => {
                    html += `<li>${resource}</li>`;
                });
                html += '</ul>';
            }
        });
        html += '</div>';
    }
    
    if (nextSteps && nextSteps.length > 0) {
        html += '<div class="learning-item">';
        html += '<strong>🚀 Next steps to improve:</strong>';
        html += '<ul>';
        nextSteps.forEach(step => {
            html += `<li>${step}</li>`;
        });
        html += '</ul>';
        html += '</div>';
    }
    
    return html || '<p>Keep practicing and writing code regularly!</p>';
}

// Save analysis to browser's local storage
function saveToHistory(data) {
    try {
        const history = JSON.parse(localStorage.getItem('codeHistory') || '[]');
        
        const historyItem = {
            id: Date.now(),
            timestamp: new Date().toISOString(),
            language: data.language,
            score: data.score?.score || 0,
            grade: data.score?.grade || 'N/A',
            summary: data.summary || '',
            codePreview: codeInput.value.substring(0, 100) + '...'
        };
        
        history.unshift(historyItem); // Add to beginning
        history.splice(10, 1); // Keep only last 10 items
        
        localStorage.setItem('codeHistory', JSON.stringify(history));
    } catch (error) {
        console.error('Error saving to history:', error);
    }
}

// Show mock results for testing (when backend is not available)
function showMockResults(code, language) {
    const mockData = {
        summary: "Mock analysis complete! (Backend not connected)",
        language: language,
        skill_level: "intermediate",
        score: { score: 75, grade: "C" },
        analysis: {
            total_lines: code.split('\n').length,
            loops: 2,
            functions: 1,
            complexity: "O(n)"
        },
        mistakes: [
            {
                problem: "Magic numbers detected",
                why_bad: "Hard-coded numbers make code hard to maintain",
                solution: "Use named constants instead"
            }
        ],
        detailed_feedback: ["Your code structure is good!", "Consider adding more comments"],
        positive_points: ["Good variable naming", "Proper indentation"],
        learning_path: [
            {
                topic: "Code Optimization",
                priority: "Medium",
                resources: ["Book: Clean Code", "Video: Python Best Practices"]
            }
        ],
        next_steps: ["Practice with more exercises", "Review data structures"]
    };
    
    displayResults(mockData);
    showToast('Showing mock results (backend not connected)', 'warning');
}

// Add CSS animations for toast
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .success-message {
        color: #4CAF50;
        font-weight: bold;
        padding: 10px;
        background: #f1f8e9;
        border-radius: 5px;
        border-left: 4px solid #4CAF50;
    }
`;
document.head.appendChild(style);

// Initialize
window.addEventListener('DOMContentLoaded', () => {
    // Try to load last used code
    const savedCode = localStorage.getItem('lastCode');
    if (savedCode) {
        codeInput.value = savedCode;
    }
    
    // Save code on input (with debounce)
    let saveTimeout;
    codeInput.addEventListener('input', () => {
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(() => {
            localStorage.setItem('lastCode', codeInput.value);
        }, 1000);
    });
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl+Enter to analyze
        if (e.ctrlKey && e.key === 'Enter') {
            e.preventDefault();
            analyzeCode();
        }
        
        // Ctrl+L to clear
        if (e.ctrlKey && e.key === 'l') {
            e.preventDefault();
            clearCode();
        }
        
        // Ctrl+E for example
        if (e.ctrlKey && e.key === 'e') {
            e.preventDefault();
            loadExampleCode();
        }
    });
});