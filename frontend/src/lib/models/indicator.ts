import type { LineData } from 'lightweight-charts';
import { API_BASE_URL } from '$lib/utils/env';

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

export interface IndicatorSchema {
	name: string;
	displayName: string;
	parameters: IndicatorParameter[];
}

// -- Module-level state for fetched schemas --------------------------------
// Schemas are loaded once from the backend and cached for the session lifetime.

let indicatorSchemasByName: Map<string, IndicatorSchema> | null = null;
let indicatorSchemasList: IndicatorSchema[] | null = null;

/**
 * Fetches indicator schemas from the backend and caches them at module level.
 * Must be called once before any other schema accessor is used (e.g. in a
 * top-level layout load or app initialization).
 */
export async function loadIndicatorSchemas(): Promise<void> {
	const response = await fetch(`${API_BASE_URL}/api/indicator-schemas`);
	if (!response.ok) {
		throw new Error(`Failed to fetch indicator schemas: ${response.status} ${response.statusText}`);
	}

	const schemas: IndicatorSchema[] = await response.json();

	indicatorSchemasByName = new Map(schemas.map((schema) => [schema.name, schema]));
	indicatorSchemasList = schemas;
}

/**
 * Returns all indicator schemas fetched from the backend.
 * @throws if `loadIndicatorSchemas()` has not been called yet.
 */
export function getIndicatorSchemas(): IndicatorSchema[] {
	if (indicatorSchemasList === null) {
		throw new Error(
			'Indicator schemas have not been loaded yet. Call loadIndicatorSchemas() first.'
		);
	}
	return indicatorSchemasList;
}

/**
 * Returns the schema for a specific indicator by name.
 * @throws if schemas have not been loaded or the name is unknown.
 */
export function getIndicatorSchema(name: string): IndicatorSchema {
	if (indicatorSchemasByName === null) {
		throw new Error(
			'Indicator schemas have not been loaded yet. Call loadIndicatorSchemas() first.'
		);
	}

	const schema = indicatorSchemasByName.get(name);
	if (!schema) {
		const availableNames = Array.from(indicatorSchemasByName.keys()).join(', ');
		throw new Error(`Unknown indicator: "${name}". Available: ${availableNames}`);
	}
	return schema;
}

// -- Helpers ---------------------------------------------------------------

/**
 * Creates an Indicator instance with default parameter values from the fetched
 * schema. The `key` getter mirrors the backend algorithm: filter parameters
 * where `plotParam === true`, join their values with `:`, prepend the indicator name.
 */
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
			const plotParamDefinitions = schema.parameters.filter((p) => p.plotParam);
			const plotValues = plotParamDefinitions.map((p) => parameters[p.name]).join(':');
			return `${indicatorName}:${plotValues}`;
		}
	};
}
