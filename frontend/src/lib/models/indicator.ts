import type { LineData } from 'lightweight-charts';

/**
 * @example { bblow: [], bbhigh: []}
 */
export type IndicatorValues = Record<string, LineData[]>;
// TODO merge these two types
export type IndicatorValue = Record<string, LineData>;

export interface Indicator {
	name: string;
	parameters: Record<string, number | string>;
	history?: IndicatorValues;
	readonly key: string;
}

// -- Parameter schema -----------------------------------------------------
// Drives the ConditionNode UI generically: selects and number inputs
// are rendered automatically from this schema.

export interface IndicatorParameter {
	name: string;
	displayName: string;
	htmlTag: 'input' | 'select';
	min?: number;
	max?: number;
	default: number | string;
	/**
	 * Present only if htmlTag == 'select'
	 */
	options?: { name: string; displayName: string }[];
}

export type ComparisonOperator = '<' | '>' | '=' | '<=' | '>=' | '!=';

export interface IndicatorSchema {
	name: string;
	displayName: string;
	parameters: IndicatorParameter[];
}

const LENGTH_PARAMETER: IndicatorParameter = {
	name: 'length',
	displayName: 'Length',
	htmlTag: 'input',
	min: 1,
	max: 200,
	default: 20
};

// -- Indicator schemas (single source of truth) ----------------------------

const INDICATOR_SCHEMAS: IndicatorSchema[] = [
	{
		name: 'sma',
		displayName: 'SMA',
		parameters: [LENGTH_PARAMETER]
	},
	{
		name: 'bollinger_bands',
		displayName: 'Bollinger Bands',
		parameters: [
			{
				name: 'band',
				displayName: 'Band',
				htmlTag: 'select',
				default: 'upper',
				options: [
					{ name: 'upper', displayName: 'Upper' },
					{ name: 'lower', displayName: 'Lower' }
				]
			},
			LENGTH_PARAMETER,
			{
				name: 'std_dev',
				displayName: 'StDev',
				htmlTag: 'input',
				min: 1,
				max: 5,
				default: 2
			}
		]
	}
];

const indicatorSchemasByName = new Map<string, IndicatorSchema>(
	INDICATOR_SCHEMAS.map((schema) => [schema.name, schema])
);

/** Returns all indicator schemas. */
export function getIndicatorSchemas(): IndicatorSchema[] {
	return INDICATOR_SCHEMAS;
}

/** Returns the schema for a specific indicator by name. */
export function getIndicatorSchema(name: string): IndicatorSchema {
	const schema = indicatorSchemasByName.get(name);
	if (!schema) {
		const availableNames = Array.from(indicatorSchemasByName.keys()).join(', ');
		throw new Error(`Unknown indicator: "${name}". Available: ${availableNames}`);
	}
	return schema;
}

// -- Helpers ---------------------------------------------------------------

export function createIndicator(indicatorName: string): Indicator {
	const schema = getIndicatorSchema(indicatorName);

	const parameters: Record<string, number | string> = {};
	for (const param of schema.parameters) {
		parameters[param.name] = param.default;
	}

	return {
		name: indicatorName,
		parameters,
		get key(): string {
			const paramValues = Object.values(parameters).join(':');
			return `${indicatorName}:${paramValues}`;
		}
	};
}
