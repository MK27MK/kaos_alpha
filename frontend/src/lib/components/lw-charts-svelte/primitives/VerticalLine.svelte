<script lang="ts">
	import type { Time } from 'lightweight-charts';
	import { useChart, useSeries } from '../context.ts';
	import type { VertLineOptions } from './utils.ts';
	import { VertLine } from './vertical-line.ts';

	interface Props {
		x: Time;
		options?: Partial<VertLineOptions>;
	}

	let { x, options }: Props = $props();

	const chart = useChart();
	const series = useSeries();

	$effect(() => {
		// checking is chart is null is not necessary since series is !== null only if chart !== null as well
		if (!chart || !series || !x) return;

		const vertLine = new VertLine(chart, series, x, options);
		series.attachPrimitive(vertLine);

		return () => {
			series?.detachPrimitive(vertLine);
		};
	});
</script>
