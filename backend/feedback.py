import os
from typing import List, Dict, Any
import datetime
from enum import Enum
import random
from history_manager import HistoryManager
from ai_detector import AIDetector


class SkillLevel(Enum):
    """Skill levels for personalized feedback."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class FeedbackGenerator:
    """Generates personalized feedback based on code analysis."""
    
    def __init__(self):
        self.skill_level = SkillLevel.BEGINNER
        self.positive_feedback = [
            "Great job keeping your functions small and focused!",
            "Your variable names are clear and descriptive.",
            "Good use of comments to explain complex logic.",
            "Well-structured code with proper indentation.",
            "You're following good naming conventions.",
            "Nice use of built-in functions and libraries.",
            "Your code is well-organized and easy to read.",
            "Good separation of concerns in your functions.",
            "You're handling edge cases properly.",
            "Excellent use of functions to avoid repetition."
        ]
        
        self.complexity_explanations = {
            "O(1)": "Constant time - Excellent! Your code runs at the same speed regardless of input size.",
            "O(n)": "Linear time - Good! Your code's speed increases proportionally with input size.",
            "O(n²)": "Quadratic time - Be careful! Your code slows down quickly as input grows.",
            "O(n³)": "Cubic time - Warning! This can become very slow with larger inputs.",
            "O(2ⁿ)": "Exponential time - Critical! This will be extremely slow even with small inputs."
        }
        
        self.learning_resources = {
            "NESTED_LOOPS": {
                "topic": "Algorithm Optimization",
                "resources": [
                    "📚 Book: 'Grokking Algorithms' by Aditya Bhargava",
                    "🎥 Video: 'Big O Notation' by CS Dojo",
                    "🛠️ Practice: LeetCode problems on time complexity",
                    "📝 Article: 'When to use which loop' on GeeksforGeeks"
                ]
            },
            "TOO_MANY_CONDITIONS": {
                "topic": "Code Refactoring",
                "resources": [
                    "📚 Book: 'Clean Code' by Robert C. Martin",
                    "🎥 Video: 'Refactoring techniques' by CodeAesthetic",
                    "🛠️ Practice: Replace conditional with polymorphism",
                    "📝 Article: 'Strategy Pattern' on Refactoring Guru"
                ]
            },
            "UNUSED_VARIABLE": {
                "topic": "Code Cleanup",
                "resources": [
                    "📚 Book: 'The Pragmatic Programmer'",
                    "🎥 Video: 'Dead code elimination'",
                    "🛠️ Practice: Use linters like pylint or flake8",
                    "📝 Article: 'DRY Principle' on Wikipedia"
                ]
            },
            "LONG_FUNCTION": {
                "topic": "Function Design",
                "resources": [
                    "📚 Book: 'Clean Code' Chapter 3",
                    "🎥 Video: 'Single Responsibility Principle'",
                    "🛠️ Practice: Break functions > 20 lines",
                    "📝 Article: 'Function decomposition' on Medium"
                ]
            },
            "DEEP_INDENTATION": {
                "topic": "Code Structure",
                "resources": [
                    "📚 Book: 'The Art of Readable Code'",
                    "🎥 Video: 'Flattening nested code'",
                    "🛠️ Practice: Use early returns",
                    "📝 Article: 'Guard clauses' on Dev.to"
                ]
            },
            "MAGIC_NUMBERS": {
                "topic": "Code Constants",
                "resources": [
                    "📚 Book: 'Code Complete' by Steve McConnell",
                    "🎥 Video: 'Why magic numbers are bad'",
                    "🛠️ Practice: Replace with named constants",
                    "📝 Article: 'Constants in programming' on FreeCodeCamp"
                ]
            }
        }
    
    def generate_feedback(self, 
                         analysis: Dict[str, Any], 
                         mistakes: List[Dict[str, str]], 
                         language: str,
                         code_lines: List[str] = None) -> Dict[str, Any]: 
        """
        Generate comprehensive feedback report.
        
        Args:
            analysis: Results from analyzer.py
            mistakes: List of mistakes from mistakes.py
            language: Programming language
            code_lines: Original code lines (optional)
            
        Returns:
            Complete feedback report
        """
        try:
            # Determine skill level
            self._determine_skill_level(analysis, mistakes)
            
            # Create feedback report
            feedback_report = {
                "timestamp": datetime.datetime.now().isoformat(),
                "language": language,
                "skill_level": self.skill_level.value,
                "summary": self._generate_summary(analysis, mistakes),
                "detailed_feedback": self._generate_detailed_feedback(analysis, mistakes),
                "positive_points": self._find_positive_points(analysis, mistakes),
                "mistakes": mistakes,
                "learning_path": self._generate_learning_path(mistakes),
                "complexity_analysis": self._analyze_complexity(analysis),
                "next_steps": self._suggest_next_steps(analysis, mistakes),
                "score": self._calculate_score(analysis, mistakes)
            }
            
            # Add AI detection if code_lines provided
            if code_lines:
                try:
                    ai_detector = AIDetector()
                    ai_results = ai_detector.detect_ai_patterns(
                        code_lines=code_lines,
                        language=language,
                        analysis=analysis,
                        skill_level=self.skill_level.value
                    )
                    feedback_report['ai_detection'] = ai_results
                    
                    # Add warning if suspicious
                    if ai_results.get('is_suspicious', False) and ai_results.get('confidence', 0) > 0.6:
                        feedback_report['summary'] += (
                            "\n⚠️  Note: Code shows patterns similar to AI-generated code. "
                            "Make sure you understand and write code yourself."
                        )
                except Exception as ai_error:
                    print(f"AI detection failed: {ai_error}")
                    feedback_report['ai_detection'] = {
                        'is_suspicious': False,
                        'error': str(ai_error)
                    }
            
            return feedback_report
            
        except Exception as e:
            print(f"Error generating feedback: {e}")
            return self._error_feedback()
    
    def _determine_skill_level(self, analysis: Dict[str, Any], mistakes: List[Dict[str, str]]):
        """Determine programmer's skill level based on code."""
        score = 100
        
        # Deduct points for mistakes
        score -= len(mistakes) * 10
        
        # Deduct points for complexity
        complexity = analysis.get('complexity', 'O(1)')
        if complexity == 'O(n²)':
            score -= 10
        elif complexity == 'O(n³)':
            score -= 20
        elif complexity == 'O(2ⁿ)':
            score -= 30
        
        # Bonus for good practices
        if analysis.get('functions', 0) > 1:
            score += 5
        if analysis.get('total_lines', 0) < 50:
            score += 5
        
        # Determine level
        if score >= 80:
            self.skill_level = SkillLevel.ADVANCED
        elif score >= 60:
            self.skill_level = SkillLevel.INTERMEDIATE
        else:
            self.skill_level = SkillLevel.BEGINNER
    
    def _generate_summary(self, analysis: Dict[str, Any], mistakes: List[Dict[str, str]]) -> str:
        """Generate a brief summary of the code quality."""
        total_mistakes = len(mistakes)
        lines = analysis.get('total_lines', 0)
        complexity = analysis.get('complexity', 'O(1)')
        
        if total_mistakes == 0:
            return f"✅ Excellent code! Your {lines} lines of code are well-structured with {complexity} complexity. Keep up the good work!"
        
        elif total_mistakes <= 2:
            return f"⚠️  Good effort! Found {total_mistakes} minor issues in {lines} lines of code. Complexity is {complexity}. Some improvements needed."
        
        else:
            return f"🚨 Needs attention! Found {total_mistakes} issues in {lines} lines of code with {complexity} complexity. Focus on the suggestions below."
    
    def _generate_detailed_feedback(self, analysis: Dict[str, Any], 
                                   mistakes: List[Dict[str, str]]) -> List[str]:
        """Generate detailed feedback points."""
        feedback_points = []
        
        # Add complexity feedback
        complexity = analysis.get('complexity', 'O(1)')
        if complexity in self.complexity_explanations:
            feedback_points.append(f"⏱️  **Time Complexity**: {self.complexity_explanations[complexity]}")
        
        # Add structure feedback
        loops = analysis.get('loops', 0)
        if loops == 0:
            feedback_points.append("✅ **Loop Usage**: No loops found - simple and direct logic.")
        elif loops == 1:
            feedback_points.append("✅ **Loop Usage**: Single loop - efficient linear processing.")
        else:
            feedback_points.append(f"🔍 **Loop Usage**: {loops} loops found. Watch for nested loops that increase complexity.")
        
        # Add function feedback
        functions = analysis.get('functions', 0)
        if functions == 0:
            feedback_points.append("💡 **Function Structure**: Consider breaking code into functions for better organization.")
        elif functions == 1:
            feedback_points.append("✅ **Function Structure**: Good single function structure.")
        else:
            feedback_points.append(f"✅ **Function Structure**: Great! {functions} functions show good modular design.")
        
        # Add mistake-specific feedback
        for mistake in mistakes:
            feedback_points.append(f"⚠️  **Issue**: {mistake['problem']}")
            feedback_points.append(f"   💡 **Suggestion**: {mistake['solution']}")
        
        return feedback_points
    
    def _find_positive_points(self, analysis: Dict[str, Any], 
                             mistakes: List[Dict[str, str]]) -> List[str]:
        """Find and highlight positive aspects of the code."""
        positives = []
        
        # Check for good practices
        if analysis.get('total_lines', 0) < 100:
            positives.append("📏 **Concise Code**: Your code is reasonably short and focused.")
        
        if analysis.get('nested_loops', 0) == 0:
            positives.append("🔄 **Flat Structure**: No deeply nested loops - good for readability.")
        
        if analysis.get('conditionals', 0) < 3:
            positives.append("🎯 **Simple Logic**: Minimal conditional branching makes code easier to follow.")
        
        # Add some random positive feedback
        if len(positives) < 3:
            extra_positives = random.sample(self.positive_feedback, min(2, len(self.positive_feedback)))
            positives.extend(extra_positives)
        
        return positives
    
    def _generate_learning_path(self, mistakes: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Create personalized learning recommendations based on mistakes."""
        learning_path = []
        
        # Group similar mistakes
        mistake_types = set(mistake['type'] for mistake in mistakes)
        
        for mistake_type in mistake_types:
            if mistake_type in self.learning_resources:
                topic_info = self.learning_resources[mistake_type].copy()
                # Count how many of this type
                count = sum(1 for m in mistakes if m['type'] == mistake_type)
                topic_info['priority'] = 'High' if count > 1 else 'Medium'
                learning_path.append(topic_info)
        
        # Add general learning if no specific mistakes
        if not learning_path:
            learning_path.append({
                "topic": "General Programming Best Practices",
                "resources": [
                    "📚 Book: 'Clean Code' by Robert C. Martin",
                    "🎥 Video: 'Programming Principles' by FreeCodeCamp",
                    "🛠️ Practice: Code reviews and pair programming",
                    "📝 Article: '10 Good Programming Practices' on Medium"
                ],
                "priority": "Low"
            })
        
        return learning_path
    
    def _analyze_complexity(self, analysis: Dict[str, Any]) -> Dict[str, str]:
        """Provide detailed complexity analysis."""
        complexity = analysis.get('complexity', 'O(1)')
        loops = analysis.get('loops', 0)
        nested = analysis.get('nested_loops', 0)
        
        analysis_text = {
            "current_complexity": complexity,
            "explanation": self.complexity_explanations.get(complexity, ""),
            "improvement_tip": ""
        }
        
        # Add improvement tips
        if complexity == 'O(n²)' and nested > 0:
            analysis_text["improvement_tip"] = "Consider using hash tables or sorting to reduce nested loops."
        elif complexity == 'O(n³)':
            analysis_text["improvement_tip"] = "This is very slow for large inputs. Look for algorithmic improvements."
        elif complexity == 'O(2ⁿ)':
            analysis_text["improvement_tip"] = "Exponential complexity is rarely acceptable. Consider dynamic programming."
        
        return analysis_text
    
    def _suggest_next_steps(self, analysis: Dict[str, Any], 
                           mistakes: List[Dict[str, str]]) -> List[str]:
        """Suggest concrete next steps for improvement."""
        next_steps = []
        
        # Based on skill level
        if self.skill_level == SkillLevel.BEGINNER:
            next_steps.append("1. **Practice**: Write 5 small programs focusing on one concept each")
            next_steps.append("2. **Read**: Complete one chapter of a beginner programming book")
            next_steps.append("3. **Review**: Compare your code with examples in documentation")
        
        elif self.skill_level == SkillLevel.INTERMEDIATE:
            next_steps.append("1. **Refactor**: Pick one project and improve its structure")
            next_steps.append("2. **Learn**: Study one design pattern this week")
            next_steps.append("3. **Contribute**: Fix one issue in an open-source project")
        
        else:  # Advanced
            next_steps.append("1. **Optimize**: Profile your code and improve performance")
            next_steps.append("2. **Teach**: Write a tutorial about what you've learned")
            next_steps.append("3. **Architect**: Design a larger system with multiple components")
        
        # Add specific steps based on mistakes
        if any(m['type'] == 'NESTED_LOOPS' for m in mistakes):
            next_steps.append("🔁 **Focus**: Practice algorithms with better time complexity")
        
        if any(m['type'] == 'LONG_FUNCTION' for m in mistakes):
            next_steps.append("✂️ **Focus**: Break one long function into smaller ones this week")
        
        return next_steps
    
    def _calculate_score(self, analysis: Dict[str, Any], 
                        mistakes: List[Dict[str, str]]) -> Dict[str, Any]:
        """Calculate a score for the code."""
        base_score = 100
        total_mistakes = len(mistakes)
        
        # Deduct for mistakes
        score = base_score - (total_mistakes * 5)
        
        # Deduct for complexity
        complexity = analysis.get('complexity', 'O(1)')
        complexity_penalty = {'O(1)': 0, 'O(n)': 0, 'O(n²)': 10, 'O(n³)': 20, 'O(2ⁿ)': 30}
        score -= complexity_penalty.get(complexity, 0)
        
        # Bonus for good structure
        if analysis.get('functions', 0) > 1:
            score += 5
        if analysis.get('total_lines', 0) < 50:
            score += 5
        if analysis.get('nested_loops', 0) == 0:
            score += 5
        
        # Ensure score is within bounds
        score = max(0, min(100, score))
        
        return {
            "score": score,
            "grade": self._get_grade(score),
            "breakdown": {
                "base": 100,
                "mistakes_penalty": total_mistakes * 5,
                "complexity_penalty": complexity_penalty.get(complexity, 0),
                "bonus_points": max(0, score - (100 - total_mistakes * 5 - complexity_penalty.get(complexity, 0)))
            }
        }
    
    def _get_grade(self, score: int) -> str:
        """Convert score to letter grade."""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"
    
    def _error_feedback(self) -> Dict[str, Any]:
        """Return error feedback when something goes wrong."""
        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "error": "Could not generate feedback",
            "suggestion": "Please check your code and try again."
        }


def format_feedback_for_display(feedback: Dict[str, Any]) -> str:
    """Format feedback nicely for display."""
    output = []
    
    output.append("=" * 60)
    output.append("📊 CODE ANALYSIS REPORT")
    output.append("=" * 60)
    output.append(f"📅 Date: {feedback.get('timestamp', 'N/A')}")
    output.append(f"💻 Language: {feedback.get('language', 'Unknown').upper()}")
    output.append(f"🎯 Skill Level: {feedback.get('skill_level', 'Unknown').upper()}")
    output.append(f"🏆 Score: {feedback.get('score', {}).get('score', 0)}/100 ({feedback.get('score', {}).get('grade', 'N/A')})")
    output.append("")
    
    # Summary
    output.append("📋 SUMMARY")
    output.append("-" * 40)
    output.append(feedback.get('summary', 'No summary available'))
    output.append("")
    
    # Positive points
    positives = feedback.get('positive_points', [])
    if positives:
        output.append("✅ STRENGTHS")
        output.append("-" * 40)
        for point in positives[:3]:  # Show top 3
            output.append(f"• {point}")
        output.append("")
    
    # Detailed feedback
    details = feedback.get('detailed_feedback', [])
    if details:
        output.append("🔍 DETAILED FEEDBACK")
        output.append("-" * 40)
        for point in details:
            output.append(point)
        output.append("")
    
    # Learning path
    learning = feedback.get('learning_path', [])
    if learning:
        output.append("🎓 RECOMMENDED LEARNING")
        output.append("-" * 40)
        for i, topic in enumerate(learning, 1):
            output.append(f"{i}. {topic.get('topic', 'Unknown')} [{topic.get('priority', 'N/A')} Priority]")
            for resource in topic.get('resources', [])[:2]:  # Show top 2 resources
                output.append(f"   {resource}")
            if i < len(learning):
                output.append("")
        output.append("")
    
    # Next steps
    next_steps = feedback.get('next_steps', [])
    if next_steps:
        output.append("🚀 NEXT STEPS")
        output.append("-" * 40)
        for step in next_steps[:3]:  # Show top 3
            output.append(step)
    
    output.append("")
    output.append("=" * 60)
    output.append("✨ Keep coding and learning! ✨")
    output.append("=" * 60)
    
    return "\n".join(output)


def test_feedback_generator():
    """Test the feedback generator."""
    generator = FeedbackGenerator()
    
    print("🧪 Testing Feedback Generator")
    print("=" * 60)
    
    # Test 1: Code with issues
    test_analysis = {
        'total_lines': 45,
        'loops': 3,
        'nested_loops': 2,
        'max_nesting_depth': 3,
        'conditionals': 6,
        'functions': 1,
        'variables': 5,
        'complexity': 'O(n²)'
    }
    
    test_mistakes = [
        {
            'type': 'NESTED_LOOPS',
            'problem': 'Code has 3 levels of nested loops',
            'why_bad': 'Deep nesting makes code hard to read',
            'solution': 'Try to flatten your logic',
            'learn_next': 'Learn about algorithmic optimization'
        },
        {
            'type': 'TOO_MANY_CONDITIONS',
            'problem': 'Function has 6 if/else statements',
            'why_bad': 'Too many conditions make code hard to follow',
            'solution': 'Use switch statements or lookup tables',
            'learn_next': 'Learn about design patterns'
        }
    ]
    
    print("\nTest 1: Code with Issues")
    print("-" * 40)
    
    # Create dummy code lines for test
    test_code_lines = [
        "def example():",
        "    for i in range(10):",
        "        for j in range(10):",
        "            print(i * j)"
    ]
    
    feedback = generator.generate_feedback(test_analysis, test_mistakes, 'python', test_code_lines)
    
    formatted = format_feedback_for_display(feedback)
    print(formatted)
    
    # Test 2: Clean code
    print("\n\nTest 2: Clean Code")
    print("-" * 40)
    
    clean_analysis = {
        'total_lines': 25,
        'loops': 1,
        'nested_loops': 0,
        'max_nesting_depth': 1,
        'conditionals': 2,
        'functions': 3,
        'variables': 4,
        'complexity': 'O(n)'
    }
    
    clean_mistakes = []
    
    feedback = generator.generate_feedback(clean_analysis, clean_mistakes, 'python', [])
    
    formatted = format_feedback_for_display(feedback)
    print(formatted)
    
    return feedback


def generate_feedback_for_file(file_path: str):
    """Generate feedback for a code file and save to history."""
    from code_reader import CodeReader
    from analyser import analyser
    from mistakes import MistakeDetector
    
    # Initialize components
    reader = CodeReader()
    analyzer = analyzer()
    detector = MistakeDetector()
    generator = FeedbackGenerator()
    history = HistoryManager()
    
    # Read and analyze
    code_lines, language, error = reader.read_code_file(file_path)
    
    if error:
        print(f"❌ Error: {error}")
        return
    
    if not code_lines:
        print("❌ No code found")
        return
    
    # Get original code
    try:
        with open(file_path, 'r') as f:
            original_code = f.read()
    except Exception as e:
        print(f"❌ Error reading original file: {e}")
        original_code = ""
    
    # Analyze code
    analysis = analyzer.analyze_code(code_lines, language)
    
    # Detect mistakes
    mistakes = detector.detect_mistakes(code_lines, language, analysis)
    
    # Generate feedback
    feedback = generator.generate_feedback(analysis, mistakes, language, code_lines)
    
    # Save to history
    success = history.save_analysis(
        feedback=feedback,
        code_snippet=original_code,
        filename=os.path.basename(file_path)
    )
    
    if success:
        print("✅ Analysis saved to history!")
    
    # Display feedback
    formatted = format_feedback_for_display(feedback)
    print(formatted)
    
    return feedback


if __name__ == "__main__":
    # Run tests
    test_feedback_generator()
    
    # Uncomment to test with actual file
    # import sys
    # if len(sys.argv) > 1:
    #     generate_feedback_for_file(sys.argv[1])
    # else:
    #     print("\nTo generate feedback for a file:")
    #     print("python feedback.py <file_path>")
    #     print("Example: python feedback.py ../test.py")