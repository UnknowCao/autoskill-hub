#!/usr/bin/env python3
"""
Batch convert multiple files to Markdown using MarkItDown.

This script demonstrates how to efficiently convert multiple files
in a directory to Markdown format.
"""

import argparse
from pathlib import Path
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

# Delegate to the full enhancement pipeline (encryption + formula + table
# detect + metadata). This makes batch_convert.py a thin parallel/recursive
# wrapper around _convert_core.convert_file(), so the two paths never diverge
# in capability.
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
from _convert_core import convert_file as _convert_file_enhanced


def convert_file(file_path: Path, output_dir: Path, verbose: bool = False,
                 enable_table_detect: bool = True,
                 enable_metadata: bool = True,
                 allow_prompt: bool = True) -> tuple[bool, str, str]:
    """
    Convert a single file via the full enhancement pipeline.

    Thin wrapper over _convert_core.convert_file() that resolves the output
    path inside output_dir and surfaces the enhanced report/errors_path.

    Returns:
        Tuple of (success, input_path_str, message_including_errors_path)
    """
    try:
        output_file = output_dir / f"{file_path.stem}.md"
        success, report, errors_path = _convert_file_enhanced(
            file_path,
            output_file,
            enable_table_detect=enable_table_detect,
            enable_metadata=enable_metadata,
            allow_prompt=allow_prompt,
        )
        msg = report
        if errors_path:
            # Surface the sidecar path so the batch driver (AI) can collect
            # all .errors.md files after the run and run stage-2 fixes.
            msg += f"\n  [SIDECAR] {errors_path}"
        return success, str(file_path), msg

    except Exception as e:
        return False, str(file_path), f"[ERR] Error: {str(e)}"


