<script lang="ts">
	import AddNodeMenu from '$lib/components/AddNodeMenu.svelte';
	import Chart from '$lib/components/lw-charts-svelte/Chart.svelte';
	import LineSeries from '$lib/components/lw-charts-svelte/series/LineSeries.svelte';
	import ContextMenu from '$lib/components/nodes/ContextMenu.svelte';
	import { nodeTypes } from '$lib/components/nodes/nodeTypes';
	import { useContextMenu } from '$lib/components/nodes/useContextMenu.svelte';
	import ReplayControls from '$lib/components/ReplayControls.svelte';
	import { BacktestResult, type BacktestResponse } from '$lib/models/backtest-result.svelte';
	import { loadIndicatorSchemas } from '$lib/models/indicator';
	import { SyntheticInstrument } from '$lib/models/market-data.svelte';
	import { createPriceStream } from '$lib/stores/price-stream.svelte';
	import { useStrategyFlow } from '$lib/stores/strategy-flow.svelte';
	import { chartOptions, lineSeriesOptions } from '$lib/utils/chartConfig';
	import { Background, Controls, Panel, SvelteFlow } from '@xyflow/svelte';
	import '@xyflow/svelte/dist/style.css';
	import { onMount } from 'svelte';

	const instrument = new SyntheticInstrument();
	const stream = createPriceStream(instrument);
	onMount(() => {
		// Schemas must be loaded before the UI renders indicator controls
		loadIndicatorSchemas().then(() => stream.connect());
		return () => stream.disconnect();
	});

	const strategyFlow = useStrategyFlow(instrument);
	const contextMenu = useContextMenu();
	const backtest = new BacktestResult();

	async function handleTest() {
		const result = await strategyFlow.runBacktest();
		console.log(result);
		if (result) {
			backtest.load(result as BacktestResponse);
			console.log(backtest.hasResults);
		}
	}
</script>

<div class="topbar">KAOS ALPHA</div>
<div class="layout">
	<div class="chart-container">
		<ReplayControls {stream} />
		<div class="chart">
			<Chart options={chartOptions}>
				<LineSeries data={instrument.prices} options={lineSeriesOptions}></LineSeries>
				{#each strategyFlow.indicatorsToPlot as indi (indi.key)}
					{#each Object.values(instrument.indicators[indi.key]?.history ?? {}) as lineData}
						<LineSeries data={lineData} color="#facc15" lineWidth={2} />
					{/each}
				{/each}
			</Chart>
		</div>
	</div>
	<div class="flow" bind:this={contextMenu.flowDiv}>
		<SvelteFlow
			bind:nodes={strategyFlow.nodes}
			bind:edges={strategyFlow.edges}
			{nodeTypes}
			onnodecontextmenu={contextMenu.handleContextMenu}
			onpaneclick={contextMenu.handlePaneClick}
			onpointerdown={contextMenu.handlePaneClick}
			fitView
		>
			<Background />
			<Controls />
			<!-- <MiniMap /> -->
			<Panel position="bottom-right">
				<AddNodeMenu onAddNode={strategyFlow.handleAddNode} />
			</Panel>
			<Panel position="top-right">
				<!-- "Test" button is clickable only if the graph is logically valid -->
				<button
					class="test-btn"
					disabled={!strategyFlow.isStrategyValid || strategyFlow.backtestLoading}
					onclick={handleTest}
				>
					{strategyFlow.backtestLoading ? 'Testing...' : 'Test'}
				</button>
			</Panel>
			{#if contextMenu.id}
				<ContextMenu {contextMenu} />
			{/if}
		</SvelteFlow>
	</div>
	{#if backtest.hasResults}
		<div class="backtest-summary">
			<span>Trades: {backtest.summary?.total_trades}</span>
			<span>Win rate: {((backtest.summary?.win_rate ?? 0) * 100).toFixed(1)}%</span>
			<span>PnL: {backtest.summary?.total_pnl.toFixed(2)}</span>
			<span>Max DD: {backtest.summary?.max_drawdown.toFixed(2)}</span>
		</div>
	{/if}
</div>

<style>
	.topbar {
		height: 40px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 0.9rem;
		font-weight: 700;
		letter-spacing: 0.25em;
		color: var(--color-text-muted);
		background: var(--color-surface);
		border-bottom: 1px solid var(--color-border);
		user-select: none;
	}

	.layout {
		display: flex;
		height: calc(100vh - 40px);
	}

	.chart-container {
		width: 50vw;
		display: flex;
		flex-direction: column;
		border-right: 1px solid var(--color-border);
	}

	.chart {
		flex: 1;
	}

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

	.backtest-summary {
		position: absolute;
		top: 50%;
		left: 50%;
		translate: -50% -50%;
		display: flex;
		gap: 24px;
		padding: 8px 16px;
		font-size: 0.8rem;
		color: var(--color-text-muted);
		z-index: 10;
		background: red;
		/* background: var(--color-surface); */
		border-top: 1px solid var(--color-border);
	}
</style>
