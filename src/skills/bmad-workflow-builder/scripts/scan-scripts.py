#!/usr/bin/env python3
"""Deterministic scripts scanner for BMad skills.

Validates scripts in a skill's scripts/ folder for:
- PEP 723 inline dependencies (Python)
- Shebang, set -e, portability (Shell)
- Version pinning for npx/uvx
- Agentic design: no input(), has argparse/--help, JSON output, exit codes
- Unit test existence
- Over-engineering signals (line count, simple-op imports)
- External lint: ruff (Python), shellcheck (Bash), biome (JS/TS)
"""

# /// script
# requires-python = ">=3.9"
# ///

from __future__ import annotations

import argparse
import ast
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


# =============================================================================
# External Linter Integration
# =============================================================================

def _run_command(cmd: list[str], timeout: int = 30) -> tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return -1, '', f'Command not found: {cmd[0]}'
    except subprocess.TimeoutExpired:
        return -2, '', f'Command timed out after {timeout}s: {" ".join(cmd)}'


def _find_uv() -> str | None:
    """Find uv binary on PATH."""
    return shutil.which('uv')


def _find_npx() -> str | None:
    """Find npx binary on PATH."""
    return shutil.which('npx')


def lint_python_ruff(filepath: Path, rel_path: str) -> list[dict]:
    """Run ruff on a Python file via uv. Returns lint findings."""
    uv = _find_uv()
    if not uv:
        return [{
            'file': rel_path, 'line': 0,
            'severity': 'high', 'category': 'lint-setup',
            'issue': 'uv not found on PATH — cannot run ruff for Python linting',
            'fix': 'Install uv: https://docs.astral.sh/uv/getting-started/installation/',
        }]

    rc, stdout, stderr = _run_command([
        uv, 'run', 'ruff', 'check', '--output-format', 'json', str(filepath),
    ])

    if rc == -1:
        return [{
            'file': rel_path, 'line': 0,
            'severity': 'high', 'category': 'lint-setup',
            'issue': f'Failed to run ruff via uv: {stderr.strip()}',
            'fix': 'Ensure uv can install and run ruff: uv run ruff --version',
        }]

    if rc == -2:
        return [{
            'file': rel_path, 'line': 0,
            'severity': 'medium', 'category': 'lint',
            'issue': f'ruff timed out on {rel_path}',
        }]

    # ruff outputs JSON array on stdout (even on rc=1 when issues found)
    findings = []
    try:
        issues = json.loads(stdout) if stdout.strip() else []
    except json.JSONDecodeError:
        return [{
            'file': rel_path, 'line': 0,
            'severity': 'medium', 'category': 'lint',
            'issue': f'Failed to parse ruff output for {rel_path}',
        }]

    for issue in issues:
        fix_msg = issue.get('fix', {}).get('message', '') if issue.get('fix') else ''
        findings.append({
            'file': rel_path,
            'line': issue.get('location', {}).get('row', 0),
            'severity': 'high',
            'category': 'lint',
            'issue': f'[{issue.get("code", "?")}] {issue.get("message", "")}',
            'fix': fix_msg or f'See https://docs.astral.sh/ruff/rules/{issue.get("code", "")}',
        })

    return findings


def lint_shell_shellcheck(filepath: Path, rel_path: str) -> list[dict]:
    """Run shellcheck on a shell script via uv. Returns lint findings."""
    uv = _find_uv()
    if not uv:
        return [{
            'file': rel_path, 'line': 0,
            'severity': 'high', 'category': 'lint-setup',
            'issue': 'uv not found on PATH — cannot run shellcheck for shell linting',
            'fix': 'Install uv: https://docs.astral.sh/uv/getting-started/installation/',
        }]

    rc, stdout, stderr = _run_command([
        uv, 'run', '--with', 'shellcheck-py',
        'shellcheck', '--format', 'json', str(filepath),
    ])

    if rc == -1:
        return [{
            'file': rel_path, 'line': 0,
            'severity': 'high', 'category': 'lint-setup',
            'issue': f'Failed to run shellcheck via uv: {stderr.strip()}',
            'fix': 'Ensure uv can install shellcheck-py: uv run --with shellcheck-py shellcheck --version',
        }]

    if rc == -2:
        return [{
            'file': rel_path, 'line': 0,
            'severity': 'medium', 'category': 'lint',
            'issue': f'shellcheck timed out on {rel_path}',
        }]

    findings = []
    # shellcheck outputs JSON on stdout (rc=1 when issues found)
    raw = stdout.strip() or stderr.strip()
    try:
        issues = json.loads(raw) if raw else []
    except json.JSONDecodeError:
        return [{
            'file': rel_path, 'line': 0,
            'severity': 'medium', 'category': 'lint',
            'issue': f'Failed to parse shellcheck output for {rel_path}',
        }]

    # Map shellcheck levels to our severity
    level_map = {'error': 'high', 'warning': 'high', 'info': 'high', 'style': 'medium'}

    for issue in issues:
        sc_code = issue.get('code', '')
        findings.append({
            'file': rel_path,
            'line': issue.get('line', 0),
            'severity': level_map.get(issue.get('level', ''), 'high'),
            'category': 'lint',
            'issue': f'[SC{sc_code}] {issue.get("message", "")}',
            'fix': f'See https://www.shellcheck.net/wiki/SC{sc_code}',
        })

    return findings


