<script lang="ts">
	import {
		LineSeries,
		type DeepPartial,
		type ISeriesApi,
		type LineData,
		type LineSeriesPartialOptions,
		type SeriesOptions
	} from 'lightweight-charts';
	import { onMount, untrack, type Snippet } from 'svelte';
	import { setSeriesContext, useChart } from '../context.js';

	interface LineSeriesProps extends Partial<LineSeriesPartialOptions> {
		series?: ISeriesApi<'Line'> | null;
		data: LineData[];
		options?: DeepPartial<SeriesOptions<'Line'>>;
		children?: Snippet;
	}

	let { series = $bindable(null), data, children, options = {} }: LineSeriesProps = $props();

	const chart = useChart();
	setSeriesContext(() => series);

	onMount(() => {
		if (!chart) return;

		series = chart.addSeries(LineSeries, options);
		series.setData(data);

		return () => {
			if (series && chart) {
				chart.removeSeries(series);
				console.log('LineSeries.onUnMount: series removed');
			}
		};
	});

	$effect(() => {
		void data;
		void data.length;

		untrack(() => {
			if (!series) return;
			series.setData(data);
		});
	});

	$effect(() => {
		if (!series) return;
		series.applyOptions(options);
	});
</script>

{@render children?.()}
