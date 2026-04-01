import { getDefaultNodeData, NODE_LIMIT } from '$lib/components/nodes/nodes';
import { getUniqueIndicatorsToPlot } from '$lib/state/active-indicators.svelte';
import type { SyntheticInstrument } from '$lib/state/instrument.svelte';
import type { Edge, Node, NodeTypes } from '@xyflow/svelte';
import '@xyflow/svelte/dist/style.css';

export function useStrategyFlow(instrument: SyntheticInstrument) {
	// xyflow state - use state.raw to avoid performance issues due to recursive reactivity
	let nodes: Node[] = $state.raw([]);
	let edges: Edge[] = $state.raw([]);
	let nodeIdCounter = $state(0);

	/**
	 * Tell the instrument which indicators the current node graph needs.
	 * Idempotent — safe to call on every indicator-relevant mutation.
	 */
	function syncIndicators() {
		instrument.syncIndicators(getUniqueIndicatorsToPlot(nodes));
	}

	/**
	 * Add a new node of the specified type to the flow chart
	 */
	function onaddnode(nodeType: keyof NodeTypes, position: { x: number; y: number }): void {
		if (nodes.length >= NODE_LIMIT) {
			alert(
				`Are you trying to decipher Enigma? ${NODE_LIMIT} nodes are more than enough for this!`
			);
			return;
		}

		const nodeLabel = nodeType.charAt(0).toUpperCase() + nodeType.slice(1) + ` #${nodeIdCounter}`;
		const newNode: Node = {
			id: String(nodeIdCounter),
			type: nodeType,
			position,
			data: getDefaultNodeData(nodeType, nodeLabel)
		};

		nodeIdCounter++;
		nodes = [...nodes, newNode];
		syncIndicators();
	}

	return {
		get nodes() {
			return nodes;
		},
		set nodes(newValue: Node[]) {
			nodes = newValue;
		},
		get edges() {
			return edges;
		},
		set edges(v: Edge[]) {
			edges = v;
		},
		onaddnode,
		// needed by IndicatorInput, shared via context
		syncIndicators
	};
}