def lint_node_biome(filepath: Path, rel_path: str) -> list[dict]:
    """Run biome on a JS/TS file via npx. Returns lint findings."""
    npx = _find_npx()
    if not npx:
        return [{
            'file': rel_path, 'line': 0,
            'severity': 'high', 'category': 'lint-setup',
            'issue': 'npx not found on PATH — cannot run biome for JS/TS linting',
            'fix': 'Install Node.js 20+: https://nodejs.org/',
        }]

    rc, stdout, stderr = _run_command([
        npx, '--yes', '@biomejs/biome', 'lint', '--reporter', 'json', str(filepath),
    ], timeout=60)

    if rc == -1:
        return [{
            'file': rel_path, 'line': 0,
            'severity': 'high', 'category': 'lint-setup',
            'issue': f'Failed to run biome via npx: {stderr.strip()}',
            'fix': 'Ensure npx can run biome: npx @biomejs/biome --version',
        }]

    if rc == -2:
        return [{
            'file': rel_path, 'line': 0,
            'severity': 'medium', 'category': 'lint',
            'issue': f'biome timed out on {rel_path}',
        }]

    findings = []
    # biome outputs JSON on stdout
    raw = stdout.strip()
    try:
        result = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        return [{
            'file': rel_path, 'line': 0,
            'severity': 'medium', 'category': 'lint',
            'issue': f'Failed to parse biome output for {rel_path}',
        }]

    for diag in result.get('diagnostics', []):
        loc = diag.get('location', {})
        start = loc.get('start', {})
        findings.append({
            'file': rel_path,
            'line': start.get('line', 0),
            'severity': 'high',
            'category': 'lint',
            'issue': f'[{diag.get("category", "?")}] {diag.get("message", "")}',
            'fix': diag.get('advices', [{}])[0].get('message', '') if diag.get('advices') else '',
        })

    return findings


# =============================================================================
# BMad Pattern Checks (Existing)
# =============================================================================

