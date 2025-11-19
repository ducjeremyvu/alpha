<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<div class="centered">
	{@render children()}
</div>

<style>
	:global(:root) {
		font-family: system-ui, Avenir, Helvetica, Arial, sans-serif;
		line-height: 1.5;
		font-weight: 400;

		color-scheme: light dark;
		color: rgba(255, 255, 255, 0.87);
		background-color: #242424;

		font-synthesis: none;
		text-rendering: optimizeLegibility;
		-webkit-font-smoothing: antialiased;
		-moz-osx-font-smoothing: grayscale;
	}

	:global(body) {
		margin: 0;
		font-family:
			system-ui,
			-apple-system,
			BlinkMacSystemFont,
			sans-serif;
		color: #e5e7eb;
		display: flex;
		place-items: center;
	}

	:global(h1) {
		font-size: 2.2em;
		line-height: 1.1;
		display: flex;
	}

	:global(header) {
		padding: 0.75rem 1rem;
		border-bottom: 1px solid #1f2937;
		display: flex;
		gap: 0.75rem;
		align-items: center;
	}

	.centered {
		display: flex;
		flex-direction: column;
		align-items: center; /* horizontal alignment */
		text-align: center; /* text inside headings/links centered */
	}
</style>
