export function formatMoney(
  amount: number,
  currency: string = 'KZT',
  locale: string = 'ru-KZ',
): string {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
    currencyDisplay: 'narrowSymbol',
  }).format(amount);
}

export function formatNumber(
  amount: number,
  locale: string = 'ru-KZ',
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
