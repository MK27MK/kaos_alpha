<script lang="ts">
	import AddNodeMenu from '$lib/components/AddNodeMenu.svelte';
	import ContextMenu from '$lib/components/nodes/ContextMenu.svelte';
	import { nodeTypes } from '$lib/components/nodes/nodes';
	import { useContextMenu } from '$lib/components/nodes/useContextMenu.svelte';
	import { getInstrumentContext } from '$lib/state/instrument-context.svelte';
	import { setStrategyFlowContext } from '$lib/state/strategy-flow-context';
	import { useStrategyFlow } from '$lib/state/strategy-flow.svelte';
	import { Background, Controls, Panel, SvelteFlow } from '@xyflow/svelte';
	import '@xyflow/svelte/dist/style.css';

	const instrument = getInstrumentContext();
	const strategyFlow = useStrategyFlow(instrument);

	setStrategyFlowContext(strategyFlow);

	const contextMenu = useContextMenu();
	// const backtest = new BacktestResult();

	// async function handleTest() {
	// 	const result = await strategyFlow.runBacktest();
	// 	console.log(result);
	// 	if (result) {
	// 		backtest.load(result as BacktestResponse);
	// 		console.log(backtest.hasResults);
	// 	}
	// }
</script>

<div class="flow" bind:this={contextMenu.flowDiv}>
	<SvelteFlow
		bind:nodes={strategyFlow.nodes}
		bind:edges={strategyFlow.edges}
		{nodeTypes}
		onnodecontextmenu={contextMenu.handleContextMenu}
		onpaneclick={contextMenu.handlePaneClick}
		onpointerdown={contextMenu.handlePaneClick}
		ondelete={() => strategyFlow.syncIndicators()}
		fitView
	>
		<Background />
		<Controls />
		<!-- <MiniMap /> -->
		<Panel position="bottom-right">
			<AddNodeMenu onaddnode={strategyFlow.onaddnode} />
		</Panel>
		<!-- <Panel position="top-right"> -->
		<!-- "Test" button is clickable only if the graph is logically valid -->
		<!-- <button
				class="test-btn"
				disabled={!strategyFlow.isStrategyValid || strategyFlow.backtestLoading}
				onclick={handleTest}
			>
				{strategyFlow.backtestLoading ? 'Testing...' : 'Test'}
			</button>
		</Panel> -->
		{#if contextMenu.id}
			<ContextMenu {contextMenu} />
		{/if}
	</SvelteFlow>
</div>

<style>
	.flow {
		width: 50vw;
		background: var(--color-bg);
	}

	.test-btn {
		padding: 6px 16px;
		font-size: 0.85rem;
		font-weight: 600;
		border: 1px solid var(--color-border);
		border-radius: 4px;
		background: var(--color-surface);
		color: var(--color-text-muted);
		cursor: pointer;
	}

	.test-btn:disabled {
		opacity: 0.4;
		cursor: not-allowed;
	}
</style>
