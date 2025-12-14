"""
smart-code-evaluator/backend/code_reader.py
Secure and robust source code reader with validation and error handling.
Version: 2.0
Author: Smart Code Evaluator Team
"""

import os
import logging
from typing import List, Optional, Tuple
from pathlib import Path

# Configure logging for security and debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security: Define allowed file extensions and maximum file size (1MB)
ALLOWED_EXTENSIONS = {'.c', '.cpp', '.py'}
MAX_FILE_SIZE = 1024 * 1024  # 1MB


class CodeReader:
    """Secure code reader with validation and sanitization."""
    
    def __init__(self):
        self.supported_languages = {
            'c': 'C',
            'cpp': 'C++',
            'py': 'Python'
        }
    
    def read_code_file(self, file_path: str) -> Tuple[List[str], Optional[str], Optional[str]]:
        """
        Securely read and clean code from a file.
        
        Args:
            file_path: Path to the source code file
            
        Returns:
            Tuple containing:
            - List of cleaned code lines (empty list on error)
            - Language type or None
            - Error message or None
        """
        
        # Security: Validate input
        if not file_path or not isinstance(file_path, str):
            return [], None, "Invalid file path provided"
        
        # Security: Convert to absolute path and normalize
        try:
            file_path = os.path.abspath(file_path)
            normalized_path = os.path.normpath(file_path)
            
            # Security: Check for path traversal attacks
            if '..' in file_path or file_path != normalized_path:
                logger.warning(f"Potential path traversal attempt: {file_path}")
                return [], None, "Invalid file path"
                
        except Exception as e:
            logger.error(f"Path normalization failed: {e}")
            return [], None, "Invalid file path"
        
        # Security: Check file exists
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return [], None, f"File '{os.path.basename(file_path)}' not found"
        
        # Security: Check if it's a file (not directory)
        if not os.path.isfile(file_path):
            return [], None, "Path is not a file"
        
        # Security: Check file size
        try:
            file_size = os.path.getsize(file_path)
            if file_size > MAX_FILE_SIZE:
                return [], None, f"File too large. Maximum size is {MAX_FILE_SIZE//1024}KB"
            if file_size == 0:
                return [], None, "File is empty"
        except OSError as e:
            logger.error(f"File size check failed: {e}")
            return [], None, "Cannot access file"
        
        # Security: Validate file extension
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            logger.warning(f"Unsupported file type: {file_ext}")
            return [], None, f"File type '{file_ext}' not supported. Use: {', '.join(ALLOWED_EXTENSIONS)}"
        
        # Determine language
        language = self._get_language_from_extension(file_ext)
        
        # Read file with error handling
        try:
            # Security: Open with explicit encoding to avoid encoding attacks
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                
                # Security: Basic content validation
                if self._contains_malicious_patterns(content):
                    logger.warning(f"Potential malicious content in: {file_path}")
                    return [], language, "File contains suspicious patterns"
                
                # Clean the code
                cleaned_lines = self._clean_code(content, language)
                
                if not cleaned_lines:
                    return [], language, "No valid code found after cleaning"
                
                logger.info(f"Successfully read {len(cleaned_lines)} lines from {file_path}")
                return cleaned_lines, language, None
                
        except PermissionError:
            return [], language, "Permission denied to read file"
        except UnicodeDecodeError:
            return [], language, "File encoding error"
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return [], language, f"Error reading file: {str(e)}"
    
    def read_code_from_text(self, code_text: str, language: str) -> Tuple[List[str], Optional[str]]:
        """
        Read and clean code from text input.
        
        Args:
            code_text: Source code as text
            language: Programming language ('python', 'c', or 'cpp')
            
        Returns:
            Tuple containing cleaned lines and error message (if any)
        """
        # Security: Validate inputs
        if not code_text or not isinstance(code_text, str):
            return [], "No code provided"
        
        if not language or language.lower() not in ['python', 'c', 'cpp']:
            return [], "Unsupported language"
        
        # Security: Check for excessive input size
        if len(code_text) > MAX_FILE_SIZE:
            return [], f"Code too large. Maximum size is {MAX_FILE_SIZE//1024}KB"
        
        # Security: Basic malicious pattern check
        if self._contains_malicious_patterns(code_text):
            logger.warning("Potential malicious content in text input")
            return [], "Code contains suspicious patterns"
        
        # Clean the code
        try:
            cleaned_lines = self._clean_code(code_text, language.lower())
            
            if not cleaned_lines:
                return [], "No valid code found after cleaning"
            
            return cleaned_lines, None
            
        except Exception as e:
            logger.error(f"Error processing code text: {e}")
            return [], f"Error processing code: {str(e)}"
    
    def _get_language_from_extension(self, extension: str) -> str:
        """Map file extension to language."""
        ext_to_lang = {
            '.py': 'python',
            '.c': 'c',
            '.cpp': 'cpp'
        }
        return ext_to_lang.get(extension, 'unknown')
    
    def _contains_malicious_patterns(self, content: str) -> bool:
        """
        Basic check for potentially malicious patterns.
        In production, this should be enhanced with more sophisticated checks.
        """
        dangerous_patterns = [
            'import os', 'import sys', '__import__', 'eval(', 'exec(',
            'open(', 'compile(', 'input(', 'subprocess', 'os.system',
            'socket.', 'http.client', 'urllib.request'
        ]
        
        # Only check for dangerous patterns in suspicious contexts
        for pattern in dangerous_patterns:
            if pattern in content.lower():
                # Check if it's in a comment (safer)
                if not self._is_in_comment(content, pattern):
                    return True
        return False
    
    def _is_in_comment(self, content: str, pattern: str) -> bool:
        """Check if pattern appears within a comment."""
        lines = content.split('\n')
        for line in lines:
            if pattern in line.lower():
                stripped = line.strip()
                if stripped.startswith('#') or stripped.startswith('//') or '/*' in line:
                    return True
        return False
    
    def _clean_code(self, content: str, language: str) -> List[str]:
        """
        Clean code by removing comments and empty lines.
        
        Args:
            content: Source code content
            language: Programming language
            
        Returns:
            List of cleaned code lines
        """
        if language == 'python':
            return self._clean_python_code(content)
        else:  # C or C++
            return self._clean_c_cpp_code(content)
    
    def _clean_python_code(self, content: str) -> List[str]:
        """Clean Python code."""
        cleaned_lines = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            try:
                stripped_line = line.rstrip()  # Only remove trailing whitespace
                
                # Skip empty lines
                if not stripped_line:
                    continue
                
                # Handle indentation
                leading_spaces = len(stripped_line) - len(stripped_line.lstrip())
                
                # Remove comments
                if '#' in stripped_line:
                    # Handle # in strings
                    in_string = False
                    string_char = None
                    for i, char in enumerate(stripped_line):
                        if char in ('"', "'") and (i == 0 or stripped_line[i-1] != '\\'):
                            if not in_string:
                                in_string = True
                                string_char = char
                            elif char == string_char:
                                in_string = False
                        
                        if char == '#' and not in_string:
                            stripped_line = stripped_line[:i]
                            break
                
                stripped_line = stripped_line.rstrip()
                
                if stripped_line:
                    cleaned_lines.append((' ' * leading_spaces) + stripped_line)
                    
            except Exception as e:
                logger.warning(f"Error cleaning Python line {line_num}: {e}")
                continue
        
        return cleaned_lines
    
    def _clean_c_cpp_code(self, content: str) -> List[str]:
        """Clean C/C++ code."""
        cleaned_lines = []
        in_multiline_comment = False
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            try:
                stripped_line = line.rstrip()
                
                # Skip empty lines
                if not stripped_line:
                    continue
                
                # Track indentation
                leading_spaces = len(stripped_line) - len(stripped_line.lstrip())
                result_line = []
                i = 0
                
                while i < len(stripped_line):
                    if in_multiline_comment:
                        # Check for comment end
                        if i + 1 < len(stripped_line) and stripped_line[i:i+2] == '*/':
                            in_multiline_comment = False
                            i += 2
                        else:
                            i += 1
                    else:
                        # Check for string literals
                        if stripped_line[i] in ('"', "'"):
                            quote_char = stripped_line[i]
                            result_line.append(quote_char)
                            i += 1
                            
                            # Skip until matching quote (handling escaped quotes)
                            while i < len(stripped_line):
                                result_line.append(stripped_line[i])
                                if stripped_line[i] == quote_char and (i == 0 or stripped_line[i-1] != '\\'):
                                    break
                                i += 1
                            i += 1
                        
                        # Check for comment start
                        elif i + 1 < len(stripped_line):
                            if stripped_line[i:i+2] == '//':
                                # Single line comment - ignore rest of line
                                break
                            elif stripped_line[i:i+2] == '/*':
                                in_multiline_comment = True
                                i += 2
                            else:
                                result_line.append(stripped_line[i])
                                i += 1
                        else:
                            result_line.append(stripped_line[i])
                            i += 1
                
                # Add line if it has content
                line_content = ''.join(result_line).strip()
                if line_content:
                    cleaned_lines.append((' ' * leading_spaces) + line_content)
                    
            except Exception as e:
                logger.warning(f"Error cleaning C/C++ line {line_num}: {e}")
                continue
        
        return cleaned_lines


