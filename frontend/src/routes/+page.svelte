<script lang="ts">
	import Chart from '$lib/components/lw-charts-svelte/Chart.svelte';
	import LineSeries from '$lib/components/lw-charts-svelte/series/LineSeries.svelte';
	import StrategyFlow from '$lib/components/nodes/StrategyFlow.svelte';
	import ReplayControls from '$lib/components/ReplayControls.svelte';
	import { setInstrumentContext } from '$lib/state/instrument-context.svelte';
	import { SyntheticInstrument } from '$lib/state/instrument.svelte';
	import { createPriceStream } from '$lib/state/price-stream.svelte';
	import { chartOptions, lineSeriesOptions } from '$lib/utils/chartConfig';
	import '@xyflow/svelte/dist/style.css';
	import { onMount } from 'svelte';

	const instrument = new SyntheticInstrument();
	setInstrumentContext(instrument);

	const stream = createPriceStream(instrument);
	onMount(() => {
		stream.connect();
		return () => stream.disconnect();
	});
</script>

<div class="topbar">KAOS ALPHA</div>
<div class="layout">
	<div class="chart-container">
		<ReplayControls {stream} />
		<div class="chart">
			<Chart options={chartOptions}>
				<LineSeries data={instrument.prices} options={lineSeriesOptions}></LineSeries>
				{#each Object.entries(instrument.indicators) as [key, indi] (key)}
					{#each Object.values(indi.history ?? {}) as lineData}
						<LineSeries data={lineData} color="#facc15" lineWidth={2} />
					{/each}
				{/each}
			</Chart>
		</div>
	</div>
	<StrategyFlow />
	<!-- {#if backtest.hasResults}
		<div class="backtest-summary">
			<span>Trades: {backtest.summary?.total_trades}</span>
			<span>Win rate: {((backtest.summary?.win_rate ?? 0) * 100).toFixed(1)}%</span>
			<span>PnL: {backtest.summary?.total_pnl.toFixed(2)}</span>
			<span>Max DD: {backtest.summary?.max_drawdown.toFixed(2)}</span>
		</div>
	{/if} -->
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
