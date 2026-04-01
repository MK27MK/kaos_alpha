<script lang="ts">
	import { createIndicator, getIndicatorSchema, getIndicatorSchemas } from '$lib/models/indicator';
	import type { Node, NodeProps } from '@xyflow/svelte';
	import { useSvelteFlow } from '@xyflow/svelte';
	import type { ConditionNodeData } from '../nodes';
	import { getStrategyFlowContext } from '$lib/state/strategy-flow-context';

	type ConditionNode = Node<ConditionNodeData, 'condition'>;

	let { id, nodeData, side }: NodeProps<ConditionNode> & { side: 'leftIndicator' | 'rightIndicator' } =
		$props();

	const { updateNodeData } = useSvelteFlow();
	const strategyFlow = getStrategyFlowContext();

	/**
	 * If the indicator is changed altogether, then update nodeData with a
	 * completely new one.
	*/
	function handleIndicatorChange(name: string) {
		updateNodeData(id, { [side]: createIndicator(name) });
		strategyFlow.syncIndicators();
	}

	function handleChangeIndicatorParams(paramKey: string, value: number | string) {
		const current = nodeData[side];
		updateNodeData(id, {
			[side]: { ...current, parameters: { ...current.parameters, [paramKey]: value } }
		});
		strategyFlow.syncIndicators();
	}
</script>

<div class="value-input">
	<select
		class="nodrag"
		value={nodeData[side].name}
		onchange={(e) => handleIndicatorChange(e.currentTarget.value)}
	>
		{#each getIndicatorSchemas() as schema (schema.name)}
			<option value={schema.name}>{schema.displayName}</option>
		{/each}
	</select>
	{#each getIndicatorSchema(nodeData[side].name).parameters as param (param.name)}
		<!-- render a SELECT tag for parameters like 'band' of bollinger band, which can be either 'upper' or 'lower' -->
		{#if param.htmlTag === 'select' && param.options}
			<select
				class="nodrag"
				value={nodeData[side].parameters[param.name]}
				onchange={(e) => handleChangeIndicatorParams(param.name, e.currentTarget.value)}
			>
				{#each param.options as opt (opt.name)}
					<option value={opt.name}>{opt.displayName}</option>
				{/each}
			</select>
			<!-- render an INPUT tag for numerical parameters like length -->
		{:else if param.htmlTag === 'input'}
			<input
				type="number"
				class="nodrag param-input"
				value={nodeData[side].parameters[param.name]}
				min={param.min}
				max={param.max}
				onchange={(e) => handleChangeIndicatorParams(param.name, Number(e.currentTarget.value))}
			/>
		{/if}
	{/each}
</div>

<style>
	.value-input {
		display: flex;
		gap: 2px;
		align-items: center;
	}
	select,
	input {
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

	.param-input {
		width: 40px;
		text-align: center;
	}
</style>
