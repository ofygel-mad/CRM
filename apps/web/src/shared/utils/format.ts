export function formatMoney(
  amount: number,
  currency: string = 'KZT',
  locale: string = 'ru-KZ',
  compact = false,
): string {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
    currencyDisplay: 'narrowSymbol',
    ...(compact ? { notation: 'compact' } : {}),
  }).format(amount);
}

export function formatNumber(
  amount: number,
  locale: string = 'ru-KZ',
  compact = false,
): string {
  return new Intl.NumberFormat(locale, { maximumFractionDigits: 0 }).format(amount);
}

export function currencySymbol(currency: string): string {
  const symbols: Record<string, string> = {
    KZT: '₸',
    RUB: '₽',
    USD: '$',
    EUR: '€',
  };
  return symbols[currency] ?? currency;
}
