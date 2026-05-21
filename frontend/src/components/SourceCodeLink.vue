<template>
	<div
		v-if="sourceUrl"
		class="border-t border-outline-gray-2 bg-surface-menu-bar px-4 py-2 text-center text-p-xs text-ink-gray-6"
	>
		{{ __('Modified under AGPL-3.0. Corresponding source:') }}
		<a
			:href="sourceUrl"
			target="_blank"
			rel="noopener noreferrer"
			class="ml-1 text-ink-gray-8 underline"
		>
			{{ sourceUrl }}
		</a>
	</div>
</template>

<script setup>
import { computed } from 'vue'

const sourceUrl = computed(() => window.source_code_url || window.boot?.source_code_url || '')
</script>
