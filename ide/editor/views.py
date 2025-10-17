from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os
import subprocess
import tempfile
import sys
from . import execution_engine

def index(request):
    """Render the main code editor page"""
    return render(request, 'index.html')

@csrf_exempt
def execute_code(request):
    """Execute Python code and return the output"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        code = data.get('code', '')
        language = data.get('language', 'python')

        if not code.strip():
            return JsonResponse({'output': '', 'error': 'No code provided'})

        try:
            output, error = execution_engine.run(code, language)
            return JsonResponse({'output': output, 'error': error})
        except Exception as e:
            return JsonResponse({'output': '', 'error': str(e)})
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

def save_code(request):
    """Save code to a file"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        code = data.get('code', '')
        filename = data.get('filename', 'untitled.py')
        
        # Ensure the uploads directory exists
        uploads_dir = os.path.join(settings.BASE_DIR, 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        
        file_path = os.path.join(uploads_dir, filename)
        
        with open(file_path, 'w') as f:
            f.write(code)
        
        return JsonResponse({
            'message': f'File saved successfully as {filename}',
            'filename': filename
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Save error: {str(e)}'}, status=500)

def load_file(request):
    """Load a Python file"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        filename = data.get('filename', '')
        
        if not filename:
            return JsonResponse({'error': 'No filename provided'}, status=400)
        
        uploads_dir = os.path.join(settings.BASE_DIR, 'uploads')
        file_path = os.path.join(uploads_dir, filename)
        
        if not os.path.exists(file_path):
            return JsonResponse({'error': 'File not found'}, status=404)
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        return JsonResponse({
            'code': content,
            'filename': filename
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Load error: {str(e)}'}, status=500)

def list_files(request):
    """List all saved Python files"""
    try:
        uploads_dir = os.path.join(settings.BASE_DIR, 'uploads')
        
        if not os.path.exists(uploads_dir):
            return JsonResponse({'files': []})
        
        files = [f for f in os.listdir(uploads_dir)]
        return JsonResponse({'files': files})
        
    except Exception as e:
        return JsonResponse({'error': f'List error: {str(e)}'}, status=500)