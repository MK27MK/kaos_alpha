import type { ComparisonOperator } from '$lib/models/indicator';
import type { ConditionNodeData, EntryNodeData, ExitNodeData } from '$lib/types/nodes';
import type { Edge, Node } from '@xyflow/svelte';

// ── Serialization types (what the backend receives) ──────────────────

export interface SerializedFeature {
	name: string;
	parameters: Record<string, number | string>;
}

export interface SerializedCondition {
	label: string;
	left: SerializedFeature;
	operator: ComparisonOperator;
	right: SerializedFeature;
}

export interface SerializedAction {
	type: 'entry' | 'exit';
	direction: 'buy' | 'sell';
}

export interface StrategyPayload {
	conditions: Record<string, SerializedCondition>;
	roots: string[];
	edges: Record<string, { true: string[]; false: string[] }>;
	actions: Record<string, SerializedAction>;
}

export interface ParseResult {
	valid: boolean;
	payload: StrategyPayload | null;
	errors: string[];
}

// ── Helpers ──────────────────────────────────────────────────────────

type Adjacency = Map<string, { true: string[]; false: string[] }>;

function buildAdjacency(edges: Edge[]): { adj: Adjacency; incomingCount: Map<string, number> } {
	const adj: Adjacency = new Map();
	const incomingCount = new Map<string, number>();

	for (const edge of edges) {
		if (!adj.has(edge.source)) {
			adj.set(edge.source, { true: [], false: [] });
		}
		const branch = edge.sourceHandle === 'true' ? 'true' : 'false';
		adj.get(edge.source)![branch].push(edge.target);

		incomingCount.set(edge.target, (incomingCount.get(edge.target) ?? 0) + 1);
	}

	return { adj, incomingCount };
}

/**
 * DFS that marks which nodes participate in at least one complete path
 * (root condition → ... → entry/exit leaf). Returns true if any complete
 * path was found in this subtree.
 */
function markReachable(
	nodeId: string,
	nodeMap: Map<string, Node>,
	adj: Adjacency,
	visited: Set<string>,
	participates: Set<string>
): boolean {
	if (visited.has(nodeId)) return participates.has(nodeId);
	visited.add(nodeId);

	const node = nodeMap.get(nodeId);
	if (!node) return false;

	if (node.type === 'entry' || node.type === 'exit') {
		participates.add(nodeId);
		return true;
	}

	if (node.type !== 'condition') return false;

	const children = adj.get(nodeId);
	let hasCompletePath = false;

	for (const branch of ['true', 'false'] as const) {
		const targets = children?.[branch] ?? [];
		for (const targetId of targets) {
			if (markReachable(targetId, nodeMap, adj, visited, participates)) {
				hasCompletePath = true;
			}
		}
	}

	if (hasCompletePath) {
		participates.add(nodeId);
	}

	return hasCompletePath;
}

// ── Main parser ──────────────────────────────────────────────────────

export function parseStrategy(nodes: Node[], edges: Edge[]): ParseResult {
	const errors: string[] = [];

	if (nodes.length === 0 || edges.length === 0) {
		return { valid: false, payload: null, errors: ['No nodes or edges'] };
	}

	const nodeMap = new Map(nodes.map((n) => [n.id, n]));
	const { adj, incomingCount } = buildAdjacency(edges);

	// Root condition nodes: condition nodes with no incoming edges
	const roots = nodes.filter((n) => n.type === 'condition' && (incomingCount.get(n.id) ?? 0) === 0);

	if (roots.length === 0) {
		errors.push(
			'No root condition node found (all condition nodes have incoming edges or none exist)'
		);
		return { valid: false, payload: null, errors };
	}

	// DFS from each root to find which nodes participate in complete paths
	const participates = new Set<string>();
	const visited = new Set<string>();

	for (const root of roots) {
		markReachable(root.id, nodeMap, adj, visited, participates);
	}

	// Only keep roots that actually lead somewhere
	const activeRoots = roots.filter((r) => participates.has(r.id));

	if (activeRoots.length === 0) {
		errors.push('No complete path from any root condition to an entry/exit node');
		return { valid: false, payload: null, errors };
	}

	// Build pruned payload — only nodes/edges in `participates`
	const conditions: Record<string, SerializedCondition> = {};
	const actions: Record<string, SerializedAction> = {};
	const prunedEdges: Record<string, { true: string[]; false: string[] }> = {};

	for (const nodeId of participates) {
		const node = nodeMap.get(nodeId)!;

		if (node.type === 'condition') {
			const nodeData = node.data as ConditionNodeData;
			conditions[nodeId] = {
				label: nodeData.label,
				left: { name: nodeData.leftIndicator.name, parameters: nodeData.leftIndicator.parameters },
				operator: nodeData.operator,
				right: {
					name: nodeData.rightIndicator.name,
					parameters: nodeData.rightIndicator.parameters
				}
			};

			// Pruned edges: only targets that participate
			const children = adj.get(nodeId);
			prunedEdges[nodeId] = {
				true: (children?.true ?? []).filter((t) => participates.has(t)),
				false: (children?.false ?? []).filter((t) => participates.has(t))
			};
		} else if (node.type === 'entry') {
			const nodeData = node.data as EntryNodeData;
			actions[nodeId] = { type: 'entry', direction: nodeData.direction };
		} else if (node.type === 'exit') {
			const nodeData = node.data as ExitNodeData;
			actions[nodeId] = { type: 'exit', direction: nodeData.direction };
		}
	}

	const payload: StrategyPayload = {
		conditions,
		roots: activeRoots.map((r) => r.id),
		edges: prunedEdges,
		actions
	};

	return { valid: true, payload, errors };
}
