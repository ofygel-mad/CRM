export const colors = {
  bg: {
    base: '#FAFAF8',
    elevated: '#FFFFFF',
    overlay: 'rgba(0, 0, 0, 0.4)',
    muted: '#F3F4F6',
  },
  amber: {
    50: '#FFFBEB',
    100: '#FEF3C7',
    400: '#FBBF24',
    500: '#F59E0B',
    600: '#D97706',
    700: '#B45309',
  },
  gray: {
    50: '#F9FAFB',
    100: '#F3F4F6',
    200: '#E5E7EB',
    300: '#D1D5DB',
    400: '#9CA3AF',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',
    900: '#111827',
  },
  success: { light: '#D1FAE5', DEFAULT: '#10B981', dark: '#065F46' },
  warning: { light: '#FEF3C7', DEFAULT: '#F59E0B', dark: '#92400E' },
  danger: { light: '#FEE2E2', DEFAULT: '#EF4444', dark: '#991B1B' },
  info: { light: '#DBEAFE', DEFAULT: '#3B82F6', dark: '#1E3A8A' },
} as const;

export const typography = {
  fontDisplay: '"Plus Jakarta Sans", sans-serif',
  fontBody: '"DM Sans", sans-serif',
  fontMono: '"JetBrains Mono", monospace',
} as const;

export const motion = {
  spring: { stiffness: 400, damping: 30 },
  springGentle: { stiffness: 200, damping: 25 },
  duration: { fast: 0.15, base: 0.2, slow: 0.35 },
} as const;
