# code_reader.py
import ast
import json
import sys

class CodeReader:
    def __init__(self):
        self.code_structure = {}
        self.questions_data = self.load_questions()
    
    def load_questions(self):
        """Load questions from JSON file"""
        try:
            with open('data/questions.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ Questions file not found. Using empty structure.")
            return {}
        except json.JSONDecodeError:
            print("❌ Error decoding JSON. Using empty structure.")
            return {}
    
    def read_code(self, code: str, question_id: int = None):
        """
        Read and analyze submitted code
        Returns: Dictionary with analysis results
        """
        try:
            # Parse the code
            tree = ast.parse(code)
            
            # Extract basic information
            functions = []
            classes = []
            imports = []
            variables = []
            loops = []
            conditionals = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module if node.module else ""
                    imports.append(f"from {module}")
                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    variables.append(node.id)
                elif isinstance(node, ast.For):
                    loops.append("for")
                elif isinstance(node, ast.While):
                    loops.append("while")
                elif isinstance(node, ast.If):
                    conditionals.append("if")
            
            # Get question details if question_id is provided
            question_info = self.get_question_info(question_id) if question_id else {}
            
            # Check required concepts for the question
            required_concepts = question_info.get('concepts', [])
            detected_concepts = self.detect_concepts(code)
            missing_concepts = [c for c in required_concepts if c not in detected_concepts]
            
            self.code_structure = {
                "basic_info": {
                    "functions": list(set(functions)),
                    "classes": list(set(classes)),
                    "imports": list(set(imports)),
                    "lines": len(code.split('\n')),
                    "characters": len(code),
                    "indentation_levels": self.check_indentation(code)
                },
                "concepts_analysis": {
                    "detected_concepts": detected_concepts,
                    "required_concepts": required_concepts,
                    "missing_concepts": missing_concepts,
                    "concepts_match": len(missing_concepts) == 0
                },
                "syntax_check": {
                    "has_syntax_error": False,
                    "error_message": None
                },
                "question_info": question_info
            }
            
            return self.code_structure
            
        except SyntaxError as e:
            return {
                "basic_info": {
                    "lines": len(code.split('\n')),
                    "characters": len(code)
                },
                "concepts_analysis": {
                    "detected_concepts": [],
                    "required_concepts": [],
                    "missing_concepts": [],
                    "concepts_match": False
                },
                "syntax_check": {
                    "has_syntax_error": True,
                    "error_message": str(e),
                    "error_line": e.lineno if hasattr(e, 'lineno') else None,
                    "error_column": e.offset if hasattr(e, 'offset') else None
                },
                "question_info": {}
            }
        except Exception as e:
            return {"error": f"Error reading code: {str(e)}"}
    
    def get_question_info(self, question_id: int):
        """Get question details by ID"""
        for category in self.questions_data.values():
            for question in category:
                if question['id'] == question_id:
                    return question
        return {}
    
    def detect_concepts(self, code: str):
        """Detect programming concepts in the code"""
        concepts = []
        code_lower = code.lower()
        
        # Check for loops
        if 'for ' in code_lower:
            concepts.append("for")
        
        if 'while ' in code_lower:
            concepts.append("while")
        
        # Check for nested loops
        if code_lower.count('for ') > 1 or code_lower.count('while ') > 1:
            concepts.append("nested-loop")
        
        # Check for conditionals
        if 'if ' in code_lower:
            concepts.append("if")
            if 'elif ' in code_lower or code_lower.count('if ') > 1:
                concepts.append("nested-if")
        
        if 'else:' in code_lower:
            concepts.append("else")
        
        # Check for specific patterns
        if 'def ' in code_lower:
            concepts.append("function")
        
        if 'import ' in code_lower:
            concepts.append("import")
        
        if 'print(' in code_lower:
            concepts.append("print")
        
        if 'input(' in code_lower:
            concepts.append("input")
        
        # Check arithmetic operations
        if any(op in code_lower for op in ['+', '-', '*', '/', '%', '**', '//']):
            concepts.append("arithmetic")
        
        # Check comparisons
        if any(op in code_lower for op in ['==', '!=', '<', '>', '<=', '>=']):
            concepts.append("comparison")
        
        # Check logical operators
        if any(op in code_lower for op in ['and ', 'or ', 'not ']):
            concepts.append("logical")
        
        return list(set(concepts))
    
    def check_indentation(self, code: str):
        """Check indentation consistency"""
        lines = code.split('\n')
        indent_levels = []
        
        for line in lines:
            if line.strip():  # Skip empty lines
                leading_spaces = len(line) - len(line.lstrip())
                indent_levels.append(leading_spaces)
        
        # Check if indentation is consistent (multiple of 4)
        is_consistent = all(indent % 4 == 0 for indent in indent_levels)
        
        return {
            "levels": list(set(indent_levels)),
            "is_consistent": is_consistent,
            "max_indent": max(indent_levels) if indent_levels else 0,
            "recommended_fix": "Use 4 spaces for indentation" if not is_consistent else "Indentation is good"
        }
    
    def analyze_code_quality(self, code: str):
        """Analyze code quality metrics"""
        lines = code.split('\n')
        
        # Remove comments and empty lines for analysis
        code_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                code_lines.append(line)
        
        total_lines = len(lines)
        code_lines_count = len(code_lines)
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        empty_lines = sum(1 for line in lines if not line.strip())
        
        # Calculate complexity score
        complexity_score = 0
        for line in code_lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ['for ', 'while ', 'if ', 'elif ', 'else:']):
                complexity_score += 1
            if 'def ' in line_lower:
                complexity_score += 2
            if 'import ' in line_lower or 'from ' in line_lower:
                complexity_score += 0.5
            if 'try:' in line_lower or 'except ' in line_lower:
                complexity_score += 1
            if 'class ' in line_lower:
                complexity_score += 3
        
        complexity_level = "low"
        if complexity_score >= 10:
            complexity_level = "high"
        elif complexity_score >= 5:
            complexity_level = "medium"
        
        return {
            "lines_analysis": {
                "total_lines": total_lines,
                "code_lines": code_lines_count,
                "comment_lines": comment_lines,
                "empty_lines": empty_lines,
                "comment_ratio": round(comment_lines / total_lines, 2) if total_lines > 0 else 0
            },
            "complexity": {
                "score": complexity_score,
                "level": complexity_level
            },
            "readability": {
                "has_comments": comment_lines > 0,
                "has_empty_lines": empty_lines > 0,
                "avg_line_length": round(sum(len(line) for line in lines) / total_lines, 1) if total_lines > 0 else 0,
                "rating": "Good" if comment_lines > 0 and empty_lines > 0 else "Needs Improvement"
            }
        }
    
    def check_variable_names(self, code: str):
        """Check variable naming conventions"""
        try:
            tree = ast.parse(code)
            variables = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    variables.append(node.id)
                elif isinstance(node, ast.FunctionDef):
                    variables.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    variables.append(node.name)
                elif isinstance(node, ast.arg):
                    variables.append(node.arg)
            
            # Check naming conventions
            poorly_named = []
            well_named = []
            
            for var in set(variables):
                if len(var) == 1 and var.isalpha():  # Single letter variables
                    poorly_named.append(var)
                elif var.isdigit():  # Numbers as variable names
                    poorly_named.append(var)
                elif '_' in var:  # Snake case
                    well_named.append(var)
                elif var[0].isupper():  # Class or constant
                    well_named.append(var)
                elif var.islower():  # Lowercase variables
                    well_named.append(var)
                else:
                    poorly_named.append(var)
            
            return {
                "all_variables": list(set(variables)),
                "well_named": well_named,
                "poorly_named": poorly_named,
                "has_descriptive_names": len(poorly_named) < len(well_named),
                "score": len(well_named) / len(set(variables)) if variables else 0
            }
        except:
            return {"error": "Could not analyze variable names"}
    
    def print_analysis(self, code: str, question_id: int = None):
        """Print detailed analysis of the code"""
        print("\n" + "="*60)
        print("📊 CODE ANALYSIS REPORT")
        print("="*60)
        
        # Basic code reading
        result = self.read_code(code, question_id)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
        
        # Print basic info
        basic = result.get('basic_info', {})
        print(f"\n📋 BASIC INFORMATION:")
        print(f"   • Lines of code: {basic.get('lines', 0)}")
        print(f"   • Characters: {basic.get('characters', 0)}")
        print(f"   • Functions: {', '.join(basic.get('functions', [])) or 'None'}")
        print(f"   • Imports: {', '.join(basic.get('imports', [])) or 'None'}")
        
        # Print indentation info
        indent = basic.get('indentation_levels', {})
        if indent:
            status = "✅ Good" if indent.get('is_consistent') else "❌ Needs Fix"
            print(f"   • Indentation: {status}")
            if not indent.get('is_consistent'):
                print(f"     ↳ {indent.get('recommended_fix', '')}")
        
        # Print concepts analysis
        concepts = result.get('concepts_analysis', {})
        print(f"\n🎯 CONCEPTS ANALYSIS:")
        print(f"   • Detected: {', '.join(concepts.get('detected_concepts', [])) or 'None'}")
        print(f"   • Required: {', '.join(concepts.get('required_concepts', [])) or 'None'}")
        
        if concepts.get('missing_concepts'):
            print(f"   ❌ Missing: {', '.join(concepts.get('missing_concepts', []))}")
        else:
            print(f"   ✅ All required concepts are present!")
        
        # Print syntax check
        syntax = result.get('syntax_check', {})
        if syntax.get('has_syntax_error'):
            print(f"\n❌ SYNTAX ERROR:")
            print(f"   • {syntax.get('error_message')}")
            if syntax.get('error_line'):
                print(f"   • Line: {syntax.get('error_line')}, Column: {syntax.get('error_column')}")
        else:
            print(f"\n✅ No syntax errors found!")
        
        # Print question info
        if question_id:
            q_info = result.get('question_info', {})
            if q_info:
                print(f"\n📝 QUESTION INFORMATION:")
                print(f"   • ID: {q_info.get('id')}")
                print(f"   • Difficulty: {q_info.get('difficulty', 'Unknown').upper()}")
                print(f"   • Question: {q_info.get('question')}")
        
        # Additional quality analysis
        print(f"\n⭐ CODE QUALITY ANALYSIS:")
        quality = self.analyze_code_quality(code)
        
        lines_info = quality.get('lines_analysis', {})
        print(f"   • Total lines: {lines_info.get('total_lines')}")
        print(f"   • Code lines: {lines_info.get('code_lines')}")
        print(f"   • Comments: {lines_info.get('comment_lines')}")
        print(f"   • Empty lines: {lines_info.get('empty_lines')}")
        print(f"   • Comment ratio: {lines_info.get('comment_ratio')}")
        
        complexity = quality.get('complexity', {})
        print(f"   • Complexity score: {complexity.get('score')} ({complexity.get('level').upper()})")
        
        readability = quality.get('readability', {})
        print(f"   • Readability: {readability.get('rating')}")
        
        # Variable analysis
        variables = self.check_variable_names(code)
        if "error" not in variables:
            print(f"\n🔤 VARIABLE NAMING:")
            print(f"   • Total variables: {len(variables.get('all_variables', []))}")
            print(f"   • Well named: {len(variables.get('well_named', []))}")
            print(f"   • Poorly named: {len(variables.get('poorly_named', []))}")
            score_percent = variables.get('score', 0) * 100
            print(f"   • Naming score: {score_percent:.1f}%")
            
            if variables.get('poorly_named'):
                print(f"   • Poor variables: {', '.join(variables.get('poorly_named', []))}")
        
        print("\n" + "="*60)
        print("📈 ANALYSIS COMPLETE")
        print("="*60 + "\n")
        
        return result


