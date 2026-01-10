/**
 * ESLint Custom Rule: no-hardcoded-colors
 * 
 * Prevents hardcoded hex colors in styled-components and inline styles.
 * Enforces use of theme variables or standardized color palette.
 * 
 * Examples of INCORRECT code:
 * - const Button = styled.button`background: #667eea;`
 * - <div style={{ color: '#FF0000' }} />
 * - border: 1px solid #e9ecef
 * 
 * Examples of CORRECT code:
 * - const Button = styled.button`background: rgb(var(--color-primary));`
 * - const Button = styled.button`background: rgb(34, 197, 94);` // Standardized green
 * - <div style={{ color: 'rgb(var(--color-primary))' }} />
 * 
 * @author ProjectMeats UI Standardization Team
 * @date 2026-01-10
 */

module.exports = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Disallow hardcoded hex colors in favor of theme variables or standardized palette',
      category: 'Best Practices',
      recommended: true,
      url: 'https://github.com/Meats-Central/ProjectMeats/blob/main/frontend/UI_STANDARDS.md#color-system'
    },
    fixable: null,
    schema: [{
      type: 'object',
      properties: {
        allowedColors: {
          type: 'array',
          items: { type: 'string' },
          description: 'Array of hex colors that are explicitly allowed'
        }
      },
      additionalProperties: false
    }],
    messages: {
      hardcodedColor: 'Hardcoded hex color "{{color}}" detected. Use theme variables (e.g., rgb(var(--color-primary))) or standardized palette colors instead.',
      hardcodedColorWithSuggestion: 'Hardcoded hex color "{{color}}" detected. Consider using: {{suggestion}}'
    }
  },

  create(context) {
    const options = context.options[0] || {};
    const allowedColors = new Set((options.allowedColors || []).map(c => c.toLowerCase()));

    const hexColorRegex = /#([0-9a-fA-F]{3}){1,2}([0-9a-fA-F]{2})?/g;

    const standardizedColors = {
      '#22c55e': 'rgb(34, 197, 94) - Success color',
      '#16a34a': 'rgb(34, 197, 94) - Success color',
      '#10b981': 'rgb(34, 197, 94) - Success color',
      '#eab308': 'rgb(234, 179, 8) - Warning color',
      '#ffc107': 'rgb(234, 179, 8) - Warning color',
      '#f59e0b': 'rgb(234, 179, 8) - Warning color',
      '#ef4444': 'rgb(239, 68, 68) - Error color',
      '#dc2626': 'rgb(239, 68, 68) - Error color',
      '#dc3545': 'rgb(239, 68, 68) - Error color',
      '#ff4d4f': 'rgb(239, 68, 68) - Error color',
      '#c82333': 'rgb(239, 68, 68) - Error color',
      '#3b82f6': 'rgb(59, 130, 246) - Info color',
      '#3498db': 'rgb(59, 130, 246) - Info color',
      '#2980b9': 'rgb(59, 130, 246) - Info color',
      '#667eea': 'rgb(var(--color-primary)) - Theme primary',
      '#5a67d8': 'rgb(var(--color-primary)) - Theme primary',
      '#764ba2': 'rgb(var(--color-primary)) - Theme primary',
      '#e9ecef': 'rgb(var(--color-border)) - Theme border',
      '#f1f3f4': 'rgb(var(--color-border)) - Theme border',
      '#495057': 'rgb(var(--color-text-secondary)) - Theme secondary text',
      '#5a6268': 'rgb(var(--color-text-secondary)) - Theme secondary text',
      '#f0fdf4': 'rgba(34, 197, 94, 0.15) - Success background',
      '#fef2f2': 'rgba(239, 68, 68, 0.15) - Error background',
      '#bbf7d0': 'rgba(34, 197, 94, 0.2) - Success border/background',
      '#fecaca': 'rgba(239, 68, 68, 0.2) - Error border/background',
      '#d4edda': 'rgba(34, 197, 94, 0.15) - Success background',
      '#f8d7da': 'rgba(239, 68, 68, 0.15) - Error background'
    };

    function isAllowedColor(color) {
      const normalized = color.toLowerCase();
      return allowedColors.has(normalized) || standardizedColors[normalized];
    }

    function getSuggestion(color) {
      const normalized = color.toLowerCase();
      return standardizedColors[normalized] || 'rgb(var(--color-primary)), rgb(var(--color-border)), or standardized palette color';
    }

    function checkTemplateLiteral(node) {
      const sourceCode = context.getSourceCode();
      const text = sourceCode.getText(node);
      
      let match;
      while ((match = hexColorRegex.exec(text)) !== null) {
        const color = match[0];
        
        if (!isAllowedColor(color)) {
          const suggestion = getSuggestion(color);
          
          context.report({
            node,
            messageId: 'hardcodedColorWithSuggestion',
            data: {
              color,
              suggestion
            }
          });
        }
      }
    }

    function checkObjectExpression(node) {
      if (node.properties) {
        node.properties.forEach(prop => {
          if (prop.value && prop.value.type === 'Literal' && typeof prop.value.value === 'string') {
            const value = prop.value.value;
            const matches = value.match(hexColorRegex);
            
            if (matches) {
              matches.forEach(color => {
                if (!isAllowedColor(color)) {
                  const suggestion = getSuggestion(color);
                  
                  context.report({
                    node: prop.value,
                    messageId: 'hardcodedColorWithSuggestion',
                    data: {
                      color,
                      suggestion
                    }
                  });
                }
              });
            }
          }
        });
      }
    }

    return {
      TemplateLiteral(node) {
        const parent = node.parent;
        if (parent && parent.type === 'TaggedTemplateExpression') {
          const tag = parent.tag;
          if (
            (tag.type === 'MemberExpression' && tag.object.name === 'styled') ||
            (tag.type === 'CallExpression' && tag.callee.name === 'styled') ||
            (tag.type === 'Identifier' && tag.name === 'css')
          ) {
            checkTemplateLiteral(node);
          }
        }
      },

      JSXAttribute(node) {
        if (node.name.name === 'style' && node.value) {
          if (node.value.type === 'JSXExpressionContainer' && node.value.expression.type === 'ObjectExpression') {
            checkObjectExpression(node.value.expression);
          }
        }
      }
    };
  }
};
