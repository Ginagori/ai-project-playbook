# Design System Creation - Desde Código Existente

**Extraer design system desde codebase existente (Lovable, custom code, etc.)**

---

## 🎯 Objetivo

Crear design system consistente desde código existente sin consistencia.

**Resultado:** Component library + Theming + Storybook + Documentation

**Tiempo:** 1-2 semanas

---

## 📋 Cuándo Necesitas Design System

**Red flags:**
- [ ] 50+ componentes sin naming consistency
- [ ] Colores hardcoded (ej: `#3B82F6` everywhere)
- [ ] Spacing inconsistente (`px`, `rem`, valores random)
- [ ] Componentes duplicados (3 versiones de Button)
- [ ] Nuevo feature = reinventar UI cada vez

**Beneficios:**
- ✅ Consistency automática
- ✅ Development speed (reutiliza components)
- ✅ Easy theming (dark mode, white-label)
- ✅ Onboarding rápido (nuevos developers)

---

## 🚀 PASO 1: Audit Componentes Existentes (2-3 días)

### 1.1 Inventario Completo

**Prompt para Claude:**
```
Analiza todos los componentes en src/components/ y crea inventario:

1. Lista de componentes únicos
2. Variantes de cada componente
3. Props que reciben
4. Estilos aplicados (colores, spacing, typography)

Output formato markdown table.
```

**Ejemplo output:**
```markdown
| Component | Variantes | Props | Colores Usados | Spacing |
|-----------|-----------|-------|----------------|---------|
| Button | primary, secondary, danger | onClick, disabled, size | #3B82F6, #EF4444 | px-4 py-2, px-6 py-3 |
| Input | text, email, password | value, onChange, error | #D1D5DB, #EF4444 | p-3, p-2 |
| Card | default, bordered | children, className | #FFFFFF, #F3F4F6 | p-6, p-4 |
```

### 1.2 Extraer Design Tokens

**Colores:**
```javascript
// design-tokens/colors.js
export const colors = {
  // Primary
  primary: {
    50: '#EFF6FF',
    100: '#DBEAFE',
    500: '#3B82F6',  // Main
    600: '#2563EB',
    900: '#1E3A8A',
  },

  // Semantic
  success: '#10B981',
  error: '#EF4444',
  warning: '#F59E0B',

  // Neutrals
  gray: {
    50: '#F9FAFB',
    100: '#F3F4F6',
    500: '#6B7280',
    900: '#111827',
  }
}
```

**Spacing:**
```javascript
// design-tokens/spacing.js
export const spacing = {
  xs: '0.25rem',   // 4px
  sm: '0.5rem',    // 8px
  md: '1rem',      // 16px
  lg: '1.5rem',    // 24px
  xl: '2rem',      // 32px
  '2xl': '3rem',   // 48px
}
```

**Typography:**
```javascript
// design-tokens/typography.js
export const typography = {
  fontFamily: {
    sans: 'Inter, system-ui, sans-serif',
    mono: 'Fira Code, monospace',
  },

  fontSize: {
    xs: '0.75rem',    // 12px
    sm: '0.875rem',   // 14px
    base: '1rem',     // 16px
    lg: '1.125rem',   // 18px
    xl: '1.25rem',    // 20px
    '2xl': '1.5rem',  // 24px
    '3xl': '1.875rem', // 30px
  },

  fontWeight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  }
}
```

---

## 🎨 PASO 2: Crear Component Library (1 semana)

### 2.1 Setup Estructura

```bash
src/
├── design-system/
│   ├── tokens/
│   │   ├── colors.ts
│   │   ├── spacing.ts
│   │   ├── typography.ts
│   │   └── index.ts
│   ├── components/
│   │   ├── Button/
│   │   │   ├── Button.tsx
│   │   │   ├── Button.stories.tsx
│   │   │   ├── Button.test.tsx
│   │   │   └── index.ts
│   │   ├── Input/
│   │   ├── Card/
│   │   └── index.ts
│   ├── hooks/
│   │   ├── useTheme.ts
│   │   └── index.ts
│   └── index.ts
```

### 2.2 Ejemplo: Button Component