def test_code_reader():
    """Test the enhanced code reader."""
    reader = CodeReader()
    
    print("🧪 Testing Code Reader")
    print("=" * 50)
    
    # Test 1: Python code cleaning
    python_code = '''# This is a comment
def hello_world():
    print("Hello, World!")  # Print greeting
    x = 10  # This is a variable
    
    # Check condition
    if x > 5:
        print("x is greater than 5")
    
    return x'''
    
    print("\nTest 1: Python Code Cleaning")
    print("-" * 30)
    cleaned, error = reader.read_code_from_text(python_code, 'python')
    
    if error:
        print(f"Error: {error}")
    else:
        print(f"Cleaned {len(cleaned)} lines:")
        for i, line in enumerate(cleaned, 1):
            print(f"{i:3}: {line}")
    
    # Test 2: C code cleaning
    c_code = '''// Single line comment
#include <stdio.h>

/* Multiline
   comment */
   
int main() {
    char *msg = "Hello // not a comment";
    int x = 10;  // Inline comment
    
    /* Another
       comment */
    
    if (x > 5) {
        printf("%s\\n", msg);
    }
    
    return 0;
}'''
    
    print("\n\nTest 2: C Code Cleaning")
    print("-" * 30)
    cleaned, error = reader.read_code_from_text(c_code, 'c')
    
    if error:
        print(f"Error: {error}")
    else:
        print(f"Cleaned {len(cleaned)} lines:")
        for i, line in enumerate(cleaned, 1):
            print(f"{i:3}: {line}")
    
    # Test 3: Error cases
    print("\n\nTest 3: Error Handling")
    print("-" * 30)
    
    # Empty input
    cleaned, error = reader.read_code_from_text("", "python")
    print(f"Empty input: {error}")
    
    # Invalid language
    cleaned, error = reader.read_code_from_text("print('test')", "java")
    print(f"Invalid language: {error}")
    
    # Potentially malicious code
    malicious_code = "import os\nos.system('rm -rf /')"
    cleaned, error = reader.read_code_from_text(malicious_code, "python")
    print(f"Malicious pattern: {error}")


def main():
    """Main function for command-line usage."""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python code_reader.py <file_path>")
        print("Example: python code_reader.py ../test.py")
        sys.exit(1)
    
    file_path = sys.argv[1]
    reader = CodeReader()
    
    cleaned_lines, language, error = reader.read_code_file(file_path)
    
    if error:
        print(f"❌ Error: {error}")
        sys.exit(1)
    
    print(f"✅ Successfully read {file_path} ({language})")
    print(f"📊 Cleaned lines: {len(cleaned_lines)}")
    print("\nCleaned code:")
    print("-" * 50)
    
    for i, line in enumerate(cleaned_lines, 1):
        print(f"{i:4}: {line}")


if __name__ == "__main__":
    # Run tests when executed directly
    test_code_reader()
    
    # Uncomment to test with file argument
    # import sys
    # if len(sys.argv) > 1:
    #     main()
    # else:
    #     print("\nTo read a file: python code_reader.py <file_path>")