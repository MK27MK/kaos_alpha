import { createIndicator, type Indicator } from '$lib/models/indicator';
import type { NodeTypes } from '@xyflow/svelte';
import ConditionNode from './ConditionNode/ConditionNode.svelte';
import EntryNode from './EntryNode.svelte';
import ExitNode from './ExitNode.svelte';

export const NODE_LIMIT = 50;

export const nodeTypes: NodeTypes = {
	condition: ConditionNode,
	entry: EntryNode,
	exit: ExitNode
};

// ============================================================================
// NodeData interfaces
// ============================================================================

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
export type ComparisonOperator = '<' | '>' | '=' | '<=' | '>=' | '!=';
