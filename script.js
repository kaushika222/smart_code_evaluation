// frontend/script.js

// Global variables
let currentTopic = null;
let currentQuestion = null;
let allQuestions = [];
let currentAnalysis = null;
const API_BASE_URL = 'http://localhost:5000';

// DOM Elements
const elements = {
    topicsContainer: document.getElementById('topics-container'),
    questionsContainer: document.getElementById('questions-container'),
    questionInfo: document.getElementById('question-info'),
    conceptsTags: document.getElementById('concepts-tags'),
    codeInput: document.getElementById('code-input'),
    languageSelect: document.getElementById('language-select'),
    lineCount: document.getElementById('line-count'),
    charCount: document.getElementById('char-count'),
    analyzeBtn: document.getElementById('analyze-btn'),
    resetBtn: document.getElementById('reset-btn'),
    exampleBtn: document.getElementById('example-btn'),
    tryAgainBtn: document.getElementById('try-again-btn'),
    nextQuestionBtn: document.getElementById('next-question-btn'),
    viewHistoryBtn: document.getElementById('view-history-btn'),
    backToResults: document.getElementById('back-to-results'),
    difficultyFilter: document.getElementById('difficulty-filter'),
    questionSearch: document.getElementById('question-search'),
    welcomeSection: document.getElementById('welcome-section'),
    loadingSection: document.getElementById('loading-section'),
    resultsSection: document.getElementById('results-section'),
    historySection: document.getElementById('history-section'),
    gradeScore: document.getElementById('grade-score'),
    gradeLetter: document.getElementById('grade-letter'),
    gradeStatus: document.getElementById('grade-status'),
    scoresGrid: document.getElementById('scores-grid'),
    conceptsStatus: document.getElementById('concepts-status'),
    feedbackList: document.getElementById('feedback-list'),
    suggestionsList: document.getElementById('suggestions-list'),
    historyList: document.getElementById('history-list')
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Smart Code Evaluator Initializing...');
    
    // Load topics and questions
    loadTopicsAndQuestions();
    
    // Setup event listeners
    setupEventListeners();
    
    // Setup code editor monitoring
    setupCodeEditor();
    
    // Test API connection
    testAPIConnection();
});