def batch_convert(
    input_dir: Path,
    output_dir: Path,
    extensions: Optional[List[str]] = None,
    recursive: bool = False,
    workers: int = 4,
    verbose: bool = False,
    enable_plugins: bool = False,
    enable_table_detect: bool = True,
    enable_metadata: bool = True,
    allow_prompt: bool = True
) -> dict:
    """
    Batch convert files in a directory using the full enhancement pipeline.

    Each file is converted via _convert_core.convert_file(), so batch gets the
    same treatment as single-file: encryption detection + decryption, formula
    escaping fix, table structure detection (sidecar .errors.md), and metadata
    header.

    Args:
        input_dir: Input directory
        output_dir: Output directory
        extensions: List of file extensions to convert (e.g., ['.pdf', '.docx'])
        recursive: Search subdirectories
        workers: Number of parallel workers
        verbose: Print detailed messages
        enable_plugins: (reserved) MarkItDown plugins — not yet wired through
        enable_table_detect: run table structure detection (default True)
        enable_metadata: prepend metadata header (default True)

    Returns:
        Dictionary with conversion statistics and per-file sidecar paths.
    """
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Default extensions if not specified
    if extensions is None:
        extensions = ['.pdf', '.docx', '.pptx', '.xlsx', '.html', '.jpg', '.png']
    
    # Find files
    files = []
    if recursive:
        for ext in extensions:
            files.extend(input_dir.rglob(f"*{ext}"))
    else:
        for ext in extensions:
            files.extend(input_dir.glob(f"*{ext}"))

    # Skip MS Office lock/temp files (start with "~$") — these are not real
    # documents and always fail with BadZipFile.
    files = [f for f in files if not f.name.startswith("~$")]
    # Deduplicate (globbing multiple extensions can match the same file once
    # per extension on case-insensitive filesystems).
    seen = set()
    files = [f for f in files if not (str(f).lower() in seen or seen.add(str(f).lower()))]

    if not files:
        print(f"No files found with extensions: {', '.join(extensions)}")
        return {'total': 0, 'success': 0, 'failed': 0, 'sidecars': []}

    print(f"Found {len(files)} file(s) to convert")

    # Convert files in parallel (each worker calls the full enhancement pipeline)
    results = {
        'total': len(files),
        'success': 0,
        'failed': 0,
        'details': [],
        'sidecars': []   # collected .errors.md paths for stage-2 AI fixing
    }

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(
                convert_file, file_path, output_dir, verbose,
                enable_table_detect, enable_metadata, allow_prompt
            ): file_path
            for file_path in files
        }

        for future in as_completed(futures):
            success, path, message = future.result()

            if success:
                results['success'] += 1
            else:
                results['failed'] += 1

            # Collect any sidecar .errors.md paths emitted by table detection
            for line in message.splitlines():
                if '[SIDECAR]' in line:
                    sidecar = line.split('[SIDECAR]', 1)[1].strip()
                    if sidecar:
                        results['sidecars'].append(sidecar)

            results['details'].append({
                'file': path,
                'success': success,
                'message': message
            })

            print(message)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Batch convert files to Markdown using MarkItDown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert all PDFs in a directory
  python batch_convert.py papers/ output/ --extensions .pdf

  # Convert multiple formats recursively
  python batch_convert.py documents/ markdown/ --extensions .pdf .docx .pptx -r

  # Use 8 parallel workers
  python batch_convert.py input/ output/ --workers 8

  # Disable table detection (faster for simple docs)
  python batch_convert.py input/ output/ --no-table-detect

  # Disable metadata header
  python batch_convert.py input/ output/ --no-metadata
        """
    )

    parser.add_argument('input_dir', type=Path, help='Input directory')
    parser.add_argument('output_dir', type=Path, help='Output directory')
    parser.add_argument(
        '--extensions', '-e',
        nargs='+',
        help='File extensions to convert (e.g., .pdf .docx)'
    )
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='Search subdirectories recursively'
    )
    parser.add_argument(
        '--workers', '-w',
        type=int,
        default=4,
        help='Number of parallel workers (default: 4)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--plugins', '-p',
        action='store_true',
        help='(reserved) Enable MarkItDown plugins'
    )
    parser.add_argument(
        '--no-table-detect',
        action='store_true',
        help='Skip table structure detection'
    )
    parser.add_argument(
        '--no-metadata',
        action='store_true',
        help='Skip the metadata header (# title / Source / Format)'
    )
    parser.add_argument(
        '--no-prompt',
        action='store_true',
        help='Skip encrypted-file password dialog; use only keyring (agent/CI safe)'
    )

    args = parser.parse_args()
    
    # Validate input directory
    if not args.input_dir.exists():
        print(f"Error: Input directory '{args.input_dir}' does not exist")
        sys.exit(1)
    
    if not args.input_dir.is_dir():
        print(f"Error: '{args.input_dir}' is not a directory")
        sys.exit(1)
    
    # Run batch conversion
    results = batch_convert(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        extensions=args.extensions,
        recursive=args.recursive,
        workers=args.workers,
        verbose=args.verbose,
        enable_plugins=args.plugins,
        enable_table_detect=not args.no_table_detect,
        enable_metadata=not args.no_metadata,
        allow_prompt=not args.no_prompt,
    )

    # Print summary
    print("\n" + "="*50)
    print("CONVERSION SUMMARY")
    print("="*50)
    print(f"Total files:     {results['total']}")
    print(f"Successful:      {results['success']}")
    print(f"Failed:          {results['failed']}")
    print(f"Success rate:    {results['success']/results['total']*100:.1f}%" if results['total'] > 0 else "N/A")
    
    # Show failed files if any
    if results['failed'] > 0:
        print("\nFailed conversions:")
        for detail in results['details']:
            if not detail['success']:
                print(f"  - {detail['file']}: {detail['message']}")

    # List sidecar .errors.md files (table errors awaiting stage-2 AI fix).
    # Per the skill's AUTO-FIX POLICY: the AI driver should read each sidecar
    # and fix the corresponding .md immediately, then delete the sidecar.
    sidecars = results.get('sidecars', [])
    if sidecars:
        print("\nTable errors detected (sidecar .errors.md written for stage-2 AI fix):")
        for sc in sidecars:
            print(f"  - {sc}")

    # Exit code: 0 if all converted AND no table errors; 1 if any failure OR
    # any sidecar was written (signals the AI driver to run stage-2 fixes).
    sys.exit(0 if results['failed'] == 0 and not sidecars else 1)


if __name__ == '__main__':
    main()

