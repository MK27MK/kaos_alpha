<script lang="ts">
	import { useSvelteFlow } from '@xyflow/svelte';

	interface AddNodeMenuProps {
		onaddnode: (type: string, position: { x: number; y: number }) => void;
	}

	let { onaddnode }: AddNodeMenuProps = $props();

	let expanded = $state(false);

	const { screenToFlowPosition } = useSvelteFlow();

	const menuItems = [
		{ type: 'condition', label: '\u25C6 Condition' },
		{ type: 'entry', label: '\u25B6 Entry' },
		{ type: 'exit', label: '\u25FC Exit' }
	] as const;

	/**
	 * Uses the flow container's bounding rect (not window center) because
	 * the flow only occupies the right half of the viewport.
	 */
	function getFlowCenter(): { x: number; y: number } {
		const flowEl = document.querySelector('.svelte-flow');
		if (!flowEl)
			return screenToFlowPosition({ x: window.innerWidth / 2, y: window.innerHeight / 2 });
		const rect = flowEl.getBoundingClientRect();
		const centerX = rect.left + rect.width / 2;
		const centerY = rect.top + rect.height / 2;
		return screenToFlowPosition({ x: centerX, y: centerY });
	}

	function handleItemClick(type: string) {
		onaddnode(type, getFlowCenter());
		expanded = false;
	}
</script>

<div class="add-node-menu">
	<div class="items-container" class:expanded>
		{#each menuItems as item (item.type)}
			<button class="menu-item {item.type}" onclick={() => handleItemClick(item.type)}>
				{item.label}
			</button>
		{/each}
	</div>
	<!-- NOTE -->
	<button class="toggle-btn" class:expanded onclick={() => (expanded = !expanded)}> + </button>
</div>

<style>
	.add-node-menu {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.5rem;
	}

	.items-container {
		display: flex;
		flex-direction: column;
		gap: 0.35rem;
		max-height: 0;
		opacity: 0;
		overflow: hidden;
		transition:
			max-height 0.3s ease,
			opacity 0.25s ease;
		pointer-events: none;
	}

	.items-container.expanded {
		max-height: 200px;
		opacity: 1;
		pointer-events: auto;
	}

	.menu-item {
		padding: 0.45rem 1rem;
		border: 1px solid var(--color-border);
		border-radius: 8px;
		background: var(--color-surface-elevated);
		color: var(--color-text);
		font-size: 0.85rem;
		cursor: pointer;
		white-space: nowrap;
		transition:
			background 0.15s ease,
			transform 0.15s ease,
			border-color 0.15s ease;
	}

	.menu-item:hover {
		background: var(--color-bg);
		transform: scale(1.04);
	}

	.menu-item.condition:hover {
		color: var(--color-condition);
		border-color: var(--color-condition);
	}

	.menu-item.entry:hover {
		color: var(--color-entry);
		border-color: var(--color-entry);
	}

	.menu-item.exit:hover {
		color: var(--color-exit);
		border-color: var(--color-exit);
	}

	.toggle-btn {
		width: 42px;
		height: 42px;
		border-radius: 50%;
		border: 1px solid var(--color-border);
		background: var(--color-surface-elevated);
		color: var(--color-text);
		font-size: 1.5rem;
		line-height: 1;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		transition:
			transform 0.3s ease,
			background 0.15s ease;
	}

	.toggle-btn.expanded {
		transform: rotate(45deg);
	}

	.toggle-btn:hover {
		background: var(--color-bg);
	}
</style>