def scan_python_script(filepath: Path, rel_path: str) -> list[dict]:
    """Check a Python script for standards compliance."""
    findings = []
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')
    line_count = len(lines)

    # PEP 723 check
    if '# /// script' not in content:
        # Only flag if the script has imports (not a trivial script)
        if 'import ' in content:
            findings.append({
                'file': rel_path, 'line': 1,
                'severity': 'medium', 'category': 'dependencies',
                'issue': 'No PEP 723 inline dependency block (# /// script)',
                'fix': 'Add PEP 723 block with requires-python and dependencies',
            })
    else:
        # Check requires-python is present
        if 'requires-python' not in content:
            findings.append({
                'file': rel_path, 'line': 1,
                'severity': 'low', 'category': 'dependencies',
                'issue': 'PEP 723 block exists but missing requires-python constraint',
                'fix': 'Add requires-python = ">=3.9" or appropriate version',
            })

    # requirements.txt reference
    if 'requirements.txt' in content or 'pip install' in content:
        findings.append({
            'file': rel_path, 'line': 1,
            'severity': 'high', 'category': 'dependencies',
            'issue': 'References requirements.txt or pip install — use PEP 723 inline deps',
            'fix': 'Replace with PEP 723 inline dependency block',
        })

    # Agentic design checks via AST
    try:
        tree = ast.parse(content)
    except SyntaxError:
        findings.append({
            'file': rel_path, 'line': 1,
            'severity': 'critical', 'category': 'error-handling',
            'issue': 'Python syntax error — script cannot be parsed',
        })
        return findings

    has_argparse = False
    has_json_dumps = False
    has_sys_exit = False
    imports = set()

    for node in ast.walk(tree):
        # Track imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)

        # input() calls
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == 'input':
                findings.append({
                    'file': rel_path, 'line': node.lineno,
                    'severity': 'critical', 'category': 'agentic-design',
                    'issue': 'input() call found — blocks in non-interactive agent execution',
                    'fix': 'Use argparse with required flags instead of interactive prompts',
                })
            # json.dumps
            if isinstance(func, ast.Attribute) and func.attr == 'dumps':
                has_json_dumps = True
            # sys.exit
            if isinstance(func, ast.Attribute) and func.attr == 'exit':
                has_sys_exit = True
            if isinstance(func, ast.Name) and func.id == 'exit':
                has_sys_exit = True

        # argparse
        if isinstance(node, ast.Attribute) and node.attr == 'ArgumentParser':
            has_argparse = True

    if not has_argparse and line_count > 20:
        findings.append({
            'file': rel_path, 'line': 1,
            'severity': 'medium', 'category': 'agentic-design',
            'issue': 'No argparse found — script lacks --help self-documentation',
            'fix': 'Add argparse with description and argument help text',
        })

    if not has_json_dumps and line_count > 20:
        findings.append({
            'file': rel_path, 'line': 1,
            'severity': 'medium', 'category': 'agentic-design',
            'issue': 'No json.dumps found — output may not be structured JSON',
            'fix': 'Use json.dumps for structured output parseable by workflows',
        })

    if not has_sys_exit and line_count > 20:
        findings.append({
            'file': rel_path, 'line': 1,
            'severity': 'low', 'category': 'agentic-design',
            'issue': 'No sys.exit() calls — may not return meaningful exit codes',
            'fix': 'Return 0=success, 1=fail, 2=error via sys.exit()',
        })

    # Over-engineering: simple file ops in Python
    simple_op_imports = {'shutil', 'glob', 'fnmatch'}
    over_eng = imports & simple_op_imports
    if over_eng and line_count < 30:
        findings.append({
            'file': rel_path, 'line': 1,
            'severity': 'low', 'category': 'over-engineered',
            'issue': f'Short script ({line_count} lines) imports {", ".join(over_eng)} — may be simpler as bash',
            'fix': 'Consider if cp/mv/find shell commands would suffice',
        })

    # Very short script
    if line_count < 5:
        findings.append({
            'file': rel_path, 'line': 1,
            'severity': 'medium', 'category': 'over-engineered',
            'issue': f'Script is only {line_count} lines — could be an inline command',
            'fix': 'Consider inlining this command directly in the prompt',
        })

    return findings