// Load topics and questions from backend
async function loadTopicsAndQuestions() {
    try {
        showLoading('topics');
        
        const response = await fetch(`${API_BASE_URL}/questions`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Store all questions for filtering
        allQuestions = [];
        for (const [topic, questions] of Object.entries(data)) {
            allQuestions.push(...questions.map(q => ({...q, topic})));
        }
        
        // Display topics
        displayTopics(data);
        
        // Display first topic's questions by default
        const firstTopic = Object.keys(data)[0];
        if (firstTopic) {
            selectTopic(firstTopic, data[firstTopic]);
        }
        
        hideLoading('topics');
    } catch (error) {
        console.error('Error loading questions:', error);
        showError('Failed to load questions. Please check if the backend server is running.');
        
        // Fallback: Use sample data
        useFallbackData();
    }
}

// Display topics in the UI
function displayTopics(topicsData) {
    elements.topicsContainer.innerHTML = '';
    
    const topics = Object.keys(topicsData);
    
    topics.forEach(topic => {
        const topicCard = document.createElement('div');
        topicCard.className = 'topic-card';
        topicCard.dataset.topic = topic;
        
        const count = topicsData[topic].length;
        const topicName = formatTopicName(topic);
        const icon = getTopicIcon(topic);
        
        topicCard.innerHTML = `
            <div class="topic-icon">${icon}</div>
            <div class="topic-name">${topicName}</div>
            <div class="topic-count">${count} questions</div>
        `;
        
        topicCard.addEventListener('click', () => {
            selectTopic(topic, topicsData[topic]);
        });
        
        elements.topicsContainer.appendChild(topicCard);
    });
}

// Select a topic and display its questions
function selectTopic(topic, questions) {
    // Update active topic card
    document.querySelectorAll('.topic-card').forEach(card => {
        card.classList.remove('active');
        if (card.dataset.topic === topic) {
            card.classList.add('active');
        }
    });
    
    currentTopic = topic;
    
    // Display questions for this topic
    displayQuestions(questions);
    
    // Reset current question
    currentQuestion = null;
    clearQuestionInfo();
    clearCodeEditor();
    
    // Show welcome section if no results are shown
    if (!currentAnalysis) {
        showWelcomeSection();
    }
}

// Display questions in the UI
function displayQuestions(questions) {
    elements.questionsContainer.innerHTML = '';
    
    if (!questions || questions.length === 0) {
        elements.questionsContainer.innerHTML = `
            <div class="no-questions">
                <i class="fas fa-exclamation-circle"></i>
                <p>No questions available for this topic</p>
            </div>
        `;
        return;
    }
    
    questions.forEach(question => {
        const questionItem = document.createElement('div');
        questionItem.className = 'question-item';
        questionItem.dataset.id = question.id;
        
        const difficultyClass = `difficulty-${question.difficulty}`;
        
        questionItem.innerHTML = `
            <div class="question-header">
                <span class="question-id">Q${question.id}</span>
                <span class="difficulty-badge ${difficultyClass}">${question.difficulty}</span>
            </div>
            <div class="question-text">${question.question}</div>
            <div class="concepts">
                ${question.concepts.map(concept => 
                    `<span class="concept-tag">${concept}</span>`
                ).join('')}
            </div>
        `;
        
        questionItem.addEventListener('click', () => {
            selectQuestion(question);
        });
        
        elements.questionsContainer.appendChild(questionItem);
    });
    
    // Apply filters if any
    applyFilters();
}

// Select a question
function selectQuestion(question) {
    // Update active question item
    document.querySelectorAll('.question-item').forEach(item => {
        item.classList.remove('active');
        if (parseInt(item.dataset.id) === question.id) {
            item.classList.add('active');
        }
    });
    
    currentQuestion = question;
    displayQuestionInfo(question);
    
    // Clear previous analysis results
    clearResults();
    showWelcomeSection();
    
    // Load example code for this question
    loadExampleCode(question);
}

// Display selected question info
function displayQuestionInfo(question) {
    elements.questionInfo.innerHTML = '';
    
    const questionInfo = document.createElement('div');
    questionInfo.innerHTML = `
        <div class="question-header">
            <span class="question-id">Q${question.id}</span>
            <span class="difficulty-badge difficulty-${question.difficulty}">
                ${question.difficulty}
            </span>
        </div>
        <div class="question-text">${question.question}</div>
        <div class="concepts-tags">
            ${question.concepts.map(concept => 
                `<span class="concept-tag-large">${concept}</span>`
            ).join('')}
        </div>
    `;
    
    elements.questionInfo.appendChild(questionInfo);
}

// Clear question info
function clearQuestionInfo() {
    elements.questionInfo.innerHTML = `
        <div class="question-header">
            <span class="question-id">Q#</span>
            <span class="question-text">Select a question to start</span>
        </div>
        <div class="concepts-tags" id="concepts-tags">
            <!-- Concepts will appear here -->
        </div>
    `;
}

// Setup event listeners
function setupEventListeners() {
    // Analyze button
    elements.analyzeBtn.addEventListener('click', analyzeCode);
    
    // Reset button
    elements.resetBtn.addEventListener('click', clearCodeEditor);
    
    // Example button
    elements.exampleBtn.addEventListener('click', () => {
        if (currentQuestion) {
            loadExampleCode(currentQuestion);
        } else {
            showError('Please select a question first');
        }
    });
    
    // Try again button
    elements.tryAgainBtn.addEventListener('click', () => {
        clearResults();
        showWelcomeSection();
    });
    
    // Next question button
    elements.nextQuestionBtn.addEventListener('click', selectNextQuestion);
    
    // View history button
    elements.viewHistoryBtn.addEventListener('click', showHistory);
    
    // Back to results button
    elements.backToResults.addEventListener('click', () => {
        showResultsSection();
    });
    
    // Filter and search
    elements.difficultyFilter.addEventListener('change', applyFilters);
    elements.questionSearch.addEventListener('input', applyFilters);
    
    // Language selector
    elements.languageSelect.addEventListener('change', () => {
        if (currentQuestion) {
            loadExampleCode(currentQuestion);
        }
    });
}

// Setup code editor monitoring
function setupCodeEditor() {
    elements.codeInput.addEventListener('input', updateEditorStats);
    updateEditorStats();
}

// Update editor statistics (line count, char count)
function updateEditorStats() {
    const code = elements.codeInput.value;
    const lines = code.split('\n').length;
    const chars = code.length;
    
    elements.lineCount.textContent = `Lines: ${lines}`;
    elements.charCount.textContent = `Chars: ${chars}`;
}

// Clear code editor
function clearCodeEditor() {
    elements.codeInput.value = '';
    updateEditorStats();
    
    if (currentQuestion) {
        loadExampleCode(currentQuestion);
    }
}

// Load example code for current question
function loadExampleCode(question) {
    const language = elements.languageSelect.value;
    
    // Simple example generation based on question
    let exampleCode = '';
    
    if (language === 'python') {
        exampleCode = generatePythonExample(question);
    } else if (language === 'c') {
        exampleCode = generateCExample(question);
    } else if (language === 'cpp') {
        exampleCode = generateCppExample(question);
    }
    
    elements.codeInput.value = exampleCode;
    updateEditorStats();
}

// Generate Python example code
function generatePythonExample(question) {
    const concepts = question.concepts;
    
    if (concepts.includes('for')) {
        if (question.id === 1) {
            return `# Print numbers from 1 to 10
for i in range(1, 11):
    print(i)`;
        } else if (concepts.includes('if')) {
            return `# Print even numbers between 1 and 50
for number in range(1, 51):
    if number % 2 == 0:
        print(number)`;
        }
    }
    
    if (concepts.includes('while')) {
        return `# Print numbers from 1 to N using while loop
n = 10
counter = 1

while counter <= n:
    print(counter)
    counter += 1`;
    }
    
    if (concepts.includes('if') && concepts.includes('else')) {
        return `# Check if number is even or odd
number = 7

if number % 2 == 0:
    print(f"{number} is even")
else:
    print(f"{number} is odd")`;
    }
    
    // Default example
    return `# Solution for: ${question.question}
# Write your code here

# Hint: Use ${concepts.join(', ')} concepts`;
}

// Generate C example code
function generateCExample(question) {
    return `// C solution for: ${question.question}
#include <stdio.h>

int main() {
    // Write your solution here
    
    return 0;
}`;
}

// Generate C++ example code
function generateCppExample(question) {
    return `// C++ solution for: ${question.question}
#include <iostream>
using namespace std;

int main() {
    // Write your solution here
    
    return 0;
}`;
}

// Apply filters to questions
function applyFilters() {
    const difficulty = elements.difficultyFilter.value;
    const searchTerm = elements.questionSearch.value.toLowerCase();
    
    const questions = Array.from(elements.questionsContainer.children);
    
    questions.forEach(questionItem => {
        if (!(questionItem instanceof HTMLElement)) return;
        
        const questionText = questionItem.querySelector('.question-text').textContent.toLowerCase();
        const difficultyText = questionItem.querySelector('.difficulty-badge').textContent.toLowerCase();
        
        const matchesDifficulty = difficulty === 'all' || difficultyText === difficulty;
        const matchesSearch = !searchTerm || questionText.includes(searchTerm);
        
        questionItem.style.display = matchesDifficulty && matchesSearch ? 'block' : 'none';
    });
}

// Analyze the code
async function analyzeCode() {
    const code = elements.codeInput.value.trim();
    const language = elements.languageSelect.value;
    
    if (!code) {
        showError('Please write some code first');
        return;
    }
    
    if (!currentQuestion) {
        showError('Please select a question first');
        return;
    }
    
    // Show loading state
    showLoadingSection();
    
    try {
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                code: code,
                question_id: currentQuestion.id,
                language: language
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            currentAnalysis = result.analysis;
            displayAnalysisResults(result.analysis);
            showResultsSection();
        } else {
            throw new Error(result.error || 'Analysis failed');
        }
        
    } catch (error) {
        console.error('Error analyzing code:', error);
        showError(`Analysis failed: ${error.message}`);
        showWelcomeSection();
    }
}

