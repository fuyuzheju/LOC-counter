import os
import argparse
from collections import defaultdict
import sys

try:
    from tqdm import tqdm
except ImportError:
    # for smooth running, define a virtual tqdm if not imported
    def tqdm(iterable, *args, **kwargs):
        return iterable

CODE_EXTENSIONS = {
    # Web
    '.html', '.htm', '.css', '.scss', '.sass', '.less', '.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte',
    # general
    '.py', '.java', '.c', '.h', '.cpp', '.hpp', '.cs', '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.kts',
    # scripts
    '.sh', '.bat', '.ps1', '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.md', '.sql',
    # other
    '.dart', '.lua', '.groovy', '.r', '.m'
}

EXCLUDE_DIRS = {
    '__pycache__', 'node_modules', 'vendor', 'build', 'dist', 'target', 'out',
    '.git', '.svn', '.hg', '.vscode', '.idea', 'env', 'venv',
    'logs', 'log', 'tmp', 'temp', 'cache', '.cache'
}

EXCLUDE_FILES = {
    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'composer.lock',
    '.DS_Store'
}

def count_lines_in_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except Exception as e:
        print(f"WARNING: Failed to read file {file_path}: {e}", file=sys.stderr)
        return 0

def analyze_project(project_path):
    """
    return: (stats_by_lang, total_files, total_lines)
    """
    stats_by_lang = defaultdict(lambda: {'files': 0, 'lines': 0})
    files_to_scan = []

    print("Finding files...")
    for root, dirs, files in os.walk(project_path, topdown=True):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for filename in files:
            if filename in EXCLUDE_FILES:
                continue

            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext in CODE_EXTENSIONS:
                files_to_scan.append(os.path.join(root, filename))
    
    if not files_to_scan:
        print("No code files found in current directory.")
        return {}, 0, 0

    print(f"{len(files_to_scan)} code files found, now analyzing...")
    for file_path in tqdm(files_to_scan, desc="analyzing", unit="files"):
        file_ext = os.path.splitext(file_path)[1].lower()
        
        line_count = count_lines_in_file(file_path)
        
        stats_by_lang[file_ext]['files'] += 1
        stats_by_lang[file_ext]['lines'] += line_count

    total_files = sum(stats['files'] for stats in stats_by_lang.values())
    total_lines = sum(stats['lines'] for stats in stats_by_lang.values())

    return stats_by_lang, total_files, total_lines

def print_report(stats, total_files, total_lines, project_path):
    print("\n" + "="*50)
    print(f" project path: {os.path.abspath(project_path)}")
    print(" report of lines of code:")
    print("="*50)

    sorted_stats = sorted(stats.items(), key=lambda item: item[1]['lines'], reverse=True)

    print(f"{'Language':<20} {'Files':>10} {'LOC':>15}")
    print("-"*50)

    for lang, data in sorted_stats:
        print(f"{lang:<20} {data['files']:>10,} {data['lines']:>15,}")

    print("-"*50)
    print(f"{'Total':<20} {total_files:>10,} {total_lines:>15,}")
    print("="*50)


def main():
    parser = argparse.ArgumentParser(description="a simple LOC estimater")
    parser.add_argument("path", nargs='?', default='.', help="project path to analyze (default: current directory)")
    
    args = parser.parse_args()
    project_path = args.path

    if not os.path.isdir(project_path):
        print(f"Error: invalid path '{project_path}'.", file=sys.stderr)
        sys.exit(1)

    stats, total_files, total_lines = analyze_project(project_path)
    
    if total_files > 0:
        print_report(stats, total_files, total_lines, project_path)

if __name__ == "__main__":
    main()