```tsx
// design-system/components/Button/Button.tsx
import { colors, spacing } from '../../tokens'

export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  children: React.ReactNode
  onClick?: () => void
  disabled?: boolean
  fullWidth?: boolean
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  children,
  onClick,
  disabled = false,
  fullWidth = false
}) => {
  const variantStyles = {
    primary: {
      bg: colors.primary[500],
      hover: colors.primary[600],
      text: '#FFFFFF'
    },
    secondary: {
      bg: colors.gray[100],
      hover: colors.gray[200],
      text: colors.gray[900]
    },
    danger: {
      bg: colors.error,
      hover: '#DC2626',
      text: '#FFFFFF'
    }
  }

  const sizeStyles = {
    sm: { padding: `${spacing.xs} ${spacing.sm}`, fontSize: '0.875rem' },
    md: { padding: `${spacing.sm} ${spacing.md}`, fontSize: '1rem' },
    lg: { padding: `${spacing.md} ${spacing.lg}`, fontSize: '1.125rem' }
  }

  const styles = {
    backgroundColor: variantStyles[variant].bg,
    color: variantStyles[variant].text,
    padding: sizeStyles[size].padding,
    fontSize: sizeStyles[size].fontSize,
    width: fullWidth ? '100%' : 'auto',
    border: 'none',
    borderRadius: '0.375rem',
    cursor: disabled ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.5 : 1,
    fontWeight: 500,
    transition: 'all 0.2s'
  }

  return (
    <button
      style={styles}
      onClick={onClick}
      disabled={disabled}
      onMouseEnter={(e) => {
        if (!disabled) {
          e.currentTarget.style.backgroundColor = variantStyles[variant].hover
        }
      }}
      onMouseLeave={(e) => {
        if (!disabled) {
          e.currentTarget.style.backgroundColor = variantStyles[variant].bg
        }
      }}
    >
      {children}
    </button>
  )
}
```

### 2.3 Migrar Componentes Existentes

**Antes (hardcoded):**
```tsx
<button className="bg-blue-500 px-4 py-2 text-white rounded">
  Click me
</button>
```

**Después (design system):**
```tsx
import { Button } from '@/design-system'

<Button variant="primary" size="md">
  Click me
</Button>
```

---

## 📚 PASO 3: Storybook Setup (2 días)

### 3.1 Instalar Storybook

```bash
npx storybook@latest init
```

### 3.2 Crear Stories

```tsx
// Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react'
import { Button } from './Button'

const meta: Meta<typeof Button> = {
  title: 'Design System/Button',
  component: Button,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'danger']
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg']
    }
  }
}

export default meta
type Story = StoryObj<typeof Button>

export const Primary: Story = {
  args: {
    variant: 'primary',
    children: 'Primary Button'
  }
}

export const Secondary: Story = {
  args: {
    variant: 'secondary',
    children: 'Secondary Button'
  }
}

export const AllSizes: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '1rem', flexDirection: 'column' }}>
      <Button size="sm">Small</Button>
      <Button size="md">Medium</Button>
      <Button size="lg">Large</Button>
    </div>
  )
}
```

### 3.3 Deploy Storybook

```bash
# Build storybook
npm run build-storybook

# Deploy a Netlify (separate site)
# Netlify dashboard → New site → Drop build-storybook/ folder
```

---

## 🎨 PASO 4: Theming Support (1-2 días)

### 4.1 Theme Provider

```tsx
// design-system/ThemeProvider.tsx
import { createContext, useContext, useState } from 'react'

type Theme = 'light' | 'dark'

const ThemeContext = createContext<{
  theme: Theme
  toggleTheme: () => void
}>({
  theme: 'light',
  toggleTheme: () => {}
})

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<Theme>('light')

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light')
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      <div data-theme={theme}>
        {children}
      </div>
    </ThemeContext.Provider>
  )
}

export const useTheme = () => useContext(ThemeContext)
```

### 4.2 Theme-Aware Components

```tsx
// Update Button to use theme
import { useTheme } from '../../ThemeProvider'

export const Button: React.FC<ButtonProps> = ({ ... }) => {
  const { theme } = useTheme()

  const variantStyles = {
    primary: {
      light: { bg: colors.primary[500], text: '#FFFFFF' },
      dark: { bg: colors.primary[400], text: colors.gray[900] }
    },
    // ...
  }

  const currentTheme = variantStyles[variant][theme]

  // Use currentTheme.bg, currentTheme.text
}
```

---

## 🎓 Key Takeaways

1. **Audit first** - Entender qué existe antes de crear
2. **Extract tokens** - Colores, spacing, typography consistentes
3. **Component library** - Componentes reutilizables con API clara
4. **Storybook** - Documentation visual para team
5. **Theming** - Dark mode, white-label desde día 1

---

**Tiempo total:** 1-2 semanas para design system básico pero funcional.
