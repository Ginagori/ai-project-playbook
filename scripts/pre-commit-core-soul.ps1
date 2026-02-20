# Pre-commit hook: Core Soul protection (PowerShell/Windows)
# Install: copy this content into .git/hooks/pre-commit (as a shell script wrapper)
# Or run manually before committing changes to core_soul.py

$CORE_SOUL_FILE = "agent/core_soul.py"
$HASH_FILE = ".github/core_soul.sha256"

# Check if core_soul.py is in staged changes
$staged = git diff --cached --name-only
if ($staged -match [regex]::Escape($CORE_SOUL_FILE)) {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Yellow
    Write-Host "  WARNING: Core Soul modification detected" -ForegroundColor Yellow
    Write-Host "============================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "You are about to commit changes to $CORE_SOUL_FILE."
    Write-Host "This file contains Archie's immutable identity."
    Write-Host ""

    # Verify hash is hardcoded
    $content = git show ":$CORE_SOUL_FILE"
    if ($content -match 'EXPECTED_HASH = hashlib') {
        Write-Host "BLOCKED: EXPECTED_HASH must be a hardcoded string, not computed." -ForegroundColor Red
        exit 1
    }

    # Compute hash from staged content
    $computedHash = python -c @"
import sys, hashlib, ast
source = r'''$($content -join "`n")'''
# Fallback: read from git
import subprocess
result = subprocess.run(['git', 'show', ':$CORE_SOUL_FILE'], capture_output=True, text=True)
source = result.stdout
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == 'CORE_SOUL':
                print(hashlib.sha256(ast.literal_eval(node.value).encode('utf-8')).hexdigest())
                sys.exit(0)
"@

    # Extract hardcoded hash
    $hashMatch = [regex]::Match(($content -join "`n"), 'EXPECTED_HASH = "([a-f0-9]{64})"')
    $hardcodedHash = $hashMatch.Groups[1].Value

    if ($computedHash.Trim() -ne $hardcodedHash) {
        Write-Host "BLOCKED: CORE_SOUL content does not match EXPECTED_HASH." -ForegroundColor Red
        Write-Host "  Computed: $($computedHash.Trim())"
        Write-Host "  Hardcoded: $hardcodedHash"
        exit 1
    }

    # Check if hash file is also staged
    if ($staged -notmatch [regex]::Escape($HASH_FILE)) {
        Write-Host "BLOCKED: Changed $CORE_SOUL_FILE but not $HASH_FILE." -ForegroundColor Red
        Write-Host "Both must be updated together."
        exit 1
    }

    Write-Host "Core Soul hash verified. Proceeding." -ForegroundColor Green
}
