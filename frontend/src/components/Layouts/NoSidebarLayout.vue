<template>
	<div class="relative flex h-full flex-col">
		<div class="absolute right-4 top-4 z-30">
			<LanguageSwitcher />
		</div>
		<div class="h-full flex-1">
			<div class="flex h-screen text-base bg-surface-white">
				<div class="w-full overflow-auto" id="scrollContainer">
					<slot />
				</div>
			</div>
		</div>
		<SourceCodeLink />
	</div>
</template>

<script setup>
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
import SourceCodeLink from '@/components/SourceCodeLink.vue'
</script>
