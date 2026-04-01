<script lang="ts">
	import type { Node, NodeProps } from '@xyflow/svelte';
	import { Handle, Position, useSvelteFlow } from '@xyflow/svelte';
	import type { ExitNodeData } from './nodes';

	type ExitNode = Node<ExitNodeData, 'exit'>;

	let { id, data }: NodeProps<ExitNode> = $props();

	const { updateNodeData } = useSvelteFlow();
</script>

<Handle type="target" position={Position.Top} />

<div class="node-header">
	<span class="icon">&#9724;</span>
	<span>{data.label}</span>
</div>

<select
	class="nodrag"
	value={data.direction}
	onchange={(e) => updateNodeData(id, { direction: e.currentTarget.value })}
>
	<option value="buy">Buy (Close Long)</option>
	<option value="sell">Sell (Close Short)</option>
</select>

<style>
	:global(.svelte-flow__node-exit) {
		border-color: var(--color-exit);
	}

	.node-header {
		display: flex;
		gap: 6px;
		align-items: center;
		margin-bottom: 6px;
	}

	.icon {
		color: var(--color-exit);
	}

	select {
		background: #f5f6f8;
		border: 1px solid #e2e4e9;
		border-radius: 4px;
		padding: 2px 4px;
		color: #1a1d24;
		font-size: 11px;
		width: 100%;
	}

	select:hover {
		border-color: #c8cbd2;
	}
</style>
