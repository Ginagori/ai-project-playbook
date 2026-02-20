#!/bin/bash
# Pre-commit hook: Core Soul protection
# Install: cp scripts/pre-commit-core-soul.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
# Or append to existing pre-commit hook.

CORE_SOUL_FILE="agent/core_soul.py"
HASH_FILE=".github/core_soul.sha256"

# Check if core_soul.py is in the staged changes
if git diff --cached --name-only | grep -q "^${CORE_SOUL_FILE}$"; then
    echo ""
    echo "============================================"
    echo "  WARNING: Core Soul modification detected"
    echo "============================================"
    echo ""
    echo "You are about to commit changes to ${CORE_SOUL_FILE}."
    echo "This file contains Archie's immutable identity."
    echo ""
    echo "Core Soul Change Protocol:"
    echo "  1. Ensure the change is justified and reviewed"
    echo "  2. Update EXPECTED_HASH in core_soul.py"
    echo "  3. Update .github/core_soul.sha256"
    echo "  4. CI will verify all 3 values match"
    echo ""

    # Verify the hash is still a hardcoded string (not dynamically computed)
    if grep -q 'EXPECTED_HASH = hashlib' "${CORE_SOUL_FILE}"; then
        echo "BLOCKED: EXPECTED_HASH must be a hardcoded string literal, not computed."
        echo "Commit aborted."
        exit 1
    fi

    # Compute hash from staged content
    COMPUTED_HASH=$(git show :"${CORE_SOUL_FILE}" | python3 -c "
import sys, hashlib, ast
source = sys.stdin.read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == 'CORE_SOUL':
                print(hashlib.sha256(ast.literal_eval(node.value).encode('utf-8')).hexdigest())
                sys.exit(0)
print('ERROR')
" 2>/dev/null)

    # Extract hardcoded hash from staged content
    HARDCODED_HASH=$(git show :"${CORE_SOUL_FILE}" | grep -oP 'EXPECTED_HASH = "([a-f0-9]{64})"' | grep -oP '[a-f0-9]{64}')

    if [ "$COMPUTED_HASH" != "$HARDCODED_HASH" ]; then
        echo "BLOCKED: CORE_SOUL content does not match EXPECTED_HASH."
        echo "  Computed: ${COMPUTED_HASH}"
        echo "  Hardcoded: ${HARDCODED_HASH}"
        echo ""
        echo "Update EXPECTED_HASH to match the new content."
        echo "Commit aborted."
        exit 1
    fi

    # Check if .github/core_soul.sha256 is also staged
    if ! git diff --cached --name-only | grep -q "^${HASH_FILE}$"; then
        echo "BLOCKED: You changed ${CORE_SOUL_FILE} but did not update ${HASH_FILE}."
        echo "Both files must be updated together."
        echo "Commit aborted."
        exit 1
    fi

    echo "Core Soul hash verified. Proceeding with commit."
    echo ""
fi
