export interface BacktestTrade {
	entry_bar: number;
	exit_bar: number;
	direction: 'long' | 'short';
	entry_price: number;
	exit_price: number;
	pnl: number;
}

export interface BacktestMarker {
	time: number;
	direction: 'long' | 'short';
}

export interface BacktestSummary {
	total_trades: number;
	winning_trades: number;
	losing_trades: number;
	total_pnl: number;
	max_drawdown: number;
	win_rate: number;
}

export interface BacktestResponse {
	trades: BacktestTrade[];
	equity_curve: { time: number; value: number }[];
	entry_markers: BacktestMarker[];
	exit_markers: BacktestMarker[];
	summary: BacktestSummary;
}

export class BacktestResult {
	trades: BacktestTrade[] = $state.raw([]);
	equityCurve: { time: number; value: number }[] = $state.raw([]);
	entryMarkers: BacktestMarker[] = $state.raw([]);
	exitMarkers: BacktestMarker[] = $state.raw([]);
	summary: BacktestSummary | null = $state.raw(null);

	load(response: BacktestResponse) {
		this.trades = response.trades;
		this.equityCurve = response.equity_curve;
		this.entryMarkers = response.entry_markers;
		this.exitMarkers = response.exit_markers;
		this.summary = response.summary;
	}

	clear() {
		this.trades = [];
		this.equityCurve = [];
		this.entryMarkers = [];
		this.exitMarkers = [];
		this.summary = null;
	}

	get hasResults(): boolean {
		return this.summary !== null;
	}
}
