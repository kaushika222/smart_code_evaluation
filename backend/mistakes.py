"""
smart-code-evaluator/backend/mistakes.py
Detects common beginner mistakes in code.
Version: 2.0
"""

from typing import List, Dict, Any


class MistakeDetector:
    """Detects common beginner coding mistakes."""
    
    def __init__(self):
        # Define threshold values (can be adjusted)
        self.thresholds = {
            'max_nested_loops': 2,          # More than 2 levels of nesting
            'max_conditions_per_function': 5, # More than 5 if/else
            'max_function_lines': 50,        # Functions longer than 50 lines
            'max_indentation_level': 4,      # More than 4 indentation levels
            'max_magic_numbers': 3,          # More than 3 magic numbers
        }
        
        self.mistakes = []
    
    def detect_mistakes(self, code_lines: List[str], language: str, 
                       analysis_results: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Detect beginner mistakes in code.
        
        Args:
            code_lines: Cleaned code lines
            language: Programming language
            analysis_results: From analyzer.py
            
        Returns:
            List of mistake dictionaries with problem and solution
        """
        self.mistakes = []  # Reset for each analysis
        
        if not code_lines or not analysis_results:
            return []
        
        try:
            # Check each type of mistake
            self._check_nested_loops(analysis_results)
            self._check_too_many_conditions(analysis_results)
            self._check_long_functions(analysis_results)
            self._check_unused_variables(code_lines, language)
            self._check_deep_indentation(code_lines, language)
            self._check_magic_numbers(code_lines, language)
            
            return self.mistakes
            
        except Exception as e:
            print(f"Error in mistake detection: {e}")
            return []
    
    def _check_nested_loops(self, analysis: Dict[str, Any]):
        """Check for too many nested loops."""
        if analysis.get('nested_loops', 0) > 0:
            depth = analysis.get('max_nesting_depth', 0)
            
            if depth > self.thresholds['max_nested_loops']:
                self.mistakes.append({
                    'type': 'NESTED_LOOPS',
                    'problem': f'Code has {depth} levels of nested loops',
                    'why_bad': 'Deep nesting makes code hard to read and maintain. '
                              'It increases complexity and reduces performance.',
                    'solution': 'Try to flatten your logic or break into functions. '
                               'Consider using built-in functions like map() or list comprehensions.',
                    'learn_next': 'Learn about algorithmic optimization and refactoring techniques.'
                })
    
    def _check_too_many_conditions(self, analysis: Dict[str, Any]):
        """Check for too many conditional statements."""
        conditions = analysis.get('conditionals', 0)
        
        if conditions > self.thresholds['max_conditions_per_function']:
            self.mistakes.append({
                'type': 'TOO_MANY_CONDITIONS',
                'problem': f'Function has {conditions} if/else statements',
                'why_bad': 'Too many conditions make code hard to follow and test. '
                          'It indicates complex business logic that should be simplified.',
                'solution': 'Use switch/case statements, lookup tables, or strategy pattern. '
                           'Consider breaking into smaller functions.',
                'learn_next': 'Learn about design patterns and refactoring techniques.'
            })
    
    def _check_long_functions(self, analysis: Dict[str, Any]):
        """Check for functions that are too long."""
        lines = analysis.get('total_lines', 0)
        functions = analysis.get('functions', 0)
        
        # Simple check: if whole file is long and has few functions
        if lines > self.thresholds['max_function_lines'] and functions <= 1:
            self.mistakes.append({
                'type': 'LONG_FUNCTION',
                'problem': f'Code has {lines} lines in main function/script',
                'why_bad': 'Long functions are hard to read, test, and maintain. '
                          'They often do too many things.',
                'solution': 'Break the function into smaller, focused functions. '
                           'Each function should do one thing well.',
                'learn_next': 'Learn about Single Responsibility Principle and function decomposition.'
            })
    
    def _check_unused_variables(self, code_lines: List[str], language: str):
        """Check for variables that are declared but not used (basic check)."""
        if language == 'python':
            self._check_unused_variables_python(code_lines)
        else:
            self._check_unused_variables_c_cpp(code_lines)
    
    def _check_unused_variables_python(self, code_lines: List[str]):
        """Basic unused variable detection for Python."""
        # Find variable assignments
        variables = []
        
        for line in code_lines:
            stripped = line.strip()
            
            # Skip function definitions, loops, conditions
            if any(keyword in stripped for keyword in ['def ', 'for ', 'while ', 'if ', 'elif ', 'else:']):
                continue
            
            # Simple variable assignment detection
            if '=' in stripped and '==' not in stripped:
                left_side = stripped.split('=')[0].strip()
                
                # Skip multiple assignments and unpacking for now
                if ',' not in left_side and ' ' not in left_side:
                    variables.append(left_side)
        
        # Check if variables are used later
        for var in variables:
            # Count occurrences after declaration
            found_declaration = False
            usage_count = 0
            
            for line in code_lines:
                if not found_declaration:
                    # Look for declaration
                    if f'{var} =' in line or f'{var}=' in line:
                        found_declaration = True
                else:
                    # Count usage after declaration
                    if var in line and not (f'{var} =' in line or f'{var}=' in line):
                        usage_count += 1
            
            # If declared but never used
            if found_declaration and usage_count == 0:
                self.mistakes.append({
                    'type': 'UNUSED_VARIABLE',
                    'problem': f'Variable "{var}" is declared but never used',
                    'why_bad': 'Unused variables waste memory and make code confusing. '
                              'They indicate incomplete refactoring or dead code.',
                    'solution': f'Remove the variable "{var}" or use it in your logic.',
                    'learn_next': 'Learn about code cleanup and the DRY (Don\'t Repeat Yourself) principle.'
                })
    
    def _check_unused_variables_c_cpp(self, code_lines: List[str]):
        """Basic unused variable detection for C/C++."""
        variables = []
        
        for line in code_lines:
            stripped = line.strip()
            
            # Skip lines that aren't declarations
            if ';' not in stripped:
                continue
            
            # Look for variable declarations (basic pattern)
            if ('int ' in stripped or 'float ' in stripped or 
                'double ' in stripped or 'char ' in stripped):
                # Remove type and get variable name
                parts = stripped.replace(';', '').split()
                if len(parts) >= 2:
                    var_name = parts[-1]
                    # Remove any assignment
                    if '=' in var_name:
                        var_name = var_name.split('=')[0]
                    variables.append(var_name)
        
        # Similar checking logic as Python
        for var in variables:
            found_declaration = False
            usage_count = 0
            
            for line in code_lines:
                line_clean = line.strip()
                
                if not found_declaration:
                    # Look for declaration
                    if f'{var};' in line_clean or f'{var} =' in line_clean or f'{var}=' in line_clean:
                        found_declaration = True
                else:
                    # Count usage (not in declarations)
                    if var in line_clean and not any(
                        pattern in line_clean 
                        for pattern in [f'{var};', f'{var} =', f'{var}=']
                    ):
                        usage_count += 1
            
            if found_declaration and usage_count == 0 and len(var) > 1:  # Avoid single-letter false positives
                self.mistakes.append({
                    'type': 'UNUSED_VARIABLE',
                    'problem': f'Variable "{var}" is declared but never used',
                    'why_bad': 'Unused variables indicate dead code and waste resources.',
                    'solution': f'Remove "{var}" or implement its usage.',
                    'learn_next': 'Learn about memory management and code optimization.'
                })
    
    def _check_deep_indentation(self, code_lines: List[str], language: str):
        """Check for excessive indentation (pyramid code)."""
        if language != 'python':
            return  # Only applicable to Python for now
        
        max_indent = 0
        line_number = 0
        
        for i, line in enumerate(code_lines, 1):
            if not line.strip():  # Skip empty lines
                continue
            
            # Calculate indentation level
            leading_spaces = len(line) - len(line.lstrip())
            indent_level = leading_spaces // 4  # Assuming 4 spaces per indent
            
            if indent_level > max_indent:
                max_indent = indent_level
                line_number = i
        
        if max_indent > self.thresholds['max_indentation_level']:
            self.mistakes.append({
                'type': 'DEEP_INDENTATION',
                'problem': f'Code has {max_indent} levels of indentation (line {line_number})',
                'why_bad': 'Deep indentation (pyramid code) is hard to read and maintain. '
                          'It often indicates too much nesting.',
                'solution': 'Flatten your code by using early returns, breaking into functions, '
                           'or using guard clauses.',
                'learn_next': 'Learn about code flattening techniques and clean code principles.'
            })
    
    def _check_magic_numbers(self, code_lines: List[str], language: str):
        """Check for magic numbers (unnamed numerical constants)."""
        magic_numbers = []
        
        for line in code_lines:
            words = line.split()
            for word in words:
                # Check if word is a number (simple check)
                if self._is_number(word):
                    # Skip common numbers (0, 1, 10, 100, etc.)
                    if word not in ['0', '1', '2', '10', '100', '1000']:
                        magic_numbers.append(word)
        
        if len(magic_numbers) > self.thresholds['max_magic_numbers']:
            unique_numbers = list(set(magic_numbers))[:5]  # Show first 5 unique
            self.mistakes.append({
                'type': 'MAGIC_NUMBERS',
                'problem': f'Found {len(magic_numbers)} magic numbers: {", ".join(unique_numbers)}...',
                'why_bad': 'Magic numbers make code hard to understand and maintain. '
                          'Their meaning is not clear without context.',
                'solution': 'Replace magic numbers with named constants or variables '
                           'with descriptive names.',
                'learn_next': 'Learn about constants and configuration management.'
            })
    
    def _is_number(self, s: str) -> bool:
        """Check if string is a number."""
        try:
            float(s)
            return True
        except ValueError:
            return False


def test_mistake_detector():
    """Test the mistake detector."""
    detector = MistakeDetector()
    
    print("🧪 Testing Mistake Detector")
    print("=" * 50)
    
    # Test 1: Python code with issues
    python_code = [
        "def complex_function():",
        "    x = 10  # Unused variable",
        "    result = 0",
        "    ",
        "    for i in range(100):",
        "        for j in range(100):",
        "            for k in range(100):  # Deep nesting",
        "                if result > 1000:",
        "                    if result < 2000:",
        "                        if result % 2 == 0:  # Many conditions",
        "                            result += i * j * k",
        "    ",
        "    # Magic numbers",
        "    if result > 42:",
        "        print('Answer found')",
        "    elif result > 3.14:",
        "        print('Pi related')",
        "    elif result > 99:",
        "        print('Almost perfect')",
        "    ",
        "    return result",
    ]
    
    # Mock analysis results
    analysis = {
        'total_lines': 20,
        'loops': 3,
        'nested_loops': 2,
        'max_nesting_depth': 3,
        'conditionals': 4,
        'functions': 1,
        'variables': 2,
    }
    
    print("\nTest 1: Python Code with Multiple Issues")
    print("-" * 40)
    mistakes = detector.detect_mistakes(python_code, 'python', analysis)
    
    print(f"Found {len(mistakes)} mistakes:\n")
    
    for i, mistake in enumerate(mistakes, 1):
        print(f"{i}. [{mistake['type']}]")
        print(f"   Problem: {mistake['problem']}")
        print(f"   Why it's bad: {mistake['why_bad']}")
        print(f"   Solution: {mistake['solution']}")
        print(f"   Learn next: {mistake['learn_next']}")
        print()
    
    # Test 2: Clean code (no mistakes)
    clean_code = [
        "def calculate_sum(numbers):",
        "    total = 0",
        "    for num in numbers:",
        "        total += num",
        "    return total",
    ]
    
    clean_analysis = {
        'total_lines': 5,
        'loops': 1,
        'nested_loops': 0,
        'max_nesting_depth': 1,
        'conditionals': 0,
        'functions': 1,
        'variables': 2,
    }
    
    print("\n\nTest 2: Clean Code")
    print("-" * 40)
    mistakes = detector.detect_mistakes(clean_code, 'python', clean_analysis)
    
    if not mistakes:
        print("✅ No mistakes found! Great code!")
    else:
        print(f"Found {len(mistakes)} mistakes")
    
    return mistakes


def detect_in_file(file_path: str):
    """Detect mistakes in a code file."""
    from code_reader import CodeReader
    from analyzer import CodeAnalyzer
    
    # Read and analyze the file
    reader = CodeReader()
    analyzer = CodeAnalyzer()
    detector = MistakeDetector()
    
    code_lines, language, error = reader.read_code_file(file_path)
    
    if error:
        print(f"❌ Error: {error}")
        return
    
    if not code_lines:
        print("❌ No code found")
        return
    
    # Analyze the code
    analysis = analyzer.analyze_code(code_lines, language)
    
    # Detect mistakes
    mistakes = detector.detect_mistakes(code_lines, language, analysis)
    
    # Display results
    print(f"\n🔍 Mistake Analysis for {file_path}")
    print("=" * 60)
    print(f"Language: {language}")
    print(f"Total lines: {analysis.get('total_lines', 0)}")
    print(f"Mistakes found: {len(mistakes)}")
    print()
    
    if not mistakes:
        print("🎉 Congratulations! No beginner mistakes detected.")
        print("Your code follows good practices.")
    else:
        print("📋 Issues Found:")
        print("-" * 60)
        
        for i, mistake in enumerate(mistakes, 1):
            print(f"\n{i}. ⚠️  {mistake['problem']}")
            print(f"   📌 Why it's bad: {mistake['why_bad']}")
            print(f"   💡 Solution: {mistake['solution']}")
            print(f"   🎯 Learn about: {mistake['learn_next']}")
    
    return mistakes


if __name__ == "__main__":
    # Run tests
    test_mistake_detector()
    
    # Uncomment to test with actual file
    # import sys
    # if len(sys.argv) > 1:
    #     detect_in_file(sys.argv[1])
    # else:
    #     print("\nTo analyze a file: python mistakes.py <file_path>")
    #     print("Example: python mistakes.py ../test.py")