import { createContext } from "svelte";
import type { SyntheticInstrument } from "./instrument.svelte";

export const [getInstrumentContext, setInstrumentContext] = createContext<SyntheticInstrument>();