// Display analysis results
function displayAnalysisResults(analysis) {
    // Display grade
    elements.gradeScore.textContent = `${analysis.scores.total}/100`;
    elements.gradeLetter.textContent = analysis.grade;
    elements.gradeStatus.textContent = analysis.passed ? '✅ PASSED' : '❌ FAILED';
    
    // Display score breakdown
    displayScoreBreakdown(analysis.scores);
    
    // Display concepts analysis
    displayConceptsAnalysis(analysis.basic_analysis.concepts_analysis);
    
    // Display feedback
    displayFeedback(analysis.feedback);
    
    // Display suggestions
    displaySuggestions(analysis.suggestions);
}

// Display score breakdown
function displayScoreBreakdown(scores) {
    elements.scoresGrid.innerHTML = '';
    
    const scoreItems = [
        { label: 'Syntax', value: scores.syntax, max: 25 },
        { label: 'Requirements', value: scores.requirements, max: 25 },
        { label: 'Structure', value: scores.structure, max: 20 },
        { label: 'Best Practices', value: scores.best_practices, max: 20 },
        { label: 'Logic', value: scores.logic, max: 10 },
    ];
    
    scoreItems.forEach(item => {
        const scoreItem = document.createElement('div');
        scoreItem.className = 'score-item';
        
        const percentage = Math.round((item.value / item.max) * 100);
        
        scoreItem.innerHTML = `
            <div class="score-label">${item.label}</div>
            <div class="score-value">${item.value}/${item.max}</div>
        `;
        
        elements.scoresGrid.appendChild(scoreItem);
    });
}

