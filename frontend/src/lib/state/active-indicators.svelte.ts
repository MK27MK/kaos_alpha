import type { ConditionNodeData } from '$lib/components/nodes/nodes';
import type { Indicator } from '$lib/models/indicator';
import type { Node } from '@xyflow/svelte';
import { SvelteMap } from 'svelte/reactivity';

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

	const seen = new SvelteMap<string, Indicator>();
	for (const indicator of allIndicators) {
		if (!seen.has(indicator.key)) seen.set(indicator.key, indicator);
	}
	return [...seen.values()];
}
