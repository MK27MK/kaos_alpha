export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
export const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK_DATA === "true";
export const WS_BASE_URL = API_BASE_URL?.replace(/^http/, 'ws') ?? 'ws://localhost:8000';

export default {
	API_BASE_URL,
	USE_MOCK_DATA,
	WS_BASE_URL,
};
