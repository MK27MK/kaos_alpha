import type { NodeEventWithPointer } from '@xyflow/svelte';

export function useContextMenu() {
	let id = $state<string | null>(null);
	let top = $state<number | undefined>(undefined);
	let left = $state<number | undefined>(undefined);
	let right = $state<number | undefined>(undefined);
	let bottom = $state<number | undefined>(undefined);
	let flowDiv = $state<HTMLDivElement | null>(null);

	const handleContextMenu: NodeEventWithPointer<MouseEvent> = ({ event, node }) => {
		event.preventDefault();
		if (!flowDiv) return;
		// Convert viewport coords to container-relative coords,
		// since the context menu is position:absolute inside SvelteFlow.
		const bounds = flowDiv.getBoundingClientRect();
		const x = event.clientX - bounds.left;
		const y = event.clientY - bounds.top;

		id = node.id;
		top = y < bounds.height - 200 ? y : undefined;
		left = x < bounds.width - 200 ? x : undefined;
		right = x >= bounds.width - 200 ? bounds.width - x : undefined;
		bottom = y >= bounds.height - 200 ? bounds.height - y : undefined;
	};

	// Close the context menu if it's open whenever the window is clicked.
	function handlePaneClick() {
		id = null;
	}

	return {
		// Getter/setter exposes the reactive $state across the module boundary.
		// Destructuring would snapshot the value and lose reactivity.
		get id() { return id; },
		get top() { return top; },
		get left() { return left; },
		get right() { return right; },
		get bottom() { return bottom; },
		get flowDiv() { return flowDiv; },
		// setter allows bind:this to write back
		set flowDiv(el: HTMLDivElement | null) { flowDiv = el; },
		handleContextMenu,
		handlePaneClick
	};
}
