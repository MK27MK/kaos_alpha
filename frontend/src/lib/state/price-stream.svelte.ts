import type { SyntheticInstrument } from '$lib/state/instrument.svelte';
import { WS_BASE_URL } from '$lib/utils/env';
import type { LineData, UTCTimestamp } from 'lightweight-charts';

interface PriceMessage {
	type: 'price';
	time: number;
	value: number;
}

interface IndicatorMessage {
	type: 'indicator';
	key: string;
	time: number;
	value: number | { upper: number; middle: number; lower: number };
}

interface ControlMessage {
	type: 'control';
	action: 'pause' | 'resume' | 'speed' | 'reset';
	value?: number;
}

type ServerMessage = PriceMessage | IndicatorMessage;

export function createPriceStream(market: SyntheticInstrument) {
	// replay controls state
	let paused = $state(false);
	let speed = $state(1);
	// ws state
	let ws: WebSocket | null = null;
	let connected = $state(false);

	function send(msg: ControlMessage) {
		if (ws && ws.readyState === WebSocket.OPEN) {
			ws.send(JSON.stringify(msg));
		}
	}

	function disconnect() {
		if (ws) {
			ws.close();
			ws = null;
			connected = false;
		}
	}

	function connect() {
		if (ws) {
			disconnect();
		}

		ws = new WebSocket(`${WS_BASE_URL}/ws/price-stream`);

		ws.onopen = () => {
			connected = true;
		};

		ws.onmessage = (event: MessageEvent) => {
			const msg: ServerMessage = JSON.parse(event.data);

			if (msg.type === 'price') {
				market.appendPrice({ time: msg.time as UTCTimestamp, value: msg.value });
			} else if (msg.type === 'indicator') {
				const time = msg.time as UTCTimestamp;
				const indicatorValue: Record<string, LineData> = {};
				if (typeof msg.value === 'number') {
					indicatorValue['value'] = { time, value: msg.value } as LineData;
				} else {
					for (const [subKey, subValue] of Object.entries(msg.value)) {
						indicatorValue[subKey] = { time, value: subValue } as LineData;
					}
				}
				market.appendIndicatorValue(msg.key, indicatorValue);
			}
		};

		ws.onclose = () => {
			connected = false;
			ws = null;
		};

		ws.onerror = () => {
			connected = false;
			ws = null;
		};
	}

	// replay controls =================================================

	function pause() {
		send({ type: 'control', action: 'pause' });
		paused = true;
	}

	function resume() {
		send({ type: 'control', action: 'resume' });
		paused = false;
	}

	function setSpeed(v: number) {
		send({ type: 'control', action: 'speed', value: v });
		speed = v;
	}

	function reset() {
		send({ type: 'control', action: 'reset' });
		market.reset();
	}

	return {
		get connected() {
			return connected;
		},
		get paused() {
			return paused;
		},
		get speed() {
			return speed;
		},
		connect,
		disconnect,
		pause,
		resume,
		setSpeed,
		reset
	};
}
