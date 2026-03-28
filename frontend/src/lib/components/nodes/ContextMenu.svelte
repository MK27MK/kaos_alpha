<script lang="ts">
	import { useSvelteFlow } from '@xyflow/svelte';
	import type { useContextMenu } from './useContextMenu.svelte';

	let { contextMenu }: { contextMenu: ReturnType<typeof useContextMenu> } = $props();

	const { deleteElements } = useSvelteFlow();

	function deleteNode() {
		deleteElements({ nodes: [{ id: contextMenu.id! }] });
	}
</script>

<div
	class="context-menu"
	role="menu"
	tabindex="-1"
	style:top={contextMenu.top != null ? `${contextMenu.top}px` : undefined}
	style:left={contextMenu.left != null ? `${contextMenu.left}px` : undefined}
	style:right={contextMenu.right != null ? `${contextMenu.right}px` : undefined}
	style:bottom={contextMenu.bottom != null ? `${contextMenu.bottom}px` : undefined}
	onclick={contextMenu.handlePaneClick}
	onkeydown={(e) => {
		if (e.key === 'Escape') contextMenu.handlePaneClick();
	}}
	onpointerdown={(e) => e.stopPropagation()}
>
	<p style="margin: 0.5em;">
		<small>node: {contextMenu.id}</small>
	</p>
	<button onclick={deleteNode}>delete</button>
</div>

<style>
	.context-menu {
		background: white;
		border-style: solid;
		box-shadow: 10px 19px 20px rgba(0, 0, 0, 10%);
		position: absolute;
		z-index: 10;
	}

	.context-menu button {
		border: none;
		display: block;
		padding: 0.5em;
		text-align: left;
		width: 100%;
	}

	.context-menu button:hover {
		background: white;
	}
</style>