// Display concepts analysis
function displayConceptsAnalysis(conceptsAnalysis) {
    elements.conceptsStatus.innerHTML = '';
    
    const detected = conceptsAnalysis.detected_concepts || [];
    const required = conceptsAnalysis.required_concepts || [];
    
    required.forEach(concept => {
        const conceptStatus = document.createElement('div');
        conceptStatus.className = `concept-status ${detected.includes(concept) ? 'concept-present' : 'concept-missing'}`;
        
        const icon = detected.includes(concept) ? '✅' : '❌';
        const text = detected.includes(concept) ? 'Present' : 'Missing';
        
        conceptStatus.innerHTML = `
            <span>${icon}</span>
            <span>${concept}: ${text}</span>
        `;
        
        elements.conceptsStatus.appendChild(conceptStatus);
    });
}

// Display feedback
function displayFeedback(feedback) {
    elements.feedbackList.innerHTML = '';
    
    if (!feedback || feedback.length === 0) {
        elements.feedbackList.innerHTML = `
            <div class="feedback-item">
                <i class="fas fa-check-circle"></i>
                <div class="feedback-content">
                    <h5>No Issues Found</h5>
                    <p>Your code looks good! No specific feedback needed.</p>
                </div>
            </div>
        `;
        return;
    }
    
    feedback.forEach(item => {
        const feedbackItem = document.createElement('div');
        feedbackItem.className = 'feedback-item';
        
        const icon = item.urgent ? 'fas fa-exclamation-triangle' : 'fas fa-info-circle';
        const color = item.urgent ? '#dc3545' : '#4a6cf7';
        
        feedbackItem.innerHTML = `
            <i class="${icon}" style="color: ${color}"></i>
            <div class="feedback-content">
                <h5>${item.category.toUpperCase()}: ${item.message}</h5>
                <p>${item.details}</p>
            </div>
        `;
        
        elements.feedbackList.appendChild(feedbackItem);
    });
}

// Display suggestions
function displaySuggestions(suggestions) {
    elements.suggestionsList.innerHTML = '';
    
    if (!suggestions || suggestions.length === 0) {
        return;
    }
    
    suggestions.forEach((suggestion, index) => {
        const suggestionItem = document.createElement('div');
        suggestionItem.className = 'suggestion-item';
        
        suggestionItem.innerHTML = `
            <i class="fas fa-lightbulb"></i>
            <div class="suggestion-content">
                <h5>Suggestion ${index + 1}</h5>
                <p>${suggestion}</p>
            </div>
        `;
        
        elements.suggestionsList.appendChild(suggestionItem);
    });
}

// Select next question
function selectNextQuestion() {
    if (!currentTopic || !allQuestions.length) return;
    
    const topicQuestions = allQuestions.filter(q => q.topic === currentTopic);
    
    if (!currentQuestion) {
        if (topicQuestions.length > 0) {
            selectQuestion(topicQuestions[0]);
        }
        return;
    }
    
    const currentIndex = topicQuestions.findIndex(q => q.id === currentQuestion.id);
    const nextIndex = (currentIndex + 1) % topicQuestions.length;
    
    selectQuestion(topicQuestions[nextIndex]);
}

