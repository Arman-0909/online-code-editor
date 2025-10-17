import subprocess
import tempfile
import os
import sys

def run(code, language):
    """
    Runs the given code in the specified language.
    """
    language = language.lower()
    if language == 'python':
        return _run_python(code)
    elif language == 'php':
        return _run_php(code)
    elif language == 'c':
        return _run_c(code)
    elif language == 'cpp':
        return _run_cpp(code)
    elif language == 'java':
       return _run_java(code)
    elif language == 'swift':
       return _run_swift(code)
    elif language == 'go':
       return _run_go(code)
    elif language in ['html', 'css', 'javascript']:
        return "Live preview for HTML/CSS/JS is not supported on the backend. Please open your HTML file in a browser to see the result.", ""
    else:
        return "", f"Unsupported language: {language}"

def _run_python(code):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        return _execute_command([sys.executable, temp_file])
    finally:
        os.unlink(temp_file)

def _run_php(code):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        return _execute_command(['php', temp_file])
    finally:
        os.unlink(temp_file)

def _run_c(code):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
        f.write(code)
        source_file = f.name
    
    executable_file = source_file.replace('.c', '.exe') if sys.platform == 'win32' else source_file.replace('.c', '')
    
    try:
        compile_stdout, compile_stderr = _execute_command(['gcc', source_file, '-o', executable_file])
        if compile_stderr:
            return "", compile_stderr
        
        return _execute_command([executable_file])
    finally:
        if os.path.exists(source_file):
            os.unlink(source_file)
        if os.path.exists(executable_file):
            os.unlink(executable_file)

def _run_cpp(code):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
        f.write(code)
        source_file = f.name
    
    executable_file = source_file.replace('.cpp', '.exe') if sys.platform == 'win32' else source_file.replace('.cpp', '')
    
    try:
        compile_stdout, compile_stderr = _execute_command(['g++', source_file, '-o', executable_file])
        if compile_stderr:
            return "", compile_stderr
        
        return _execute_command([executable_file])
    finally:
        if os.path.exists(source_file):
            os.unlink(source_file)
        if os.path.exists(executable_file):
            os.unlink(executable_file)

def _run_java(code):
    # Find the class name
    class_name = None
    for line in code.splitlines():
        if 'public class' in line:
            class_name = line.split('public class')[1].split('{')[0].strip()
            break
    
    if not class_name:
        return "", "Could not find a public class in the Java code."

    with tempfile.TemporaryDirectory() as temp_dir:
        source_file = os.path.join(temp_dir, f"{class_name}.java")
        with open(source_file, 'w') as f:
            f.write(code)
        
        compile_stdout, compile_stderr = _execute_command(['javac', source_file])
        if compile_stderr:
            return "", compile_stderr
        
        return _execute_command(['java', '-cp', temp_dir, class_name])

def _run_swift(code):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.swift', delete=False) as f:
        f.write(code)
        source_file = f.name
    
    executable_file = source_file.replace('.swift', '.exe') if sys.platform == 'win32' else source_file.replace('.swift', '')

    try:
        compile_stdout, compile_stderr = _execute_command(['swiftc', source_file, '-o', executable_file])
        if compile_stderr:
            return "", compile_stderr
        
        return _execute_command([executable_file])
    finally:
        if os.path.exists(source_file):
            os.unlink(source_file)
        if os.path.exists(executable_file):
            os.unlink(executable_file)

def _run_go(code):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.go', delete=False) as f:
        f.write(code)
        source_file = f.name
    
    executable_file = source_file.replace('.go', '.exe') if sys.platform == 'win32' else source_file.replace('.go', '')

    try:
        compile_stdout, compile_stderr = _execute_command(['go', 'build', '-o', executable_file, source_file])
        if compile_stderr:
            return "", compile_stderr
        
        return _execute_command([executable_file])
    finally:
        if os.path.exists(source_file):
            os.unlink(source_file)
        if os.path.exists(executable_file):
            os.unlink(executable_file)

def _execute_command(command, timeout=10):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False 
        )
        return result.stdout, result.stderr
    except FileNotFoundError:
        return "", f"Command not found: {command[0]}. Please ensure it is installed and in your PATH."
    except subprocess.TimeoutExpired:
        return "", f"Execution timed out after {timeout} seconds"
    except Exception as e:
        return "", f"An unexpected error occurred: {str(e)}"