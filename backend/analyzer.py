"""
smart-code-evaluator/backend/analyzer.py
Analyzes code structure to extract programming patterns.
Version: 2.0
"""

import logging
from typing import Dict, List, Tuple, Any
from collections import defaultdict

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """Analyzes code structure and extracts patterns."""
    
    def __init__(self):
        # Keywords to track
        self.loop_keywords = ['for', 'while']
        self.conditional_keywords = ['if', 'else', 'elif']
        self.function_keywords = ['def', 'void', 'int', 'float', 'double', 'char', 'bool']
        
        # Complexity estimation
        self.complexity_map = {
            0: "O(1)",
            1: "O(n)",
            2: "O(n²)",
            3: "O(n³)",
            4: "O(2ⁿ)",
        }
    
    def analyze_code(self, code_lines: List[str], language: str) -> Dict[str, Any]:
        """
        Main analysis function.
        
        Args:
            code_lines: Cleaned lines of code
            language: Programming language ('python', 'c', 'cpp')
            
        Returns:
            Dictionary with analysis results
        """
        if not code_lines:
            return self._empty_analysis_result()
        
        try:
            if language == 'python':
                return self._analyze_python(code_lines)
            else:  # C or C++
                return self._analyze_c_cpp(code_lines)
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return self._empty_analysis_result()
    
    def _analyze_python(self, code_lines: List[str]) -> Dict[str, Any]:
        """Analyze Python code structure."""
        analysis = self._create_analysis_template()
        
        stack = []  # Track indentation levels for nesting
        current_indent = 0
        in_loop = False
        loop_depth = 0
        function_depth = 0
        
        for line_num, line in enumerate(code_lines, 1):
            # Skip empty lines (though they should already be cleaned)
            if not line.strip():
                continue
            
            # Count total lines
            analysis['total_lines'] += 1
            
            # Calculate indentation
            indent_level = self._get_indent_level(line)
            
            # Check for de-indentation (end of block)
            while stack and indent_level < stack[-1]:
                stack.pop()
                if loop_depth > 0:
                    loop_depth -= 1
                if function_depth > 0:
                    function_depth -= 1
            
            # Check for function definition
            if line.strip().startswith('def '):
                analysis['functions'] += 1
                function_depth = 1
                stack.append(indent_level)
                continue
            
            # Check for loops
            for loop_kw in self.loop_keywords:
                if self._is_keyword_in_line(line, loop_kw):
                    analysis['loops'] += 1
                    in_loop = True
                    loop_depth += 1
                    
                    # Check for nesting
                    if loop_depth > 1:
                        analysis['nested_loops'] += 1
                        analysis['max_nesting_depth'] = max(
                            analysis['max_nesting_depth'], loop_depth
                        )
                    
                    stack.append(indent_level)
                    break
            
            # Check for conditionals
            for cond_kw in self.conditional_keywords:
                if self._is_keyword_in_line(line, cond_kw):
                    analysis['conditionals'] += 1
                    
                    # Check if inside loop
                    if in_loop:
                        analysis['conditions_in_loops'] += 1
                    
                    stack.append(indent_level)
                    break
            
            # Track variable declarations (simple pattern matching)
            if '=' in line and not any(kw in line for kw in ['if', 'for', 'while', 'def']):
                # Simple variable assignment detection
                left_side = line.split('=')[0].strip()
                if left_side and not left_side.startswith('#'):
                    analysis['variables'] += 1
        
        # Calculate complexity
        analysis['complexity'] = self._estimate_complexity(
            analysis['loops'],
            analysis['nested_loops'],
            analysis['max_nesting_depth']
        )
        
        return analysis
    
    def _analyze_c_cpp(self, code_lines: List[str]) -> Dict[str, Any]:
        """Analyze C/C++ code structure."""
        analysis = self._create_analysis_template()
        
        brace_count = 0
        in_loop = False
        loop_depth = 0
        function_depth = 0
        last_keyword = None
        
        # Join lines to handle multi-line statements
        combined_code = ' '.join(code_lines)
        
        # Simple tokenization for analysis
        tokens = self._tokenize_c_code(combined_code)
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            # Count braces for nesting
            if token == '{':
                brace_count += 1
            elif token == '}':
                brace_count -= 1
                if brace_count < loop_depth:
                    loop_depth = max(0, loop_depth - 1)
                if brace_count < function_depth:
                    function_depth = max(0, function_depth - 1)
            
            # Check for function definition
            elif token in self.function_keywords:
                # Look ahead for function name and parentheses
                j = i + 1
                while j < len(tokens) and tokens[j] == '*':  # Skip pointers
                    j += 1
                
                if j < len(tokens) and '(' in tokens[j]:
                    # Check if it's a function definition (has { after parameters)
                    k = j + 1
                    paren_count = 1
                    while k < len(tokens) and paren_count > 0:
                        if tokens[k] == '(':
                            paren_count += 1
                        elif tokens[k] == ')':
                            paren_count -= 1
                        k += 1
                    
                    if k < len(tokens) and tokens[k] == '{':
                        analysis['functions'] += 1
                        function_depth = brace_count + 1
            
            # Check for loops
            elif token in self.loop_keywords:
                analysis['loops'] += 1
                in_loop = True
                last_keyword = token
                
                # Check if we're inside another loop
                if loop_depth > 0:
                    analysis['nested_loops'] += 1
                    analysis['max_nesting_depth'] = max(
                        analysis['max_nesting_depth'], loop_depth + 1
                    )
                
                loop_depth += 1
            
            # Check for conditionals
            elif token == 'if' or token == 'else':
                analysis['conditionals'] += 1
                last_keyword = token
                
                # Check if inside loop
                if in_loop:
                    analysis['conditions_in_loops'] += 1
            
            # Count semicolons as approximate statement count
            elif token == ';':
                analysis['total_statements'] += 1
            
            i += 1
        
        # Count lines from original code
        analysis['total_lines'] = len(code_lines)
        
        # Count variables (simple pattern)
        for line in code_lines:
            if ';' in line and '=' in line:
                if not any(kw in line for kw in ['for', 'while', 'if']):
                    analysis['variables'] += 1
        
        # Calculate complexity
        analysis['complexity'] = self._estimate_complexity(
            analysis['loops'],
            analysis['nested_loops'],
            analysis['max_nesting_depth']
        )
        
        return analysis
    
    def _tokenize_c_code(self, code: str) -> List[str]:
        """Simple tokenizer for C/C++ code."""
        tokens = []
        current = ''
        in_string = False
        string_char = None
        in_comment = False
        
        i = 0
        while i < len(code):
            char = code[i]
            
            # Handle strings
            if char in ('"', "'") and not in_comment:
                if not in_string:
                    in_string = True
                    string_char = char
                    if current:
                        tokens.append(current)
                        current = ''
                    current += char
                elif char == string_char and (i == 0 or code[i-1] != '\\'):
                    in_string = False
                    current += char
                    tokens.append(current)
                    current = ''
                else:
                    current += char
            
            # Handle comments
            elif not in_string:
                if i + 1 < len(code):
                    if code[i:i+2] == '//':
                        # Skip to end of line
                        while i < len(code) and code[i] != '\n':
                            i += 1
                        continue
                    elif code[i:i+2] == '/*':
                        in_comment = True
                        i += 1
                    elif code[i:i+2] == '*/' and in_comment:
                        in_comment = False
                        i += 1
                
                if in_comment:
                    i += 1
                    continue
            
            # Tokenize special characters
            elif not in_string and char in '{}();=<>!&|+-*/%':
                if current:
                    tokens.append(current)
                    current = ''
                tokens.append(char)
            
            # Handle whitespace
            elif char.isspace():
                if current:
                    tokens.append(current)
                    current = ''
            
            # Build identifier/number
            else:
                current += char
            
            i += 1
        
        # Add last token
        if current:
            tokens.append(current)
        
        return tokens
    
    def _get_indent_level(self, line: str) -> int:
        """Calculate indentation level for Python."""
        # Count leading spaces (assuming 4 spaces per indent)
        spaces = len(line) - len(line.lstrip())
        return spaces // 4
    
    def _is_keyword_in_line(self, line: str, keyword: str) -> bool:
        """
        Check if keyword appears in line (not as part of another word).
        
        Args:
            line: Code line
            keyword: Keyword to search for
            
        Returns:
            True if keyword is found as standalone
        """
        words = line.strip().split()
        return any(word == keyword for word in words)
    
    def _estimate_complexity(self, loops: int, nested_loops: int, max_depth: int) -> str:
        """Estimate time complexity based on loop patterns."""
        if loops == 0:
            return self.complexity_map[0]  # O(1)
        elif nested_loops == 0:
            return self.complexity_map[1]  # O(n)
        elif max_depth == 2:
            return self.complexity_map[2]  # O(n²)
        elif max_depth == 3:
            return self.complexity_map[3]  # O(n³)
        else:
            return self.complexity_map[4]  # O(2ⁿ) for deep nesting
    
    def _create_analysis_template(self) -> Dict[str, Any]:
        """Create a template for analysis results."""
        return {
            'total_lines': 0,
            'loops': 0,
            'nested_loops': 0,
            'conditionals': 0,
            'conditions_in_loops': 0,
            'functions': 0,
            'variables': 0,
            'total_statements': 0,
            'max_nesting_depth': 0,
            'complexity': 'O(1)',
        }
    
    def _empty_analysis_result(self) -> Dict[str, Any]:
        """Return empty analysis result for error cases."""
        template = self._create_analysis_template()
        template['error'] = 'Analysis failed'
        return template


