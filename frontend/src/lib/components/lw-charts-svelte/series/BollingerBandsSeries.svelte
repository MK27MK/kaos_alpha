<script lang="ts">
	import { LineSeries, LineStyle, type ISeriesApi } from 'lightweight-charts';
	import { onMount, untrack } from 'svelte';
	import { useChart } from '../context.js';
	import type { PricePoint } from '$lib/models/market-data.svelte';
	import { indicatorSeriesDefaults } from '$lib/utils/chartConfig';

	interface BollingerBandsSeriesProps {
		data: PricePoint[][];
	}

	let { data }: BollingerBandsSeriesProps = $props();

	const chart = useChart();

	const upperData = $derived(data[0] ?? []);
	const middleData = $derived(data[1] ?? []);
	const lowerData = $derived(data[2] ?? []);

	let upperSeries: ISeriesApi<'Line'> | null = null;
	let middleSeries: ISeriesApi<'Line'> | null = null;
	let lowerSeries: ISeriesApi<'Line'> | null = null;

	onMount(() => {
		if (!chart) return;

		upperSeries = chart.addSeries(LineSeries, {
			color: '#c084fc',
			lineWidth: 1,
			...indicatorSeriesDefaults
		});

		middleSeries = chart.addSeries(LineSeries, {
			color: '#c084fc',
			lineWidth: 1,
			lineStyle: LineStyle.Dashed,
			...indicatorSeriesDefaults
		});

		lowerSeries = chart.addSeries(LineSeries, {
			color: '#c084fc',
			lineWidth: 1,
			...indicatorSeriesDefaults
		});

		upperSeries.setData(upperData);
		middleSeries.setData(middleData);
		lowerSeries.setData(lowerData);

		return () => {
			if (chart) {
				if (upperSeries) chart.removeSeries(upperSeries);
				if (middleSeries) chart.removeSeries(middleSeries);
				if (lowerSeries) chart.removeSeries(lowerSeries);
			}
		};
	});

	$effect(() => {
		void upperData;
		void upperData.length;
		untrack(() => {
			if (!upperSeries) return;
			upperSeries.setData(upperData);
		});
	});

	$effect(() => {
		void middleData;
		void middleData.length;
		untrack(() => {
			if (!middleSeries) return;
			middleSeries.setData(middleData);
		});
	});

	$effect(() => {
		void lowerData;
		void lowerData.length;
		untrack(() => {
			if (!lowerSeries) return;
			lowerSeries.setData(lowerData);
		});
	});
</script>
