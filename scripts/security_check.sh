#!/usr/bin/env bash
set -euo pipefail

echo "=========================================="
echo "🛡️  Running Repository Security Audit"
echo "=========================================="

FAILED=0

# 1. Check for malicious font/asset masquerading
echo "[+] Checking static asset file types..."
for file in $(find public/ -type f 2>/dev/null); do
  file_type=$(file -b --mime-type "$file")
  case "$file" in
    *.woff|*.woff2|*.ttf|*.eot|*.otf)
      if [[ "$file_type" == *"text"* || "$file_type" == *"javascript"* ]]; then
        echo "❌ ALERT: Suspicious file masquerading as font: $file (MIME: $file_type)"
        FAILED=1
      fi
      ;;
    *.png|*.jpg|*.jpeg|*.gif|*.ico)
      if [[ "$file_type" == *"text"* || "$file_type" == *"javascript"* ]]; then
        echo "❌ ALERT: Suspicious file masquerading as image: $file (MIME: $file_type)"
        FAILED=1
      fi
      ;;
  esac
done

# 2. Check for known malware signatures or C2 Ethereum addresses
echo "[+] Checking for malware signatures & C2 addresses..."
KNOWN_BAD_ADDR="0xa322E5f3D311D3080e6f0121063e9aDC2490Ef1a"
if grep -rnI --exclude="security_check.sh" --exclude-dir=".git" "$KNOWN_BAD_ADDR" . ; then
  echo "❌ ALERT: Found known attacker Ethereum C2 address in repository!"
  FAILED=1
fi

# 3. Check VS Code tasks for automatic execution hooks
echo "[+] Auditing VS Code configuration for hidden auto-run tasks..."
if [ -f ".vscode/tasks.json" ]; then
  if grep -E '"runOn"\s*:\s*"folderOpen"' .vscode/tasks.json >/dev/null 2>&1; then
    echo "❌ ALERT: Found 'runOn: folderOpen' in .vscode/tasks.json!"
    FAILED=1
  fi
fi

if [ -f ".vscode/settings.json" ]; then
  if grep -E '"task\.allowAutomaticTasks"\s*:\s*true' .vscode/settings.json >/dev/null 2>&1; then
    echo "❌ ALERT: 'task.allowAutomaticTasks' is set to true in .vscode/settings.json!"
    FAILED=1
  fi
fi

echo "------------------------------------------"
if [ "$FAILED" -eq 0 ]; then
  echo "✅ All security checks passed! No threats detected."
  exit 0
else
  echo "⚠️  Security audit failed. Review the warnings above."
  exit 1
fi
