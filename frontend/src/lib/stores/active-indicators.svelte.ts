import type { Indicator } from '$lib/models/indicator';
import type { ConditionNodeData } from '$lib/types/nodes';
import type { Node } from '@xyflow/svelte';

function isConditionNode(
	node: Node | (Node & { data: ConditionNodeData })
): node is Node & { data: ConditionNodeData } {
	return node.type === 'condition';
}

/**
 * Derive a deduplicated list of indicators that need plotting.
 * Indicators with the same key (e.g. bb upper vs lower with same
 * length/std_dev) collapse into a single entry.
 */
export function getUniqueIndicatorsToPlot(nodes: Node[]): Indicator[] {
	const allIndicators = nodes
		.filter(isConditionNode)
		.flatMap((n) => [n.data.leftIndicator, n.data.rightIndicator]);

	const seen = new Map<string, Indicator>();
	for (const indicator of allIndicators) {
		if (!seen.has(indicator.key)) seen.set(indicator.key, indicator);
	}
	return [...seen.values()];
}

/**
 * Diff old and new indicator lists, calling addIndicator/removeIndicator as needed.
 */
export function syncIndicators(
	prev: Indicator[],
	next: Indicator[],
	addIndicator: (indicator: Indicator) => Promise<void>,
	removeIndicator: (key: string) => Promise<void>
): void {
	const prevKeys = new Set(prev.map((f) => f.key));
	const nextKeys = new Set(next.map((f) => f.key));

	for (const indicator of prev) {
		if (!nextKeys.has(indicator.key)) {
			void removeIndicator(indicator.key);
		}
	}

	for (const indicator of next) {
		if (!prevKeys.has(indicator.key)) {
			void addIndicator(indicator);
		}
	}
}