def scan_shell_script(filepath: Path, rel_path: str) -> list[dict]:
    """Check a shell script for standards compliance."""
    findings = []
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')
    line_count = len(lines)

    # Shebang
    if not lines[0].startswith('#!'):
        findings.append({
            'file': rel_path, 'line': 1,
            'severity': 'high', 'category': 'portability',
            'issue': 'Missing shebang line',
            'fix': 'Add #!/usr/bin/env bash or #!/usr/bin/env sh',
        })
    elif '/usr/bin/env' not in lines[0]:
        findings.append({
            'file': rel_path, 'line': 1,
            'severity': 'medium', 'category': 'portability',
            'issue': f'Shebang uses hardcoded path: {lines[0].strip()}',
            'fix': 'Use #!/usr/bin/env bash for cross-platform compatibility',
        })

    # set -e
    if 'set -e' not in content and 'set -euo' not in content:
        findings.append({
            'file': rel_path, 'line': 1,
            'severity': 'medium', 'category': 'error-handling',
            'issue': 'Missing set -e — errors will be silently ignored',
            'fix': 'Add set -e (or set -euo pipefail) near the top',
        })

    # Hardcoded interpreter paths
    hardcoded_re = re.compile(r'/usr/bin/(python|ruby|node|perl)\b')
    for i, line in enumerate(lines, 1):
        if hardcoded_re.search(line):
            findings.append({
                'file': rel_path, 'line': i,
                'severity': 'medium', 'category': 'portability',
                'issue': f'Hardcoded interpreter path: {line.strip()}',
                'fix': 'Use /usr/bin/env or PATH-based lookup',
            })

    # GNU-only tools
    gnu_re = re.compile(r'\b(gsed|gawk|ggrep|gfind)\b')
    for i, line in enumerate(lines, 1):
        m = gnu_re.search(line)
        if m:
            findings.append({
                'file': rel_path, 'line': i,
                'severity': 'medium', 'category': 'portability',
                'issue': f'GNU-only tool: {m.group()} — not available on all platforms',
                'fix': 'Use POSIX-compatible equivalent',
            })

    # Unquoted variables (basic check)
    unquoted_re = re.compile(r'(?<!")\$\w+(?!")')
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('#'):
            continue
        for m in unquoted_re.finditer(line):
            # Skip inside double-quoted strings (rough heuristic)
            before = line[:m.start()]
            if before.count('"') % 2 == 1:
                continue
            findings.append({
                'file': rel_path, 'line': i,
                'severity': 'low', 'category': 'portability',
                'issue': f'Potentially unquoted variable: {m.group()} — breaks with spaces in paths',
                'fix': f'Use "{m.group()}" with double quotes',
            })

    # npx/uvx without version pinning
    no_pin_re = re.compile(r'\b(npx|uvx)\s+([a-zA-Z][\w-]+)(?!\S*@)')
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('#'):
            continue
        m = no_pin_re.search(line)
        if m:
            findings.append({
                'file': rel_path, 'line': i,
                'severity': 'medium', 'category': 'dependencies',
                'issue': f'{m.group(1)} {m.group(2)} without version pinning',
                'fix': f'Pin version: {m.group(1)} {m.group(2)}@<version>',
            })

    # Very short script
    if line_count < 5:
        findings.append({
            'file': rel_path, 'line': 1,
            'severity': 'medium', 'category': 'over-engineered',
            'issue': f'Script is only {line_count} lines — could be an inline command',
            'fix': 'Consider inlining this command directly in the prompt',
        })

    return findings


def scan_node_script(filepath: Path, rel_path: str) -> list[dict]:
    """Check a JS/TS script for standards compliance."""
    findings = []
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')
    line_count = len(lines)

    # npx/uvx without version pinning
    no_pin = re.compile(r'\b(npx|uvx)\s+([a-zA-Z][\w-]+)(?!\S*@)')
    for i, line in enumerate(lines, 1):
        m = no_pin.search(line)
        if m:
            findings.append({
                'file': rel_path, 'line': i,
                'severity': 'medium', 'category': 'dependencies',
                'issue': f'{m.group(1)} {m.group(2)} without version pinning',
                'fix': f'Pin version: {m.group(1)} {m.group(2)}@<version>',
            })

    # Very short script
    if line_count < 5:
        findings.append({
            'file': rel_path, 'line': 1,
            'severity': 'medium', 'category': 'over-engineered',
            'issue': f'Script is only {line_count} lines — could be an inline command',
            'fix': 'Consider inlining this command directly in the prompt',
        })

    return findings


# =============================================================================
# Main Scanner
# =============================================================================

