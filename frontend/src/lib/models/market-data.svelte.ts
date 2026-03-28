import type { LineData } from 'lightweight-charts';
import type { Indicator, IndicatorValue, IndicatorValues } from './indicator';

export class SyntheticInstrument {
	prices = $state.raw<LineData[]>([]);
	indicators = $state.raw<Record<string, Indicator>>({});

	appendPrice(point: LineData) {
		this.prices = [...this.prices, point];
	}

	/** Bulk-load history for a given key (called after REST fetch). */
	setIndicatorHistory(indicatorKey: string, history: IndicatorValues) {
		// NOTE see note below
		// this.indicators[indicatorKey].history = history;
		const indicator = this.indicators[indicatorKey];
		this.indicators = {
			...this.indicators,
			[indicatorKey]: { ...indicator, history }
		};
	}

	appendIndicatorValue(indicatorKey: string, value: IndicatorValue) {
		const indicator = this.indicators[indicatorKey];
		const updatedHistory: IndicatorValues = { ...indicator.history };

		for (const [key, lineData] of Object.entries(value)) {
			updatedHistory[key] = [...(updatedHistory[key] ?? []), lineData];
		}

		this.indicators = {
			...this.indicators,
			[indicatorKey]: { ...indicator, history: updatedHistory }
		};
		// NOTE
		// this does not trigger reactivity with state.raw
		// this.indicators[indicatorKey].history = updatedHistory;
	}

	/** Remove an indicator by its plot key. */
	removeIndicatorKeys(key: string) {
		const cleaned = { ...this.indicators };
		delete cleaned[key];
		this.indicators = cleaned;
	}

	reset() {
		this.prices = [];
		this.indicators = {};
	}
}
