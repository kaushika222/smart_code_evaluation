"""
smart-code-evaluator/backend/app.py
Flask web server for the Smart Code Evaluator.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
import json
from datetime import datetime
# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from code_reader import CodeReader
from analyzer import CodeAnalyzer
from mistakes import MistakeDetector
from feedback import FeedbackGenerator
from ai_detector import AIDetector
from history_manager import HistoryManager

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize components
reader = CodeReader()
analyzer = CodeAnalyzer()
detector = MistakeDetector()
feedback_gen = FeedbackGenerator()
ai_detector = AIDetector()
history_manager = HistoryManager()

# Path to questions
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_PATH = os.path.join(BASE_DIR, "..", "data", "questions.json")

# Load questions
with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
    QUESTIONS = json.load(f)

@app.route('/')
def index():
    """Serve the frontend index.html."""
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory('../frontend', filename)

@app.route('/analyze-old', methods=['POST'])
def analyze_old():
    """Analyze code from frontend (old method)."""
    try:
        # Get data from request
        data = request.json
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        if not code:
            return jsonify({'error': 'No code provided'}), 400
        
        if len(code) > 10000:  # Limit code size
            return jsonify({'error': 'Code too large (max 10000 characters)'}), 400
        
        # Clean the code
        code_lines = reader.read_code_from_text(code, language)
        
        if not code_lines:
            return jsonify({'error': 'No valid code found after cleaning'}), 400
        
        # Analyze code structure
        analysis = analyzer.analyze_code(code_lines, language)
        
        # Detect mistakes
        mistakes = detector.detect_mistakes(code_lines, language, analysis)
        
        # Generate feedback
        feedback = feedback_gen.generate_feedback(analysis, mistakes, language, code_lines)
        
        # Detect AI patterns
        ai_results = ai_detector.detect_ai_patterns(
            code_lines, 
            language, 
            analysis, 
            feedback.get('skill_level', 'beginner')
        )
        feedback['ai_detection'] = ai_results
        
        # Add code_lines to feedback for history
        feedback['code_lines_count'] = len(code_lines)
        
        # Save to history
        history_manager.save_analysis(
            feedback=feedback,
            code_snippet=code,
            filename=f"web_input.{language}"
        )
        
        return jsonify(feedback)
        
    except Exception as e:
        print(f"Error in /analyze-old: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze_code():
    """Analyze code submission with question-based evaluation."""
    try:
        data = request.json
        code = data.get('code', '')
        question_id = data.get('question_id')
        language = data.get('language', 'python')
        
        if not code:
            return jsonify({"error": "No code provided"}), 400
        
        if len(code) > 10000:
            return jsonify({"error": "Code too large (max 10000 characters)"}), 400
        
        # Analyze the code using new analyzer
        result = analyzer.analyze_submission(code, question_id)
        
        # Get question info
        question_info = {}
        for category in QUESTIONS.values():
            for question in category:
                if question['id'] == question_id:
                    question_info = question
                    break
            if question_info:
                break
        
        # Save to history
        history_manager.save_analysis(
            feedback=result,
            code_snippet=code,
            filename=f"question_{question_id}.{language}"
        )
        
        return jsonify({
            "success": True,
            "analysis": result,
            "question": question_info
        })
        
    except Exception as e:
        print(f"Error in /analyze: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    """Get analysis history."""
    try:
        history = history_manager.get_all_analyses()
        return jsonify({'history': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get statistics."""
    try:
        stats = history_manager.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy', 
        'service': 'Smart Code Evaluator',
        'version': '1.0',
        'modules_loaded': True
    })

@app.route('/questions', methods=['GET'])
def get_questions():
    """
    Return coding practice questions.
    Optional query param: ?topic=for_loop / while_loop / if_else / nested_if_else
    """
    topic = request.args.get("topic")

    if topic:
        return jsonify(QUESTIONS.get(topic, []))

    return jsonify(QUESTIONS)

@app.route('/questions/all', methods=['GET'])
def get_all_questions():
    """Get all questions organized by topic."""
    return jsonify(QUESTIONS)

