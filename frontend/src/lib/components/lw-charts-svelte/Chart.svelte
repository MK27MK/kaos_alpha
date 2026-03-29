<script lang="ts">
	import {
		createChart,
		type ChartOptions,
		type DeepPartial,
		type IChartApi
	} from 'lightweight-charts';
	import { onMount, type Snippet } from 'svelte';
	import { setChartContext } from './context.js';

	const defaultChartOptions: DeepPartial<ChartOptions> = {};

	interface Props {
		chart?: IChartApi | null;
		container?: HTMLDivElement | null;
		options?: DeepPartial<ChartOptions>;
		children?: Snippet;
	}

	let {
		chart = $bindable(null),
		container = $bindable(null),
		options = {},
		children
	}: Props = $props();

	// You wrap it inside a closure to preserve reactivity
	setChartContext(() => chart);

	onMount(() => {
		console.log('Chart.onMount: chart is about to be added');
		if (!container) return;

		chart = createChart(container, {
			...defaultChartOptions,
			...options
		});

		return () => {
			chart?.remove();
			console.log('Chart.onUnMount: chart removed');
		};
	});

	// Update chart options when they change
	$effect(() => {
		if (!chart || !options) return;

		chart.applyOptions(options);
	});
</script>

<div bind:this={container}>
	{#if chart}
		{@render children?.()}
	{/if}
</div>

<style>
	div {
		/* Makes absoulte positioning of the chart legend work */
		position: relative;
		width: 100%;
		height: 100%;
	}
</style>
