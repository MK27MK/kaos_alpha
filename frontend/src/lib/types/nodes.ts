import { createIndicator, type ComparisonOperator, type Indicator } from '$lib/models/indicator';

// ── Node data interfaces ────────────────────────────────────────────

export interface ConditionNodeData {
	label: string;
	leftIndicator: Indicator;
	operator: ComparisonOperator;
	rightIndicator: Indicator;
}

export interface EntryNodeData {
	label: string;
	direction: 'buy' | 'sell';
}

export interface ExitNodeData {
	label: string;
	direction: 'buy' | 'sell';
}

export const NODE_LIMIT = 50;

export function getDefaultNodeData(type: string, label: string): Record<string, unknown> {
	switch (type) {
		case 'condition':
			return {
				label,
				leftIndicator: createIndicator('price'),
				operator: '>',
				rightIndicator: createIndicator('sma')
			};
		case 'entry':
			return { label, direction: 'buy' };
		case 'exit':
			return { label, direction: 'buy' };
		default:
			return { label };
	}
}
