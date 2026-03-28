<script lang="ts">
	let { stream } = $props();
</script>

<div class="controls-bar">
	<button onclick={() => (stream.paused ? stream.resume() : stream.pause())}>
		{stream.paused ? 'Resume' : 'Pause'}
	</button>
	<select
		value={String(stream.speed)}
		onchange={(e) => stream.setSpeed(Number(e.currentTarget.value))}
	>
		<option value="0.5">0.5x</option>
		<option value="1">1x</option>
		<option value="2">2x</option>
		<option value="5">5x</option>
	</select>
</div>

<style>
	.controls-bar {
		display: flex;
		gap: 0.5rem;
		padding: 0.4rem 0.75rem;
		align-items: center;
		background: var(--color-surface);
		border-bottom: 1px solid var(--color-border);
	}

	.controls-bar button,
	.controls-bar select {
		background: var(--color-surface-elevated);
		color: var(--color-text);
		border: 1px solid var(--color-border);
		border-radius: 6px;
		padding: 4px 10px;
		font-size: 0.8rem;
		cursor: pointer;
		outline: none;
	}

	.controls-bar button:hover,
	.controls-bar select:hover {
		border-color: var(--color-border-hover);
	}
</style>
