import type { CandlestickData, Time } from 'lightweight-charts';

export function generateMockCandles(
	count: number = 100,
	startPrice: number = 100,
	startTime: number = Math.floor(Date.now() / 1000) - count * 60
): CandlestickData[] {
	const candles: CandlestickData[] = [];
	let currentPrice = startPrice;
	let currentTime = startTime;

	for (let i = 0; i < count; i++) {
		const open = currentPrice;

		// Random price movement with slight trending bias
		const trend = Math.sin(i / 50) * 0.2; // Gentle wave pattern
		const randomMove = (Math.random() - 0.5) * 2; // -1 to +1
		const priceChange = (trend + randomMove) * (startPrice * 0.01); // 1% max move

		currentPrice += priceChange;

		// Generate realistic OHLC
		const isGreen = Math.random() > 0.5;
		const close = isGreen
			? currentPrice + Math.random() * (startPrice * 0.005)
			: currentPrice - Math.random() * (startPrice * 0.005);

		const high = Math.max(open, close) + Math.random() * (startPrice * 0.003);
		const low = Math.min(open, close) - Math.random() * (startPrice * 0.003);

		candles.push({
			time: currentTime as Time,
			open: Number(open.toFixed(2)),
			high: Number(high.toFixed(2)),
			low: Number(low.toFixed(2)),
			close: Number(close.toFixed(2)),
		});

		currentTime += 60; // 1 minute intervals
	}

	return candles;
}

// Simulate network delay for realistic testing
export function mockDelay(ms: number = 50): Promise<void> {
	return new Promise((resolve) => setTimeout(resolve, ms));
}
