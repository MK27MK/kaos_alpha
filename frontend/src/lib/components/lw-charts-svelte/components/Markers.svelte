<script lang="ts">
	import { createSeriesMarkers, type SeriesMarker, type Time } from 'lightweight-charts';
	import { useSeries } from '../context.js';

	interface Props {
		markers: SeriesMarker<Time>[];
	}

	let { markers }: Props = $props();

	const series = useSeries();

	$effect(() => {
		if (!series) return;
		const seriesMarkers = createSeriesMarkers(series, markers);

		return () => {
			seriesMarkers.detach();
		};
	});
</script>
