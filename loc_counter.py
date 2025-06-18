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
    '.html', '.htm', '.css', '.scss', '.sass', '.less', '.styl',
    '.js', '.jsx', '.ts', '.tsx', '.cjs', '.mjs', '.vue', '.svelte', '.ejs', '.pug', '.hbs',
    '.py', '.java', '.c', '.h', '.cpp', '.hpp', '.cs', '.go', '.rs', '.php',
    '.rb', '.swift', '.kt', '.kts', '.dart', '.lua', '.groovy', '.r', '.m',
    '.ex', '.exs', '.erl', '.hrl', '.clj', '.cljs', '.cljc', '.ml', '.mli', '.nim',
    '.sh', '.fish', '.bat', '.ps1', '.make', '.mk', '.gradle', '.bazel', '.bzl', '.nix',
    '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.env',
    '.md', '.rst', '.adoc', '.asciidoc', '.tex',
    '.sql', '.log', '.csv', '.tsv',
    '.tscn', '.gd', '.ux',
    '.wasm', '.wat'
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
        print(f"警告: 无法读取文件 {file_path}: {e}", file=sys.stderr)
        return 0

def analyze_project(project_path):
    """
    return: (stats_by_lang, total_files, total_lines)
    """
    stats_by_lang = defaultdict(lambda: {'files': 0, 'lines': 0})
    files_to_scan = []

    print("正在发现文件...")
    for root, dirs, files in os.walk(project_path, topdown=True):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for filename in files:
            if filename in EXCLUDE_FILES:
                continue

            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext in CODE_EXTENSIONS:
                files_to_scan.append(os.path.join(root, filename))
    
    if not files_to_scan:
        print("在指定路径下没有找到可分析的代码文件。")
        return {}, 0, 0

    print(f"发现 {len(files_to_scan)} 个代码文件，开始分析...")
    for file_path in tqdm(files_to_scan, desc="正在分析", unit="个文件"):
        file_ext = os.path.splitext(file_path)[1].lower()
        
        line_count = count_lines_in_file(file_path)
        
        stats_by_lang[file_ext]['files'] += 1
        stats_by_lang[file_ext]['lines'] += line_count

    total_files = sum(stats['files'] for stats in stats_by_lang.values())
    total_lines = sum(stats['lines'] for stats in stats_by_lang.values())

    return stats_by_lang, total_files, total_lines

def print_report(stats, total_files, total_lines, project_path):
    print("\n" + "="*50)
    print(f" 项目路径: {os.path.abspath(project_path)}")
    print(" 代码行数估算报告")
    print("="*50)

    sorted_stats = sorted(stats.items(), key=lambda item: item[1]['lines'], reverse=True)

    print(f"{'语言 (扩展名)':<20} {'文件数':>10} {'代码行数':>15}")
    print("-"*50)

    for lang, data in sorted_stats:
        print(f"{lang:<20} {data['files']:>10,} {data['lines']:>15,}")

    print("-"*50)
    print(f"{'总计':<20} {total_files:>10,} {total_lines:>15,}")
    print("="*50)
    print("\n* 注：行数包括代码、注释和空行。已排除常见的缓存和依赖目录。")


def main():
    parser = argparse.ArgumentParser(description="一个简单的项目代码行数估算工具。")
    parser.add_argument("path", nargs='?', default='.', help="要分析的项目文件夹路径 (默认为当前目录)")
    
    args = parser.parse_args()
    project_path = args.path

    if not os.path.isdir(project_path):
        print(f"错误: 路径 '{project_path}' 不是一个有效的目录。", file=sys.stderr)
        sys.exit(1)

    stats, total_files, total_lines = analyze_project(project_path)
    
    if total_files > 0:
        print_report(stats, total_files, total_lines, project_path)

if __name__ == "__main__":
    main()
