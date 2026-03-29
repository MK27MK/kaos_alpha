<script lang="ts">
	import type {
		DeepPartial,
		IRange,
		ITimeScaleApi,
		LogicalRangeChangeEventHandler,
		SizeChangeEventHandler,
		Time,
		TimeRangeChangeEventHandler,
		TimeScaleOptions as TimeScaleNativeOptions
	} from 'lightweight-charts';
	import type { Snippet } from 'svelte';
	import { getChartContext } from './context.js';

	type TimeScaleOptions = DeepPartial<TimeScaleNativeOptions>;

	interface TimeScaleProps {
		/** Options for the time scale */
		options?: TimeScaleOptions;
		/** The visible time range for the time scale */
		visibleRange?: IRange<Time>;
		/** The visible logical range for the time scale */
		visibleLogicalRange?: IRange<number>;
		/** Callback for when the visible time range changes */
		onVisibleTimeRangeChange?: TimeRangeChangeEventHandler<Time>;
		/** Callback for when the visible logical range changes */
		onVisibleLogicalRangeChange?: LogicalRangeChangeEventHandler;
		/** Callback for when the size of the time scale changes */
		onSizeChange?: SizeChangeEventHandler;
		/** Children snippet */
		children?: Snippet;
	}

	let {
		options = {},
		visibleRange,
		visibleLogicalRange,
		onVisibleTimeRangeChange,
		onVisibleLogicalRangeChange,
		onSizeChange,
		children
	}: TimeScaleProps = $props();

	const chart = getChartContext()();

	// Internal state for time scale API
	let timeScale = $state<ITimeScaleApi<Time> | null>(null);

	// Initialize time scale API when api.chart is available
	$effect(() => {
		if (!chart) return;

		timeScale = chart.timeScale();

		return () => {
			timeScale = null;
		};
	});

	// Apply options when they change
	$effect(() => {
		if (!timeScale) return;

		timeScale.applyOptions(options);
	});

	// Subscribe to visible time range changes
	$effect(() => {
		if (!timeScale || !onVisibleTimeRangeChange) return;

		timeScale.subscribeVisibleTimeRangeChange(onVisibleTimeRangeChange);

		return () => {
			timeScale?.unsubscribeVisibleTimeRangeChange(onVisibleTimeRangeChange);
		};
	});

	// Subscribe to visible logical range changes
	$effect(() => {
		if (!timeScale || !onVisibleLogicalRangeChange) return;

		timeScale.subscribeVisibleLogicalRangeChange(onVisibleLogicalRangeChange);
		console.log('TimeScale.effect: subscribed to VisibleLogicalRangeChange.');

		return () => {
			timeScale?.unsubscribeVisibleLogicalRangeChange(onVisibleLogicalRangeChange);
			console.log('TimeScale.effect: unsubscribed to VisibleLogicalRangeChange.');
		};
	});

	// Subscribe to size changes
	$effect(() => {
		if (!timeScale || !onSizeChange) return;

		timeScale.subscribeSizeChange(onSizeChange);

		return () => {
			timeScale?.unsubscribeSizeChange(onSizeChange);
		};
	});

	// Set visible time range
	$effect(() => {
		if (!timeScale || !visibleRange) return;

		timeScale.setVisibleRange(visibleRange);
	});

	// Set visible logical range
	$effect(() => {
		if (!timeScale || !visibleLogicalRange) return;

		timeScale.setVisibleLogicalRange(visibleLogicalRange);
	});
</script>

{#if children}
	{@render children()}
{/if}
