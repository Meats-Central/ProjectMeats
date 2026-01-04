#!/bin/bash
# Pre-commit hook to validate heredoc syntax in workflow files
# Prevents indented heredoc closing delimiters that cause syntax errors

set -e

echo "🔍 Checking heredoc syntax in workflow files..."

FAILED=0

# Check all YAML workflow files
shopt -s nullglob
for file in .github/workflows/*.yml .github/workflows/*.yaml; do
  if [ ! -f "$file" ]; then
    continue
  fi
  
  # Look for heredoc markers
  while IFS=: read -r line_num content; do
    # Check if using <<- (allows indentation)
    if echo "$content" | grep -q "<<-"; then
      # <<- allows indented closing delimiter, skip validation
      continue
    fi
    
    # Extract delimiter name for << (without dash)
    DELIMITER=$(echo "$content" | sed -n "s/.*<<\s*['\"]\\?\([A-Z_]*\)['\"]\\?.*/\1/p")
    
    if [ -n "$DELIMITER" ] && [ "$DELIMITER" != "SSH" ] && [ "$DELIMITER" != "ENVJS" ]; then
      # Find closing delimiter
      CLOSING_LINE=$(awk "NR>$line_num && /^[[:space:]]+$DELIMITER\$/ {print NR; exit}" "$file")
      
      if [ -n "$CLOSING_LINE" ]; then
        echo "❌ ERROR in $file:"
        echo "   Line $line_num: Heredoc '$DELIMITER' has INDENTED closing delimiter at line $CLOSING_LINE"
        echo "   Closing delimiters must be at column 0 (no indentation)"
        echo ""
        echo "   Fix: Either unindent the closing delimiter OR use <<- operator"
        echo ""
        FAILED=1
      fi
    fi
  done < <(grep -n "<<" "$file" 2>/dev/null || true)
done

if [ $FAILED -eq 1 ]; then
  echo ""
  echo "════════════════════════════════════════════════════════════"
  echo "❌ Heredoc syntax validation FAILED"
  echo "════════════════════════════════════════════════════════════"
  echo ""
  echo "Heredoc closing delimiters MUST be at column 0 (no spaces/tabs)."
  echo ""
  echo "Example of INCORRECT syntax (will fail):"
  echo "  cat > file.txt << 'EOF'"
  echo "  content here"
  echo "          EOF  # ❌ INDENTED - will cause syntax error"
  echo ""
  echo "Example of CORRECT syntax:"
  echo "  cat > file.txt << 'EOF'"
  echo "  content here"
  echo "EOF  # ✅ NO INDENTATION"
  echo ""
  echo "Alternative (use <<- to allow indentation):"
  echo "  cat > file.txt <<- 'EOF'"
  echo "  	content here"
  echo "  	EOF  # ✅ Tabs allowed with <<-"
  echo ""
  echo "════════════════════════════════════════════════════════════"
  exit 1
fi

echo "✅ All heredoc syntax is valid"
exit 0
