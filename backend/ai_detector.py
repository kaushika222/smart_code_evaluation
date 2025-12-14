# backend/ai_detector.py

"""
AI Code Detector - Detects potential AI-generated code
Version: 1.0
"""

import math
import re
from typing import List, Dict, Any


class AIDetector:
    """Detects potential AI-generated code patterns."""
    
    def __init__(self):
        # Thresholds (can be adjusted)
        self.thresholds = {
            'comment_ratio': 0.3,      # More than 30% comments is suspicious
            'perfection_score': 0.8,   # Too perfect naming/structure
            'complexity_mismatch': 0.7,# Code too complex for skill level
            'pattern_repetition': 0.6  # Too much repetition
        }
    
    def detect_ai_patterns(self, 
                          code_lines: List[str], 
                          language: str,
                          analysis: Dict[str, Any],
                          skill_level: str) -> Dict[str, Any]:
        """
        Detect potential AI-generated code patterns.
        
        Args:
            code_lines: Cleaned code lines
            language: Programming language
            analysis: Code analysis results
            skill_level: User's skill level from feedback
            
        Returns:
            Detection results
        """
        results = {
            'is_suspicious': False,
            'confidence': 0.0,
            'detected_patterns': [],
            'explanations': [],
            'recommendations': []
        }
        
        try:
            # Calculate various metrics
            comment_ratio = self._calculate_comment_ratio(code_lines, language)
            perfection_score = self._calculate_perfection_score(code_lines, language)
            complexity_mismatch = self._calculate_complexity_mismatch(analysis, skill_level)
            pattern_score = self._calculate_pattern_repetition(code_lines)
            
            # Check each metric against thresholds
            suspicious_patterns = []
            
            if comment_ratio > self.thresholds['comment_ratio']:
                suspicious_patterns.append('HIGH_COMMENT_RATIO')
                results['explanations'].append(
                    f"Code has {comment_ratio:.1%} comments. "
                    "AI often adds excessive comments."
                )
            
            if perfection_score > self.thresholds['perfection_score']:
                suspicious_patterns.append('TOO_PERFECT')
                results['explanations'].append(
                    f"Code structure is very perfect (score: {perfection_score:.2f}). "
                    "AI generates flawlessly formatted code."
                )
            
            if complexity_mismatch > self.thresholds['complexity_mismatch']:
                suspicious_patterns.append('COMPLEXITY_MISMATCH')
                results['explanations'].append(
                    f"Code complexity doesn't match {skill_level} skill level. "
                    "AI can write advanced code easily."
                )
            
            if pattern_score > self.thresholds['pattern_repetition']:
                suspicious_patterns.append('REPETITIVE_PATTERNS')
                results['explanations'].append(
                    "Code shows repetitive AI-like patterns."
                )
            
            # Calculate overall confidence
            if suspicious_patterns:
                results['is_suspicious'] = True
                results['detected_patterns'] = suspicious_patterns
                results['confidence'] = self._calculate_confidence(
                    comment_ratio,
                    perfection_score,
                    complexity_mismatch,
                    pattern_score
                )
                
                # Add recommendations
                results['recommendations'] = [
                    "Write code in your own style, not perfect textbook style",
                    "Add personal comments explaining YOUR thought process",
                    "Make small human-like variations in your code",
                    "Don't copy patterns exactly - add your own twist"
                ]
            
            return results
            
        except Exception as e:
            print(f"Error in AI detection: {e}")
            return results
    
    def _calculate_comment_ratio(self, code_lines: List[str], language: str) -> float:
        """Calculate ratio of comments to code."""
        total_lines = len(code_lines)
        if total_lines == 0:
            return 0.0
        
        comment_count = 0
        
        for line in code_lines:
            stripped = line.strip()
            
            if language == 'python':
                if stripped.startswith('#'):
                    comment_count += 1
            else:  # C/C++
                if stripped.startswith('//') or '/*' in stripped:
                    comment_count += 1
        
        return comment_count / total_lines
    
    def _calculate_perfection_score(self, code_lines: List[str], language: str) -> float:
        """Calculate how 'perfect' the code is."""
        score = 0.0
        metrics_checked = 0
        
        # 1. Variable naming perfection
        variable_score = self._check_variable_naming(code_lines, language)
        score += variable_score
        metrics_checked += 1
        
        # 2. Function structure perfection
        function_score = self._check_function_structure(code_lines, language)
        score += function_score
        metrics_checked += 1
        
        # 3. Formatting consistency
        format_score = self._check_formatting_consistency(code_lines)
        score += format_score
        metrics_checked += 1
        
        return score / metrics_checked if metrics_checked > 0 else 0.0
    
    def _check_variable_naming(self, code_lines: List[str], language: str) -> float:
        """Check if variable names are 'too perfect'."""
        perfect_patterns = [
            r'\bindex\b', r'\bcounter\b', r'\bresult\b', r'\btemp\b',
            r'\bvalue\b', r'\bdata\b', r'\binput\b', r'\boutput\b'
        ]
        
        variable_names = []
        for line in code_lines:
            # Simple variable extraction (basic)
            if '=' in line and '==' not in line:
                left_side = line.split('=')[0].strip()
                words = left_side.split()
                if words:
                    variable_names.append(words[-1])
        
        if not variable_names:
            return 0.0
        
        perfect_count = 0
        for var in variable_names:
            for pattern in perfect_patterns:
                if re.search(pattern, var, re.IGNORECASE):
                    perfect_count += 1
                    break
        
        return perfect_count / len(variable_names)
    
    def _check_function_structure(self, code_lines: List[str], language: str) -> float:
        """Check if functions follow perfect textbook structure."""
        if language == 'python':
            func_pattern = r'def\s+\w+\(.*\):'
        else:  # C/C++
            func_pattern = r'\w+\s+\w+\(.*\)\s*{'
        
        func_lines = []
        for line in code_lines:
            if re.search(func_pattern, line):
                func_lines.append(line)
        
        if not func_lines:
            return 0.0
        
        # Check for perfect textbook patterns
        perfect_count = 0
        textbook_patterns = [
            r'def\s+main\(\):',  # Python main
            r'int\s+main\(\)',   # C main
            r'void\s+setup\(\)', # Common patterns
            r'def\s+calculate_', # Calculate functions
            r'def\s+process_'    # Process functions
        ]
        
        for line in func_lines:
            for pattern in textbook_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    perfect_count += 1
                    break
        
        return perfect_count / len(func_lines)
    
    def _check_formatting_consistency(self, code_lines: List[str]) -> float:
        """Check formatting consistency (too consistent = suspicious)."""
        if len(code_lines) < 3:
            return 0.0
        
        # Check indentation consistency
        indent_lengths = []
        for line in code_lines:
            if line.strip():  # Skip empty lines
                leading_spaces = len(line) - len(line.lstrip())
                indent_lengths.append(leading_spaces)
        
        if not indent_lengths:
            return 0.0
        
        # Calculate consistency (lower variance = more consistent)
        mean = sum(indent_lengths) / len(indent_lengths)
        variance = sum((x - mean) ** 2 for x in indent_lengths) / len(indent_lengths)
        
        # Perfect consistency would have variance = 0
        # More variance = more human-like
        consistency = 1.0 - min(variance / 4.0, 1.0)  # Normalize
        
        return consistency
    
    def _calculate_complexity_mismatch(self, 
                                      analysis: Dict[str, Any], 
                                      skill_level: str) -> float:
        """Check if code complexity matches skill level."""
        # Get complexity metrics
        complexity = analysis.get('complexity', 'O(1)')
        nested_loops = analysis.get('nested_loops', 0)
        functions = analysis.get('functions', 0)
        
        # Map skill levels to expected complexity
        expected_complexity = {
            'beginner': 'O(n)',
            'intermediate': 'O(n²)',
            'advanced': 'O(n³)'
        }
        
        expected = expected_complexity.get(skill_level, 'O(n)')
        
        # Complexity scores
        complexity_scores = {
            'O(1)': 1,
            'O(n)': 2,
            'O(n²)': 3,
            'O(n³)': 4,
            'O(2ⁿ)': 5
        }
        
        actual_score = complexity_scores.get(complexity, 1)
        expected_score = complexity_scores.get(expected, 1)
        
        # Calculate mismatch
        if actual_score > expected_score + 1:  # Much more complex than expected
            mismatch = min((actual_score - expected_score) / 3.0, 1.0)
        else:
            mismatch = 0.0
        
        # Adjust for other factors
        if skill_level == 'beginner' and nested_loops > 1:
            mismatch += 0.3
        
        if skill_level == 'beginner' and functions > 2:
            mismatch += 0.2
        
        return min(mismatch, 1.0)
    
    def _calculate_pattern_repetition(self, code_lines: List[str]) -> float:
        """Check for repetitive AI-like patterns."""
        if len(code_lines) < 5:
            return 0.0
        
        # Common AI patterns to check
        ai_patterns = [
            r'for.*in range\(.*\):',           # Python range loops
            r'for\(.*;.*;.*\)\s*{',            # C for loops
            r'if.*:\s*$',                      # Python if statements
            r'def\s+\w+\(self,.*\):',          # Method definitions
            r'print\(f".*"\)',                 # f-strings
            r'return\s+\w+',                   # Simple returns
            r'int\s+\w+\s*=\s*\d+;'           # C int declarations
        ]
        
        pattern_counts = {}
        total_patterns = 0
        
        for line in code_lines:
            for pattern in ai_patterns:
                if re.search(pattern, line):
                    pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
                    total_patterns += 1
        
        if total_patterns == 0:
            return 0.0
        
        # Calculate repetition score
        repetition_score = 0.0
        for count in pattern_counts.values():
            repetition_score += (count - 1) * 0.2  # Penalize repetition
        
        return min(repetition_score, 1.0)
    
    def _calculate_confidence(self, *scores) -> float:
        """Calculate overall confidence score."""
        weights = [0.3, 0.3, 0.25, 0.15]  # Weight for each metric
        confidence = 0.0
        
        for score, weight in zip(scores, weights):
            confidence += score * weight
        
        return min(confidence, 1.0)


