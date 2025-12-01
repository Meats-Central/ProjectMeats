#!/usr/bin/env python3
"""
Source AI Conventions Script

This script searches for and aggregates AI convention files from various sources
following the glob pattern:
**/{.github/copilot-instructions.md,AGENT.md,AGENTS.md,CLAUDE.md,.cursorrules,
.windsurfrules,.clinerules,.cursor/rules/**,.windsurf/rules/**,.clinerules/**,README.md}

Usage:
    python source-ai-conventions.py [--output OUTPUT_FILE] [--format FORMAT]

Options:
    --output, -o    Output file path (default: stdout)
    --format, -f    Output format: 'markdown' or 'json' (default: markdown)
    --verbose, -v   Enable verbose output
"""

import argparse
import glob
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple


def should_skip_file(path: Path) -> bool:
    """
    Check if a file should be skipped (e.g., archived files).
    
    Args:
        path: Path object to check
        
    Returns:
        True if file should be skipped, False otherwise
    """
    # Check if 'archived' appears in any directory component (case-insensitive)
    parts = [p.lower() for p in path.parts]
    return any('archived' in part for part in parts)


def get_file_type(path: Path) -> str:
    """
    Determine the file type based on path.
    
    Args:
        path: Path object
        
    Returns:
        String describing the file type
    """
    # Check if file is in a rules directory
    parts = path.parts
    if 'rules' in parts:
        # Find the AI tool directory (e.g., .cursor, .windsurf)
        try:
            rules_idx = parts.index('rules')
            if rules_idx > 0:
                tool_dir = parts[rules_idx - 1]
                return f"{tool_dir}/rules/{path.name}"
        except (ValueError, IndexError):
            pass
    
    # Default to just the filename
    return path.name


def find_ai_convention_files(root_dir: str = ".") -> List[Tuple[str, str]]:
    """
    Find all AI convention files matching the specified patterns.
    
    Args:
        root_dir: Root directory to search from
        
    Returns:
        List of tuples (file_path, file_type)
    """
    files_found = []
    seen_paths = set()  # Track seen paths to avoid duplicates
    root_path = Path(root_dir).resolve()
    
    # Define patterns to search for
    # Note: glob doesn't handle hidden directories well, so we use Path.rglob instead
    patterns = [
        "copilot-instructions.md",
        "AGENT.md",
        "AGENTS.md",
        "CLAUDE.md",
        ".cursorrules",
        ".windsurfrules",
        ".clinerules",
        "README.md",
    ]
    
    # Search for files in rules directories
    rules_dirs = [
        ".cursor/rules",
        ".windsurf/rules",
        ".clinerules",
    ]
    
    # Use Path.rglob which handles hidden directories better
    for pattern in patterns:
        for path in root_path.rglob(pattern):
            # Skip directories
            if path.is_dir():
                continue
                
            # Skip archived files
            if should_skip_file(path):
                continue
            
            # Get relative path for cleaner output
            try:
                rel_path = path.relative_to(root_path)
            except ValueError:
                rel_path = path
            
            # Skip if we've already seen this path
            rel_path_str = str(rel_path)
            if rel_path_str in seen_paths:
                continue
            seen_paths.add(rel_path_str)
                
            # Determine file type
            file_type = get_file_type(path)
                
            files_found.append((rel_path_str, file_type))
    
    # Search in rules directories
    for rules_dir in rules_dirs:
        rules_path = root_path / rules_dir
        if rules_path.exists() and rules_path.is_dir():
            for path in rules_path.rglob("*"):
                if path.is_file():
                    # Skip archived files
                    if should_skip_file(path):
                        continue
                    
                    # Get relative path for cleaner output
                    try:
                        rel_path = path.relative_to(root_path)
                    except ValueError:
                        rel_path = path
                    
                    # Skip if we've already seen this path
                    rel_path_str = str(rel_path)
                    if rel_path_str in seen_paths:
                        continue
                    seen_paths.add(rel_path_str)
                    
                    file_type = get_file_type(path)
                        
                    files_found.append((rel_path_str, file_type))
    
    # Sort for consistent output
    files_found.sort()
    
    return files_found


def read_file_content(file_path: str) -> str:
    """
    Read content from a file.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        File content as string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"[Error reading file: {e}]"


def generate_markdown_output(files: List[Tuple[str, str]], root_dir: str = ".") -> str:
    """
    Generate markdown formatted output with all AI conventions.
    
    Args:
        files: List of tuples (file_path, file_type)
        root_dir: Root directory for resolving paths
        
    Returns:
        Markdown formatted string
    """
    output = []
    output.append("# AI Conventions - Aggregated from Multiple Sources\n")
    output.append(f"Generated from {len(files)} file(s)\n")
    output.append("---\n")
    
    for file_path, file_type in files:
        full_path = os.path.join(root_dir, file_path)
        content = read_file_content(full_path)
        
        output.append(f"\n## Source: `{file_path}`\n")
        output.append(f"**Type:** {file_type}\n")
        output.append(f"\n```\n{content}\n```\n")
        output.append("---\n")
    
    return "\n".join(output)


def generate_json_output(files: List[Tuple[str, str]], root_dir: str = ".") -> str:
    """
    Generate JSON formatted output with all AI conventions.
    
    Args:
        files: List of tuples (file_path, file_type)
        root_dir: Root directory for resolving paths
        
    Returns:
        JSON formatted string
    """
    result = {
        "total_files": len(files),
        "conventions": []
    }
    
    for file_path, file_type in files:
        full_path = os.path.join(root_dir, file_path)
        content = read_file_content(full_path)
        
        result["conventions"].append({
            "path": file_path,
            "type": file_type,
            "content": content
        })
    
    return json.dumps(result, indent=2)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Source and aggregate AI convention files from repository"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--format", "-f",
        type=str,
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--root", "-r",
        type=str,
        default=".",
        help="Root directory to search from (default: current directory)"
    )
    
    args = parser.parse_args()
    
    # Find all AI convention files
    if args.verbose:
        print("Searching for AI convention files...", file=sys.stderr)
    
    files = find_ai_convention_files(args.root)
    
    if args.verbose:
        print(f"Found {len(files)} file(s):", file=sys.stderr)
        for file_path, file_type in files:
            print(f"  - {file_path} ({file_type})", file=sys.stderr)
        print("", file=sys.stderr)
    
    # Generate output
    if args.format == "json":
        output = generate_json_output(files, args.root)
    else:
        output = generate_markdown_output(files, args.root)
    
    # Write output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        if args.verbose:
            print(f"Output written to: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
