#!/usr/bin/env python3
"""
Analyze unused files in the codebase
"""
import os
import ast
import re
from pathlib import Path
from typing import Set, Dict, List

def find_python_files(directory: str) -> List[str]:
    """Find all Python files in directory"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def extract_imports(file_path: str) -> Set[str]:
    """Extract all imports from a Python file"""
    imports = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse AST
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
        except SyntaxError:
            pass
        
        # Also check for string-based imports
        import_patterns = [
            r'from\s+(\w+)',
            r'import\s+(\w+)',
            r'importlib\.import_module\([\'"](\w+)[\'"]',
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            imports.update(matches)
            
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return imports

def analyze_usage():
    """Analyze file usage in the codebase"""
    
    # Get all Python files
    python_files = find_python_files('.')
    
    # Extract base names without extension
    file_modules = {}
    for file_path in python_files:
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        file_modules[base_name] = file_path
    
    # Find all imports across all files
    all_imports = set()
    file_imports = {}
    
    for file_path in python_files:
        imports = extract_imports(file_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        file_imports[base_name] = imports
        all_imports.update(imports)
    
    # Entry points (files that are run directly)
    entry_points = {
        'main',           # CLI entry point
        'streamlit_ui',   # Web UI entry point
        'run_ui',         # UI launcher
        'start_ui',       # Batch launcher
    }
    
    # Core system files (always used)
    core_files = {
        'tools',          # Core functionality
        'orchestrator',   # Main orchestrator
        'agents',         # Agent system
        'config',         # Configuration
    }
    
    # UI-specific files
    ui_files = {
        'main_ui',
        'ui_dashboard', 
        'ui_question_handler',
    }
    
    # Find unused files
    used_files = set()
    
    # Add entry points
    used_files.update(entry_points)
    
    # Add files imported by entry points and core files
    def add_dependencies(file_name):
        if file_name in file_imports:
            for imported in file_imports[file_name]:
                if imported in file_modules and imported not in used_files:
                    used_files.add(imported)
                    add_dependencies(imported)  # Recursive
    
    # Start from entry points
    for entry in entry_points:
        if entry in file_modules:
            add_dependencies(entry)
    
    # Add core files
    for core in core_files:
        if core in file_modules:
            used_files.add(core)
            add_dependencies(core)
    
    # Add UI files (used by streamlit_ui)
    for ui in ui_files:
        if ui in file_modules:
            used_files.add(ui)
            add_dependencies(ui)
    
    # Find unused files
    all_modules = set(file_modules.keys())
    unused_files = all_modules - used_files
    
    return {
        'all_files': all_modules,
        'used_files': used_files,
        'unused_files': unused_files,
        'file_modules': file_modules
    }

def main():
    """Main analysis function"""
    print("🔍 Analyzing unused files in the codebase...")
    
    analysis = analyze_usage()
    
    print(f"\n📊 Analysis Results:")
    print(f"Total Python files: {len(analysis['all_files'])}")
    print(f"Used files: {len(analysis['used_files'])}")
    print(f"Unused files: {len(analysis['unused_files'])}")
    
    if analysis['unused_files']:
        print(f"\n❌ UNUSED FILES (can be removed):")
        for unused in sorted(analysis['unused_files']):
            file_path = analysis['file_modules'][unused]
            print(f"   - {unused}.py ({file_path})")
    
    print(f"\n✅ USED FILES (required for system):")
    for used in sorted(analysis['used_files']):
        if used in analysis['file_modules']:
            file_path = analysis['file_modules'][used]
            print(f"   - {used}.py ({file_path})")
    
    # Additional analysis
    print(f"\n🔧 ENTRY POINTS:")
    entry_points = ['main', 'streamlit_ui', 'run_ui']
    for entry in entry_points:
        if entry in analysis['file_modules']:
            print(f"   - {entry}.py - {analysis['file_modules'][entry]}")
    
    print(f"\n📁 DIRECTORIES AND DATA FILES (not analyzed):")
    dirs = ['chroma/', 'temp/', 'user_feedback/', 'generated_testcases/', 'traceability_logs/']
    for dir_name in dirs:
        if os.path.exists(dir_name):
            file_count = len([f for f in os.listdir(dir_name) if os.path.isfile(os.path.join(dir_name, f))])
            print(f"   - {dir_name} ({file_count} files)")

if __name__ == "__main__":
    main()