<script lang="ts">
	import {
		CandlestickSeries,
		type CandlestickData,
		type CandlestickSeriesPartialOptions,
		type DeepPartial,
		type ISeriesApi,
		type SeriesOptions
	} from 'lightweight-charts';
	import { onMount, untrack, type Snippet } from 'svelte';
	import { setSeriesContext, useChart } from '../context.js';

	interface CandlestickSeriesProps extends Partial<CandlestickSeriesPartialOptions> {
		series?: ISeriesApi<'Candlestick'> | null;
		data: CandlestickData[];
		options?: DeepPartial<SeriesOptions<'Candlestick'>>;
		children?: Snippet;
	}
	// TODO consider using a serires state to extract common logic and effects between all the seires
	let { series = $bindable(null), data, children, options = {} }: CandlestickSeriesProps = $props();

	const chart = useChart();
	setSeriesContext(() => series);

	onMount(() => {
		if (!chart) return;

		series = chart.addSeries(CandlestickSeries, options);
		series.setData(data);

		return () => {
			if (series && chart) {
				chart.removeSeries(series);
				console.log('CandlestickSeries.onUnMount: series removed');
			}
		};
	});

	$effect(() => {
		// We track the array reference and length to trigger updates on mutations like push/unshift.
		// We use untrack() for setData because reading the entire array inside an effect
		// would create subscriptions for every single item, causing massive performance issues.

		// NOTE consider using $state.raw for the data to make it more efficient (no proxy for every obj)
		void data;
		void data.length;

		untrack(() => {
			if (!series) return;
			series.setData(data);
			$inspect(
				'CandlestickSeries: last few data points: ',
				data.slice(0, 4),
				`length ${data.length}`
			);
		});
	});

	$effect(() => {
		if (!series) return;
		series.applyOptions(options);
	});
</script>

<!-- {@debug} -->
{@render children?.()}