def scan_skill_scripts(skill_path: Path) -> dict:
    """Scan all scripts in a skill directory."""
    scripts_dir = skill_path / 'scripts'
    all_findings = []
    lint_findings = []
    script_inventory = {'python': [], 'shell': [], 'node': [], 'other': []}
    missing_tests = []

    if not scripts_dir.exists():
        return {
            'scanner': 'scripts',
            'script': 'scan-scripts.py',
            'version': '2.0.0',
            'skill_path': str(skill_path),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'status': 'pass',
            'issues': [{
                'file': 'scripts/',
                'severity': 'info',
                'category': 'none',
                'issue': 'No scripts/ directory found — nothing to scan',
            }],
            'lint_summary': {
                'tools_used': [],
                'files_linted': 0,
                'lint_issues': 0,
            },
            'script_summary': {
                'total_scripts': 0,
                'by_type': script_inventory,
                'missing_tests': [],
            },
            'summary': {
                'total_issues': 0,
                'by_severity': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
            },
        }

    # Find all script files (exclude tests/ and __pycache__)
    script_files = []
    for f in sorted(scripts_dir.iterdir()):
        if f.is_file() and f.suffix in ('.py', '.sh', '.bash', '.js', '.ts', '.mjs'):
            script_files.append(f)

    tests_dir = scripts_dir / 'tests'
    lint_tools_used = set()

    for script_file in script_files:
        rel_path = f'scripts/{script_file.name}'
        ext = script_file.suffix

        if ext == '.py':
            script_inventory['python'].append(script_file.name)
            findings = scan_python_script(script_file, rel_path)
            lf = lint_python_ruff(script_file, rel_path)
            lint_findings.extend(lf)
            if lf and not any(f['category'] == 'lint-setup' for f in lf):
                lint_tools_used.add('ruff')
        elif ext in ('.sh', '.bash'):
            script_inventory['shell'].append(script_file.name)
            findings = scan_shell_script(script_file, rel_path)
            lf = lint_shell_shellcheck(script_file, rel_path)
            lint_findings.extend(lf)
            if lf and not any(f['category'] == 'lint-setup' for f in lf):
                lint_tools_used.add('shellcheck')
        elif ext in ('.js', '.ts', '.mjs'):
            script_inventory['node'].append(script_file.name)
            findings = scan_node_script(script_file, rel_path)
            lf = lint_node_biome(script_file, rel_path)
            lint_findings.extend(lf)
            if lf and not any(f['category'] == 'lint-setup' for f in lf):
                lint_tools_used.add('biome')
        else:
            script_inventory['other'].append(script_file.name)
            findings = []

        # Check for unit tests
        if tests_dir.exists():
            stem = script_file.stem
            test_patterns = [
                f'test_{stem}{ext}', f'test-{stem}{ext}',
                f'{stem}_test{ext}', f'{stem}-test{ext}',
                f'test_{stem}.py', f'test-{stem}.py',
            ]
            has_test = any((tests_dir / t).exists() for t in test_patterns)
        else:
            has_test = False

        if not has_test:
            missing_tests.append(script_file.name)
            findings.append({
                'file': rel_path, 'line': 1,
                'severity': 'medium', 'category': 'tests',
                'issue': f'No unit test found for {script_file.name}',
                'fix': f'Create scripts/tests/test-{script_file.stem}{ext} with test cases',
            })

        all_findings.extend(findings)

    # Check if tests/ directory exists at all
    if script_files and not tests_dir.exists():
        all_findings.append({
            'file': 'scripts/tests/',
            'line': 0,
            'severity': 'high',
            'category': 'tests',
            'issue': 'scripts/tests/ directory does not exist — no unit tests',
            'fix': 'Create scripts/tests/ with test files for each script',
        })

    # Merge lint findings into all findings
    all_findings.extend(lint_findings)

    # Build summary
    by_severity = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    by_category: dict[str, int] = {}
    for f in all_findings:
        sev = f['severity']
        if sev in by_severity:
            by_severity[sev] += 1
        cat = f['category']
        by_category[cat] = by_category.get(cat, 0) + 1

    total_scripts = sum(len(v) for v in script_inventory.values())
    status = 'pass'
    if by_severity['critical'] > 0:
        status = 'fail'
    elif by_severity['high'] > 0:
        status = 'warning'
    elif total_scripts == 0:
        status = 'pass'

    lint_issue_count = sum(1 for f in lint_findings if f['category'] == 'lint')

    return {
        'scanner': 'scripts',
        'script': 'scan-scripts.py',
        'version': '2.0.0',
        'skill_path': str(skill_path),
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status': status,
        'issues': all_findings,
        'lint_summary': {
            'tools_used': sorted(lint_tools_used),
            'files_linted': total_scripts,
            'lint_issues': lint_issue_count,
        },
        'script_summary': {
            'total_scripts': total_scripts,
            'by_type': {k: len(v) for k, v in script_inventory.items()},
            'scripts': {k: v for k, v in script_inventory.items() if v},
            'missing_tests': missing_tests,
        },
        'summary': {
            'total_issues': len(all_findings),
            'by_severity': by_severity,
            'by_category': by_category,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Scan BMad skill scripts for quality, portability, agentic design, and lint issues',
    )
    parser.add_argument(
        'skill_path',
        type=Path,
        help='Path to the skill directory to scan',
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Write JSON output to file instead of stdout',
    )
    args = parser.parse_args()

    if not args.skill_path.is_dir():
        print(f"Error: {args.skill_path} is not a directory", file=sys.stderr)
        return 2

    result = scan_skill_scripts(args.skill_path)
    output = json.dumps(result, indent=2)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output)
        print(f"Results written to {args.output}", file=sys.stderr)
    else:
        print(output)

    return 0 if result['status'] == 'pass' else 1


if __name__ == '__main__':
    sys.exit(main())