def test_ai_detector():
    """Test the AI detector."""
    print("🧪 Testing AI Detector")
    print("=" * 60)
    
    detector = AIDetector()
    
    # Test 1: Potential AI-generated code
    ai_like_code = [
        "# Calculate the sum of numbers",
        "def calculate_sum(numbers):",
        "    # Initialize total to zero",
        "    total = 0",
        "    # Iterate through each number",
        "    for number in numbers:",
        "        # Add number to total",
        "        total += number",
        "    # Return the total sum",
        "    return total",
        "",
        "# Main function",
        "def main():",
        "    # Sample numbers list",
        "    numbers = [1, 2, 3, 4, 5]",
        "    # Calculate sum",
        "    result = calculate_sum(numbers)",
        "    # Display result",
        "    print(f'The sum is: {result}')"
    ]
    
    print("\nTest 1: AI-like Code (lots of comments, perfect structure)")
    print("-" * 40)
    
    analysis = {
        'complexity': 'O(n)',
        'nested_loops': 0,
        'functions': 2
    }
    
    results = detector.detect_ai_patterns(ai_like_code, 'python', analysis, 'beginner')
    
    print(f"Suspicious: {results['is_suspicious']}")
    print(f"Confidence: {results['confidence']:.2%}")
    print(f"Patterns: {results['detected_patterns']}")
    print("Explanations:")
    for exp in results['explanations']:
        print(f"  • {exp}")
    
    # Test 2: Human-like code
    human_code = [
        "x = [1,2,3,4,5]",
        "s = 0",
        "for n in x:",
        "    s = s + n  # adding",
        "print(s)",
        "# thats it"
    ]
    
    print("\n\nTest 2: Human-like Code (imperfect, minimal comments)")
    print("-" * 40)
    
    results = detector.detect_ai_patterns(human_code, 'python', analysis, 'beginner')
    
    print(f"Suspicious: {results['is_suspicious']}")
    print(f"Confidence: {results['confidence']:.2%}")
    if results['is_suspicious']:
        print("Patterns:", results['detected_patterns'])
    
    return results


if __name__ == "__main__":
    test_ai_detector()