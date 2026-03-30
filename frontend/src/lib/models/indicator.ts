import type { LineData } from 'lightweight-charts';

/**
 * @example { bblow: [], bbhigh: []}
 */
export type IndicatorValues = Record<string, LineData[]>;
// TODO merge these two types
export type IndicatorValue = Record<string, LineData>;

export type IndicatorName = 'price' | 'sma' | 'bollinger_bands' | 'hour';

export interface Indicator {
	name: IndicatorName;
	parameters: Record<string, number | string>;
	history?: IndicatorValues;
	readonly key: string;
}

// ── Parameter schema ────────────────────────────────────────────────
// Drives the ConditionNode UI generically: selects and number inputs
// are rendered automatically from this schema.

export interface IndicatorParameter {
	name: string;
	displayName: string;
	htmlTag: 'input' | 'select';
	/** If true, this param is part of the plot indicator key (used for deduplication).
	 *  If false, it's condition-specific (e.g. band, barsAgo) and excluded from the key. */
	plotParam: boolean;
	min?: number;
	max?: number;
	default: number | string;
	/**
	 * Present only if htmlTag == 'select'
	 */
	options?: { name: string; displayName: string }[];
}
export type ComparisonOperator = '<' | '>' | '=' | '<=' | '>=' | '!=';

export const INDICATOR_DISPLAY_NAMES: { value: IndicatorName; displayName: string }[] = [
	{ value: 'price', displayName: 'Price' },
	{ value: 'sma', displayName: 'SMA' },
	{ value: 'bollinger_bands', displayName: 'Bollinger Bands' },
	{ value: 'hour', displayName: 'Hour' }
];

export const INDICATOR_PARAMETERS: Record<IndicatorName, IndicatorParameter[]> = {
	price: [
		{
			name: 'shift',
			displayName: 'shift',
			htmlTag: 'input',
			plotParam: false,
			min: 0,
			max: 100,
			default: 0
		}
	],
	hour: [
		{
			name: 'shift',
			displayName: 'shift',
			htmlTag: 'input',
			plotParam: false,
			min: 0,
			max: 100,
			default: 0
		}
	],
	sma: [
		{
			name: 'length',
			displayName: 'Length',
			htmlTag: 'input',
			plotParam: true,
			min: 1,
			max: 200,
			default: 20
		}
	],
	bollinger_bands: [
		{
			name: 'band',
			displayName: 'Band',
			htmlTag: 'select',
			plotParam: false,
			default: 'upper',
			options: [{ name: 'upper', displayName: 'lower' }]
		},
		{
			name: 'length',
			displayName: 'Length',
			htmlTag: 'input',
			plotParam: true,
			min: 1,
			max: 200,
			default: 20
		},
		{
			name: 'stDev',
			displayName: 'StDev',
			htmlTag: 'input',
			plotParam: true,
			min: 1,
			max: 5,
			default: 2
		}
	]
};
// ── Helpers ─────────────────────────────────────────────────────────

export function createIndicator(indicatorName: IndicatorName): Indicator {
	const parameters: Record<string, number | string> = {};
	for (const p of INDICATOR_PARAMETERS[indicatorName]) parameters[p.name] = p.default;

	return {
		name: indicatorName,
		parameters,
		get key(): string {
			const plotParams = INDICATOR_PARAMETERS[indicatorName].filter((p) => p.plotParam);
			const values = plotParams.map((p) => parameters[p.name]).join(':');
			return `${indicatorName}:${values}`;
		}
	};
}
