<template>
	<div class="relative flex h-full flex-col">
		<div class="h-full flex-1">
			<div class="flex h-screen text-base bg-surface-white">
				<div class="w-full overflow-auto" id="scrollContainer">
					<slot />
				</div>
			</div>
		</div>
		<button
			type="button"
			class="fixed bottom-3 end-4 z-30 text-p-xs text-ink-gray-6 hover:text-ink-gray-9 underline"
			@click="showAboutDialog = true"
		>
			{{ __('About') }}
		</button>
		<AboutDialog v-model="showAboutDialog" />
	</div>
</template>

<script setup>
import { ref } from 'vue'
import AboutDialog from '@/components/AboutDialog.vue'

const showAboutDialog = ref(false)
</script>
