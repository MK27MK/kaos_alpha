import type { Indicator } from '$lib/models/indicator';
import type { SyntheticInstrument } from '$lib/models/market-data.svelte';
import { getUniqueIndicatorsToPlot, syncIndicators } from '$lib/stores/active-indicators.svelte';
import { getDefaultNodeData, NODE_LIMIT } from '$lib/types/nodes';
import { API_BASE_URL } from '$lib/utils/env';
import { parseStrategy } from '$lib/utils/strategyParser';
import type { Edge, Node, NodeTypes } from '@xyflow/svelte';
import '@xyflow/svelte/dist/style.css';

export function useStrategyFlow(instrument: SyntheticInstrument) {
	// xyflow state - use state.raw to avoid performance issues due to recursive reactivity
	let nodes: Node[] = $state.raw([]);
	let edges: Edge[] = $state.raw([]);
	let nodeIdCounter = $state(0);

	let prevIndicators: Indicator[] = $state.raw([]);

	// Strategy validation - re-parsed on every node/edge change
	let lastParseResult = $derived(parseStrategy(nodes, edges));
	let backtestLoading = $state(false);

	// function revalidate() {
	// 	lastParseResult = parseStrategy(nodes, edges);
	// }

	function syncIndicatorsFromNodes(currentNodes: Node[]) {
		const next = getUniqueIndicatorsToPlot(currentNodes);
		syncIndicators(prevIndicators, next, addIndicator, removeIndicator);
		prevIndicators = next;
	}

	/**
	 * Add a new node of the specified type to the flow chart
	 */
	function handleAddNode(type: keyof NodeTypes, position: { x: number; y: number }): void {
		if (nodes.length >= NODE_LIMIT) {
			alert(
				`Are you trying to decipher Enigma? ${NODE_LIMIT} nodes are more than enough for this!`
			);
			return;
		}

		const nodeLabel = type.charAt(0).toUpperCase() + type.slice(1) + ` #${nodeIdCounter}`;
		const newNode: Node = {
			id: String(nodeIdCounter),
			type,
			position,
			data: getDefaultNodeData(type, nodeLabel)
		};

		nodeIdCounter++;
		nodes = [...nodes, newNode];
		syncIndicatorsFromNodes(nodes);
	}

	/**
	 * Add indicator via REST, then fetch its full history and load it into market data.
	 */
	async function addIndicator(indicator: Indicator): Promise<void> {
		// indicator already added
		if (indicator.key in instrument.indicators) return;
		try {
			const IndicatorKeyRes = await fetch(`${API_BASE_URL}/api/indicators`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ name: indicator.name, parameters: indicator.parameters })
			});
			if (!IndicatorKeyRes.ok) return;
			const { indicatorKey } = await IndicatorKeyRes.json();

			const historyRes = await fetch(`${API_BASE_URL}/api/indicators/${indicatorKey}/history`);
			if (!historyRes.ok) return;
			const history = await historyRes.json();

			instrument.setIndicatorHistory(indicatorKey, history);
		} catch {
			// Network error during rapid indicator changes — silently ignore
		}
	}

	/**
	 * Remove indicator via REST and clean up market data.
	 */
	async function removeIndicator(key: string): Promise<void> {
		try {
			await fetch(`${API_BASE_URL}/api/indicators/${key}`, { method: 'DELETE' });
		} catch {
			// Connection may be lost during rapid changes — clean up locally regardless
		}

		instrument.removeIndicatorKeys(key);
	}

	async function runBacktest(): Promise<Record<string, unknown> | null> {
		if (!lastParseResult.valid || !lastParseResult.payload) return null;

		backtestLoading = true;
		try {
			const res = await fetch(`${API_BASE_URL}/api/backtest`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(lastParseResult.payload)
			});
			if (!res.ok) return null;
			return await res.json();
		} catch {
			return null;
		} finally {
			backtestLoading = false;
		}
	}

	return {
		get nodes() {
			return nodes;
		},
		set nodes(newValue: Node[]) {
			nodes = newValue;
			// Sync indicators on xyflow-driven mutations (delete, data edits).
			// No-ops for position-only changes like dragging.
			// console.log("setter triggered")
			// TODO this gets triggered too many times (i.e. even if you drag a node around)
			// we want to sync indis on add, remove and condition node parameter change.
			syncIndicatorsFromNodes(newValue);
			// revalidate();
		},
		get edges() {
			return edges;
		},
		set edges(v: Edge[]) {
			edges = v;
			// revalidate();
		},
		get indicatorsToPlot() {
			return prevIndicators;
		},
		get isStrategyValid() {
			return lastParseResult.valid;
		},
		get backtestLoading() {
			return backtestLoading;
		},
		handleAddNode,
		runBacktest
	};
}
