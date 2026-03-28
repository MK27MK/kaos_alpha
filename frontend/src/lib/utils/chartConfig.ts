import {
	CrosshairMode,
	LastPriceAnimationMode,
	type ChartOptions,
	type DeepPartial,
	type LineSeriesOptions
} from 'lightweight-charts';

export const chartOptions: DeepPartial<ChartOptions> = {
	height: 100,
	width: 100,
	autoSize: true, // NOTE FIXME this is the setting that causes layout problems when adding new panels
	// layout: {
	// 	background: { color: '#131722' },
	// 	textColor: '#d1d4dc'
	// },
	grid: {
		vertLines: { color: '#363c4e', visible: false },
		horzLines: { color: '#363c4e', visible: false }
	},
	crosshair: {
		mode: CrosshairMode.Normal
	},
	rightPriceScale: {
		borderColor: 'transparent'
	},
	timeScale: {
		borderColor: 'transparent',
		timeVisible: true,
		secondsVisible: false,
		rightBarStaysOnScroll: true, // mimicks the behaviour of tradingview's scrolling
		// Leaving this to true in backtest env causes forward fetching to be triggered
		// in a loop since the end of the range is always inside the viewport
		shiftVisibleRangeOnNewBar: true
	}
};

export const lineSeriesOptions: DeepPartial<LineSeriesOptions> = {
	lastValueVisible: false,
	priceLineVisible: false,
	lastPriceAnimation: LastPriceAnimationMode.OnDataUpdate
};

/** Shared options for all indicator series (SMA, BB bands, etc.) */
export const indicatorSeriesDefaults = {
	lastValueVisible: false,
	priceLineVisible: false
} as const;
