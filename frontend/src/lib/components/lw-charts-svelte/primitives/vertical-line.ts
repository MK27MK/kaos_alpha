import { CanvasRenderingTarget2D } from 'fancy-canvas';
import {
	type Coordinate,
	type IChartApi,
	type IPrimitivePaneRenderer,
	type IPrimitivePaneView,
	type ISeriesApi,
	type ISeriesPrimitive,
	type ISeriesPrimitiveAxisView,
	type SeriesType,
	type Time
} from 'lightweight-charts';
import { positionsLine, type VertLineOptions } from './utils.ts';

class VertLinePaneRenderer implements IPrimitivePaneRenderer {
	constructor(
		private _x: Coordinate | null = null,
		protected _options: VertLineOptions
	) {}
	draw(target: CanvasRenderingTarget2D) {
		target.useBitmapCoordinateSpace((scope) => {
			if (this._x === null) return;
			const ctx = scope.context;
			const position = positionsLine(this._x, scope.horizontalPixelRatio, this._options.width);
			ctx.fillStyle = this._options.color;
			ctx.fillRect(position.position, 0, position.length, scope.bitmapSize.height);
		});
	}
}

class VertLinePaneView implements IPrimitivePaneView {
	private _x: Coordinate | null = null;

	constructor(
		protected _source: VertLine,
		protected _options: VertLineOptions
	) {}
	update() {
		const timeScale = this._source._chart.timeScale();
		this._x = timeScale.timeToCoordinate(this._source._time);
	}
	renderer() {
		return new VertLinePaneRenderer(this._x, this._options);
	}
}

class VertLineTimeAxisView implements ISeriesPrimitiveAxisView {
	private _x: Coordinate | null = null;

	constructor(
		protected _source: VertLine,
		protected _options: VertLineOptions
	) {}
	update() {
		const timeScale = this._source._chart.timeScale();
		this._x = timeScale.timeToCoordinate(this._source._time);
	}
	visible() {
		return this._options.showLabel;
	}
	tickVisible() {
		return this._options.showLabel;
	}
	coordinate() {
		return this._x ?? 0;
	}
	text() {
		return this._options.labelText;
	}
	textColor() {
		return this._options.labelTextColor;
	}
	backColor() {
		return this._options.labelBackgroundColor;
	}
}

const defaultOptions: VertLineOptions = {
	color: 'green',
	labelText: '',
	width: 3,
	labelBackgroundColor: 'green',
	labelTextColor: 'white',
	showLabel: false
};

export class VertLine implements ISeriesPrimitive<Time> {
	private _paneViews: VertLinePaneView[];
	private _timeAxisViews: VertLineTimeAxisView[];

	constructor(
		public _chart: IChartApi,
		public _series: ISeriesApi<SeriesType>,
		public _time: Time,
		options?: Partial<VertLineOptions>
	) {
		const vertLineOptions: VertLineOptions = {
			...defaultOptions,
			...options
		};
		this._paneViews = [new VertLinePaneView(this, vertLineOptions)];
		this._timeAxisViews = [new VertLineTimeAxisView(this, vertLineOptions)];
	}
	updateAllViews() {
		this._paneViews.forEach((pw) => pw.update());
		this._timeAxisViews.forEach((tw) => tw.update());
	}
	timeAxisViews() {
		return this._timeAxisViews;
	}
	paneViews() {
		return this._paneViews;
	}
}
