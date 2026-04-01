import { API_BASE_URL } from '$lib/utils/env';
import type { LineData } from 'lightweight-charts';
import type { Indicator, IndicatorValue, IndicatorValues } from '../models/indicator';
import { SvelteSet } from 'svelte/reactivity';

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

	/**
	 * Idempotent sync: diffs `desired` against current indicators,
	 * adding new ones via REST and removing stale ones.
	 * Safe to call repeatedly with the same set (no-op).
	 */
	syncIndicators(desired: Indicator[]): void {
		const desiredKeys = new SvelteSet(desired.map((i) => i.key));
		const currentKeys = new SvelteSet(Object.keys(this.indicators));

		for (const key of currentKeys) {
			if (!desiredKeys.has(key)) void this.removeIndicator(key);
		}
		for (const indicator of desired) {
			if (!currentKeys.has(indicator.key)) void this.addIndicator(indicator);
		}
	}

	/** POST indicator to backend, fetch its full history, and load into state. */
	private async addIndicator(indicator: Indicator): Promise<void> {
		if (indicator.key in this.indicators) return;
		try {
			const createResponse = await fetch(`${API_BASE_URL}/api/indicators`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ name: indicator.name, parameters: indicator.parameters })
			});
			if (!createResponse.ok) return;
			const { indicatorKey } = await createResponse.json();

			const historyResponse = await fetch(`${API_BASE_URL}/api/indicators/${indicatorKey}/history`);
			if (!historyResponse.ok) return;
			const history = await historyResponse.json();

			this.setIndicatorHistory(indicatorKey, history);
		} catch {
			// Network error during rapid indicator changes — silently ignore
		}
	}

	/** DELETE indicator from backend and remove from local state. */
	private async removeIndicator(key: string): Promise<void> {
		try {
			await fetch(`${API_BASE_URL}/api/indicators/${key}`, { method: 'DELETE' });
		} catch {
			// Connection may be lost during rapid changes — clean up locally regardless
		}
		const cleaned = { ...this.indicators };
		delete cleaned[key];
		this.indicators = cleaned;
	}

	reset() {
		this.prices = [];
		this.indicators = {};
	}
}