@app.route('/questions/<int:question_id>', methods=['GET'])
def get_question(question_id):
    """Get specific question by ID."""
    try:
        # Search for the question
        for category in QUESTIONS.values():
            for question in category:
                if question['id'] == question_id:
                    return jsonify({
                        "success": True,
                        "question": question
                    })
        
        return jsonify({"success": False, "error": "Question not found"}), 404
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/examples', methods=['GET'])
def get_examples():
    """Get example codes for each language."""
    examples = {
        'python': '''# Python Example - Calculate Fibonacci
def fibonacci(n):
    """Calculate Fibonacci sequence."""
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
        print(num, end=" ")''',
        
        'c': '''// C Example - Calculate Factorial
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
}''',
        
        'cpp': '''// C++ Example - Simple Calculator
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
}'''
    }
    
    return jsonify(examples)

@app.route('/analyze/quick', methods=['POST'])
def quick_analyze():
    """Quick code analysis without question ID."""
    try:
        data = request.json
        code = data.get('code', '')
        
        if not code:
            return jsonify({"error": "No code provided"}), 400
        
        # Use code reader for basic analysis
        analysis = reader.read_code(code)
        quality = reader.analyze_code_quality(code)
        variables = reader.check_variable_names(code)
        
        result = {
            "basic_analysis": analysis,
            "quality_analysis": quality,
            "variable_analysis": variables,
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify({
            "success": True,
            "analysis": result
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/topics', methods=['GET'])
def get_topics():
    """Get all available question topics."""
    topics = list(QUESTIONS.keys())
    return jsonify({
        "topics": topics,
        "count": len(topics)
    })

@app.route('/topics/<topic_name>/questions', methods=['GET'])
def get_topic_questions(topic_name):
    """Get all questions for a specific topic."""
    if topic_name in QUESTIONS:
        return jsonify({
            "topic": topic_name,
            "questions": QUESTIONS[topic_name]
        })
    else:
        return jsonify({"error": f"Topic '{topic_name}' not found"}), 404

@app.route('/difficulty/<level>', methods=['GET'])
def get_questions_by_difficulty(level):
    """Get questions by difficulty level."""
    level = level.lower()
    filtered_questions = []
    
    for category in QUESTIONS.values():
        for question in category:
            if question.get('difficulty', '').lower() == level:
                filtered_questions.append(question)
    
    return jsonify({
        "difficulty": level,
        "count": len(filtered_questions),
        "questions": filtered_questions
    })

@app.route('/concepts/<concept_name>', methods=['GET'])
def get_questions_by_concept(concept_name):
    """Get questions that require a specific concept."""
    concept_name = concept_name.lower()
    filtered_questions = []
    
    for category in QUESTIONS.values():
        for question in category:
            concepts = [c.lower() for c in question.get('concepts', [])]
            if concept_name in concepts:
                filtered_questions.append(question)
    
    return jsonify({
        "concept": concept_name,
        "count": len(filtered_questions),
        "questions": filtered_questions
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Smart Code Evaluator Server...")
    print("=" * 50)
    print("📁 Frontend: http://localhost:5000")
    print("📡 API Endpoints:")
    print("  • GET  /                           - Main web interface")
    print("  • POST /analyze                    - Analyze code with question ID")
    print("  • POST /analyze-old                - Legacy code analysis")
    print("  • POST /analyze/quick              - Quick code analysis")
    print("  • GET  /history                    - Get analysis history")
    print("  • GET  /stats                      - Get statistics")
    print("  • GET  /questions                  - Get all questions")
    print("  • GET  /questions/all              - Get all questions organized")
    print("  • GET  /questions/<id>             - Get specific question")
    print("  • GET  /topics                     - Get all topics")
    print("  • GET  /topics/<topic>/questions   - Get questions by topic")
    print("  • GET  /difficulty/<level>         - Get questions by difficulty")
    print("  • GET  /concepts/<concept>         - Get questions by concept")
    print("  • GET  /examples                   - Get example codes")
    print("  • GET  /health                     - Health check")
    print("=" * 50)
    print("⚡ Server running... Press Ctrl+C to stop")
    print("=" * 50)
    
    # Run the Flask app
    app.run(debug=True, port=5000, host='0.0.0.0')