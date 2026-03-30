<script lang="ts">
	import type { ConditionNodeData } from '$lib/types/nodes';
	import type { Node, NodeProps } from '@xyflow/svelte';
	import { Handle, Position, useSvelteFlow } from '@xyflow/svelte';
	import IndicatorInput from './IndicatorInput.svelte';

	type ConditionNode = Node<ConditionNodeData, 'condition'>;

	let { id, data }: NodeProps<ConditionNode> = $props();

	const { updateNodeData } = useSvelteFlow();

	const operators = ['<', '>', '=', '<=', '>=', '!='];
</script>

<Handle type="target" position={Position.Top} />

<div class="node-header">
	<span class="icon">&#9670;</span>
	<span>{data.label}</span>
</div>

<div class="selects-row">
	<IndicatorInput {id} {data} side="leftIndicator" />
	<!-- Operator -->
	<select
		class="nodrag"
		value={data.operator}
		onchange={(e) => updateNodeData(id, { operator: e.currentTarget.value })}
	>
		{#each operators as op (op)}
			<option value={op}>{op}</option>
		{/each}
	</select>
	<IndicatorInput {id} {data} side="rightIndicator" />
</div>

<Handle type="source" position={Position.Right} id="true" />
<Handle type="source" position={Position.Left} id="false" />

<style>
	:global(.svelte-flow__node-condition) {
		--xy-node-color: var(--color-condition);
		border-color: var(--color-condition);
		background-color: color-mix(in srgb, var(--xy-node-color) 20%, transparent);
	}

	/* highlight the border of the node while hovering */
	:global(.svelte-flow__node-condition.selectable:hover),
	:global(.svelte-flow__node-condition.draggable:hover) {
		border-color: var(--color-condition-hover);
		box-shadow: var(--xy-node-boxshadow-hover);
	}

	/* highlight and make the border thicker if clicked */
	:global(.svelte-flow__node-condition.selectable.selected) {
		border-color: var(--color-condition-hover);
		border-width: 2px;
		box-shadow: var(--xy-node-boxshadow-selected);
	}

	/* internal components of the node */
	.icon {
		color: var(--xy-node-color);
	}
	.node-header {
		display: flex;
		flex-direction: row;
		gap: 6px;
		align-items: center;
		/* without this the left side of the icon touches the border of the node */
		margin-left: 6px;
		margin-bottom: 6px;
	}
	.selects-row {
		display: flex;
		gap: 4px;
		align-items: center;
	}

	select {
		/* appearance provato ma non funziona */
		/* appearance: none; */
		background: var(--color-condition-transparent);
		border: 1px solid #e2e4e9;
		border-radius: 10px;
		padding: 2px 4px;
		color: #1a1d24;
		font-size: 11px;
	}

	select:hover {
		border-color: #c8cbd2;
	}
</style>