// Show history
async function showHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/history`);
        if (response.ok) {
            const data = await response.json();
            displayHistory(data.history || []);
            showHistorySection();
        }
    } catch (error) {
        console.error('Error loading history:', error);
        showError('Failed to load history');
    }
}

// Display history
function displayHistory(history) {
    elements.historyList.innerHTML = '';
    
    if (!history || history.length === 0) {
        elements.historyList.innerHTML = `
            <div class="no-history">
                <i class="fas fa-history"></i>
                <p>No analysis history found</p>
            </div>
        `;
        return;
    }
    
    // Show only last 10 items
    const recentHistory = history.slice(-10).reverse();
    
    recentHistory.forEach(item => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        
        const grade = item.feedback?.grade || 'N/A';
        const question = item.filename || 'Unknown Question';
        const timestamp = new Date(item.timestamp || Date.now()).toLocaleString();
        const codePreview = item.code_preview || 'No code preview';
        
        historyItem.innerHTML = `
            <div class="history-info">
                <span class="history-question">${question}</span>
                <span class="history-grade">Grade: ${grade}</span>
            </div>
            <div class="history-timestamp">${timestamp}</div>
            <div class="history-code">${codePreview}</div>
        `;
        
        elements.historyList.appendChild(historyItem);
    });
}

// Show/hide sections
function showWelcomeSection() {
    elements.welcomeSection.classList.remove('hidden');
    elements.loadingSection.classList.add('hidden');
    elements.resultsSection.classList.add('hidden');
    elements.historySection.classList.add('hidden');
}

function showLoadingSection() {
    elements.welcomeSection.classList.add('hidden');
    elements.loadingSection.classList.remove('hidden');
    elements.resultsSection.classList.add('hidden');
    elements.historySection.classList.add('hidden');
    
    // Animate loading steps
    const steps = document.querySelectorAll('.loading-steps .step');
    steps.forEach((step, index) => {
        setTimeout(() => {
            steps.forEach(s => s.classList.remove('active'));
            step.classList.add('active');
        }, index * 800);
    });
}

function showResultsSection() {
    elements.welcomeSection.classList.add('hidden');
    elements.loadingSection.classList.add('hidden');
    elements.resultsSection.classList.remove('hidden');
    elements.historySection.classList.add('hidden');
}

function showHistorySection() {
    elements.welcomeSection.classList.add('hidden');
    elements.loadingSection.classList.add('hidden');
    elements.resultsSection.classList.add('hidden');
    elements.historySection.classList.remove('hidden');
}

function clearResults() {
    currentAnalysis = null;
}

// Test API connection
async function testAPIConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('✅ Backend API is connected');
        } else {
            console.warn('⚠️ Backend API returned non-OK status');
        }
    } catch (error) {
        console.error('❌ Cannot connect to backend API:', error);
        showError('Cannot connect to backend server. Make sure it is running on port 5000.');
    }
}

// Show error message
function showError(message) {
    alert(`Error: ${message}`);
}

// Show loading state
function showLoading(element) {
    // Implement if needed
}

function hideLoading(element) {
    // Implement if needed
}

// Format topic name
function formatTopicName(topic) {
    return topic.split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

// Get topic icon
function getTopicIcon(topic) {
    const icons = {
        'for_loop': '🔄',
        'while_loop': '⚡',
        'if_else': '❓',
        'nested_if_else': '🎯'
    };
    
    return icons[topic] || '📝';
}

// Fallback data if API fails
function useFallbackData() {
    const fallbackData = {
        'for_loop': [
            { id: 1, difficulty: 'easy', question: 'Print numbers from 1 to 10.', concepts: ['for'] },
            { id: 3, difficulty: 'easy', question: 'Print all even numbers between 1 and 50.', concepts: ['for', 'if'] },
            { id: 10, difficulty: 'medium', question: 'Find factorial of a number.', concepts: ['for'] }
        ],
        'while_loop': [
            { id: 21, difficulty: 'easy', question: 'Print numbers from 1 to N.', concepts: ['while'] },
            { id: 25, difficulty: 'easy', question: 'Check whether a number is palindrome.', concepts: ['while', 'if'] }
        ],
        'if_else': [
            { id: 41, difficulty: 'easy', question: 'Check whether a number is positive or negative.', concepts: ['if', 'else'] },
            { id: 42, difficulty: 'easy', question: 'Check whether a number is even or odd.', concepts: ['if', 'else'] }
        ],
        'nested_if_else': [
            { id: 61, difficulty: 'easy', question: 'Find the largest of three numbers.', concepts: ['nested-if'] },
            { id: 65, difficulty: 'medium', question: 'Find grade based on marks using nested if.', concepts: ['nested-if'] }
        ]
    };
    
    displayTopics(fallbackData);
    
    const firstTopic = Object.keys(fallbackData)[0];
    if (firstTopic) {
        selectTopic(firstTopic, fallbackData[firstTopic]);
    }
    
    showError('Using fallback data. Backend server may not be running.');
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        elements,
        loadTopicsAndQuestions,
        analyzeCode,
        displayAnalysisResults
    };
}