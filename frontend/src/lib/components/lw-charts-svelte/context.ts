import type { IChartApi, ISeriesApi, SeriesType } from 'lightweight-charts';
import { createContext } from 'svelte';

// Wrapping inside an object seems necessary since its value is initially null, and null is immutable
export type SeriesContext<T extends SeriesType> = () => ISeriesApi<T> | null;
export type ChartContext = () => IChartApi | null

export const [getChartContext, setChartContext] = createContext<ChartContext>();
export const [getSeriesContext, setSeriesContext] = createContext<SeriesContext<SeriesType>>();

export const useSeries = (): ISeriesApi<SeriesType> | null => getSeriesContext()();
export const useChart = (): IChartApi | null => getChartContext()();