<template>
	<div class="flex items-center gap-1 rounded-md border border-outline-gray-2 bg-surface-white p-0.5">
		<button
			v-for="item in languages"
			:key="item.code"
			type="button"
			class="rounded px-2 py-1 text-p-xs font-medium transition"
			:class="
				currentLanguage === item.code
					? 'bg-surface-gray-2 text-ink-gray-9'
					: 'text-ink-gray-6 hover:text-ink-gray-8'
			"
			:disabled="loading"
			@click="switchLanguage(item.code)"
		>
			{{ item.label }}
		</button>
	</div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { getCurrentLanguage, setLanguage } from '@/translation'

defineProps({
	languages: {
		type: Array,
		default: () => [
			{ code: 'en', label: 'English' },
			{ code: 'zh', label: '中文' },
		],
	},
})

const currentLanguage = ref(getCurrentLanguage())
const loading = ref(false)

onMounted(() => {
	currentLanguage.value = getCurrentLanguage()
})

const switchLanguage = async (code) => {
	if (code === currentLanguage.value || loading.value) return
	loading.value = true
	try {
		await setLanguage(code)
	} finally {
		loading.value = false
	}
}
</script>
