import { createContext } from 'svelte';
import { useStrategyFlow } from './strategy-flow.svelte';

export const [getStrategyFlowContext, setStrategyFlowContext] =
	createContext<ReturnType<typeof useStrategyFlow>>();