def test_analyzer():
    """Test the code analyzer with sample code."""
    analyzer = CodeAnalyzer()
    
    print("🧪 Testing Code Analyzer")
    print("=" * 50)
    
    # Test 1: Simple Python code
    python_code = [
        "def calculate_sum(n):",
        "    total = 0",
        "    for i in range(n):",
        "        total += i",
        "        if total > 100:",
        "            break",
        "    return total",
        "",
        "def main():",
        "    result = calculate_sum(10)",
        "    print(f'Result: {result}')",
        "    if result > 50:",
        "        print('Large result')",
        "    else:",
        "        print('Small result')",
    ]
    
    print("\nTest 1: Python Code Analysis")
    print("-" * 30)
    result = analyzer.analyze_code(python_code, 'python')
    
    for key, value in result.items():
        if key != 'error':
            print(f"{key.replace('_', ' ').title():25}: {value}")
    
    # Test 2: C code with loops
    c_code = [
        "#include <stdio.h>",
        "",
        "int main() {",
        "    int i, j;",
        "    int sum = 0;",
        "",
        "    for (i = 0; i < 10; i++) {",
        "        for (j = 0; j < 10; j++) {",
        "            sum += i * j;",
        "            if (sum > 1000) {",
        "                break;",
        "            }",
        "        }",
        "    }",
        "",
        "    if (sum > 500) {",
        "        printf('Large sum: %d\\n', sum);",
        "    } else {",
        "        printf('Small sum: %d\\n', sum);",
        "    }",
        "",
        "    return 0;",
        "}",
    ]
    
    print("\n\nTest 2: C Code Analysis")
    print("-" * 30)
    result = analyzer.analyze_code(c_code, 'c')
    
    for key, value in result.items():
        if key != 'error':
            print(f"{key.replace('_', ' ').title():25}: {value}")
    
    # Test 3: Empty code
    print("\n\nTest 3: Empty Code Analysis")
    print("-" * 30)
    result = analyzer.analyze_code([], 'python')
    
    if 'error' in result:
        print(f"Error (expected): {result['error']}")
    else:
        print("Empty analysis completed")
    
    return result


