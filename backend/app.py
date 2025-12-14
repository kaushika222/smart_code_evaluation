"""
smart-code-evaluator/backend/app.py
Flask web server for the Smart Code Evaluator.
"""
"""
smart-code-evaluator/backend/app.py
Flask web server for the Smart Code Evaluator.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys

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

@app.route('/')
def index():
    """Serve the frontend index.html."""
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory(('.. ','frontend'), filename)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze code from frontend."""
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
        print(f"Error in /analyze: {str(e)}")
        return jsonify({'error': str(e)}), 500

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
    print("  • GET  /                - Main web interface")
    print("  • POST /analyze         - Analyze code")
    print("  • GET  /history         - Get analysis history")
    print("  • GET  /stats           - Get statistics")
    print("  • GET  /examples        - Get example codes")
    print("  • GET  /health          - Health check")
    print("=" * 50)
    print("⚡ Server running... Press Ctrl+C to stop")
    print("=" * 50)
    
    # Run the Flask app
    app.run(debug=True, port=5000)