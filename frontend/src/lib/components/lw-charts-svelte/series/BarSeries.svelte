<script lang="ts">
	import {
		BarSeries,
		type BarData,
		type BarSeriesPartialOptions,
		type ISeriesApi
	} from 'lightweight-charts';
	import { getChartContext } from '../context.js';

	interface BarSeriesProps extends Partial<BarSeriesPartialOptions> {
		data: BarData[];
	}

	let { data, ...seriesOptions }: BarSeriesProps = $props();

	const chart = getChartContext();
	let series = $state<ISeriesApi<'Bar'>>();

	$effect(() => {
		const barSeries = chart.addSeries(BarSeries, seriesOptions);
		series = barSeries;

		barSeries.setData(data);

		return () => {
			chart.removeSeries(barSeries);
		};
	});

	$effect(() => {
		if (!series) return;
		series.setData(data);
	});

	$effect(() => {
		if (!series) return;
		series.applyOptions(seriesOptions);
	});
</script>
