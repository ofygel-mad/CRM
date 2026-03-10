export function useCapabilities() { return { can: (_cap: string) => true, mode: 'basic' as const, isBasic: true, isAdvanced: false, isIndustrial: false }; }