# Main function for testing
if __name__ == "__main__":
    print("🧪 Testing CodeReader...")
    
    # Create instance
    reader = CodeReader()
    
    # Test with sample code
    sample_code = """
# This is a sample Python program
def print_numbers(n):
    for i in range(1, n+1):
        if i % 2 == 0:
            print(f"{i} is even")
        else:
            print(f"{i} is odd")

# Call the function
print_numbers(10)
"""
    
    print("Sample Code:")
    print("-" * 40)
    print(sample_code)
    print("-" * 40)
    
    # Analyze the code for question 1 (for loop question)
    print("\nAnalyzing code for Question ID 1...")
    result = reader.print_analysis(sample_code, question_id=1)
    
    # Test with another sample
    print("\n" + "="*60)
    print("Testing with while loop code...")
    
    while_code = """
# While loop example
counter = 0
while counter < 5:
    print(f"Counter: {counter}")
    counter += 1
print("Done!")
"""
    
    result2 = reader.print_analysis(while_code, question_id=21)
    
    # Test with error code
    print("\n" + "="*60)
    print("Testing with syntax error...")
    
    error_code = """
def test():
    print("Hello"
    x = 10
    return x
"""
    
    result3 = reader.print_analysis(error_code)
    
    print("\n✅ CodeReader is working correctly!")
    print("Use reader.read_code(your_code, question_id) to analyze code.")
    print("Use reader.print_analysis(your_code, question_id) to see formatted output.")