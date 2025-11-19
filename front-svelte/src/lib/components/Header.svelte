<script lang="ts">
	import * as Menubar from '$lib/components/ui/menubar/index.js';

	// later you can pass routes, user info, etc.
</script>

<header class="flex items-center justify-center mt-3">
	<div class="item-center justitify-center flex">
		<Menubar.Root class="flex items-center">
			<Menubar.Menu>
				<Menubar.Trigger class="font-semibold">Duc Jeremy Vu</Menubar.Trigger>

				<Menubar.Content>
					<Menubar.Item>
						<a href="/">Home</a>
					</Menubar.Item>

					<Menubar.Separator />

					<Menubar.Item>
						<a href="/tools/opening-range-30m">30 Min Open</a>
					</Menubar.Item>

					<Menubar.Separator />

					<Menubar.Item>
						<a href="/tools/context-replay">Context Replay</a>
					</Menubar.Item>
				</Menubar.Content>
			</Menubar.Menu>
		</Menubar.Root>
	</div>
</header>
