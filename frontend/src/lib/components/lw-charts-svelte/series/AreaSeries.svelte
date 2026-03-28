<script lang="ts">
	import {
		AreaSeries,
		type AreaData,
		type AreaSeriesPartialOptions,
		type ISeriesApi
	} from 'lightweight-charts';
	import { getChartContext } from '../context.js';

	interface AreaSeriesProps extends Partial<AreaSeriesPartialOptions> {
		data: AreaData[];
	}

	let { data, ...seriesOptions }: AreaSeriesProps = $props();

	const chart = getChartContext();
	let series = $state<ISeriesApi<'Area'>>();

	$effect(() => {
		const areaSeries = chart.addSeries(AreaSeries, seriesOptions);
		series = areaSeries;

		areaSeries.setData(data);

		return () => {
			chart.removeSeries(areaSeries);
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