def analyze_file(file_path: str):
    """Analyze a code file."""
    from code_reader import CodeReader
    
    # Read the file
    reader = CodeReader()
    code_lines, language, error = reader.read_code_file(file_path)
    
    if error:
        print(f"❌ Error reading file: {error}")
        return
    
    if not code_lines:
        print("❌ No code found in file")
        return
    
    # Analyze the code
    analyzer = CodeAnalyzer()
    result = analyzer.analyze_code(code_lines, language)
    
    # Display results
    print(f"\n📊 Analysis Results for {file_path}")
    print("=" * 50)
    print(f"Language: {language}")
    print(f"Total Lines: {result['total_lines']}")
    print(f"Functions: {result['functions']}")
    print(f"Loops: {result['loops']}")
    print(f"Nested Loops: {result['nested_loops']}")
    print(f"Conditionals: {result['conditionals']}")
    print(f"Conditions in Loops: {result['conditions_in_loops']}")
    print(f"Variables: {result['variables']}")
    print(f"Max Nesting Depth: {result['max_nesting_depth']}")
    print(f"Estimated Complexity: {result['complexity']}")
    
    return result


if __name__ == "__main__":
    # Run tests
    test_analyzer()
    
    # Uncomment to test with actual files
    # import sys
    # if len(sys.argv) > 1:
    #     analyze_file(sys.argv[1])
    # else:
    #     print("\nTo analyze a file: python analyzer.py <file_path>")
    #     print("Example: python analyzer.py ../test.py")