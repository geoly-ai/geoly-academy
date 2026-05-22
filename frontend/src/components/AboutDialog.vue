<template>
	<Dialog
		v-model="show"
		:options="{
			title: __('About'),
		}"
	>
		<template #body-content>
			<div class="text-base text-ink-gray-7 space-y-4">
				<div v-if="versionLine" class="text-p-sm text-ink-gray-6">
					{{ versionLine }}
				</div>

				<div class="space-y-3 text-p-sm leading-relaxed">
					<p>
						This software is a modified version of
						<a
							href="https://github.com/frappe/lms"
							target="_blank"
							rel="noopener noreferrer"
							class="text-ink-gray-9 underline"
						>
							Frappe Learning</a>, distributed under the GNU AGPL-3.0-or-later license.
					</p>

					<div v-if="sourceUrl">
						<div class="text-ink-gray-6">
							{{ __('Corresponding source (this deployment)') }}
						</div>
						<a
							:href="sourceUrl"
							target="_blank"
							rel="noopener noreferrer"
							class="text-ink-gray-9 underline break-all"
						>
							{{ sourceUrl }}
						</a>
					</div>
					<div v-else>
						<div class="text-ink-red-3">
							{{
								__(
									'Source code link is not configured. Please ask the operator to set lms_source_code_url.'
								)
							}}
						</div>
					</div>

					<div class="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1">
						<div class="text-ink-gray-6">License</div>
						<a
							href="https://www.gnu.org/licenses/agpl-3.0.html"
							target="_blank"
							rel="noopener noreferrer"
							class="text-ink-gray-9 underline"
						>
							GNU Affero General Public License v3.0
						</a>
						<div class="text-ink-gray-6">Upstream</div>
						<a
							href="https://github.com/frappe/lms"
							target="_blank"
							rel="noopener noreferrer"
							class="text-ink-gray-9 underline"
						>
							github.com/frappe/lms
						</a>
					</div>
				</div>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import { computed } from 'vue'
import { Dialog } from 'frappe-ui'

const show = defineModel({
	type: Boolean,
	default: false,
})

const sourceUrl = computed(
	() => window.source_code_url || window.boot?.source_code_url || ''
)

const frappeVersion = computed(() => window.boot?.frappe_version || '')

const appName = computed(() => {
	const fromBoot = window.boot?.app_name
	const fromWindow = window.app_name
	const candidate = fromBoot || fromWindow
	if (candidate && candidate !== 'Frappe') return candidate
	return ''
})

const versionLine = computed(() => {
	const parts = []
	if (appName.value) parts.push(appName.value)
	if (frappeVersion.value) parts.push(`Frappe Framework v${frappeVersion.value}`)
	return parts.join(' · ')
})
</script>
