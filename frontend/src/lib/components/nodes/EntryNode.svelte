<script lang="ts">
	import type { Node, NodeProps } from '@xyflow/svelte';
	import { Handle, Position, useSvelteFlow } from '@xyflow/svelte';
	import type { EntryNodeData } from './nodes';

	type EntryNode = Node<EntryNodeData, 'entry'>;

	let { id, data }: NodeProps<EntryNode> = $props();

	const { updateNodeData } = useSvelteFlow();
</script>

<Handle type="target" position={Position.Top} />

<div>
	<span class="icon">&#9654;</span>
	<span>{data.label}</span>
</div>

<select
	class="nodrag"
	value={data.direction}
	onchange={(e) => updateNodeData(id, { direction: e.currentTarget.value })}
>
	<option value="buy">Buy (Long)</option>
	<option value="sell">Sell (Short)</option>
</select>

<style>
	:global(.svelte-flow__node-entry) {
		border-color: var(--color-entry);
	}

	.icon {
		color: var(--color-entry);
	}

	select {
		background: #f5f6f8;
		border: 1px solid #e2e4e9;
		border-radius: 4px;
		padding: 2px 4px;
		color: #1a1d24;
		font-size: 11px;
		margin-top: 6px;
		width: 100%;
	}

	select:hover {
		border-color: #c8cbd2;
	}
</style>
