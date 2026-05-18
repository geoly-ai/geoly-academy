<template>
	<div class="flex h-screen w-screen">
		<div class="h-full border-e bg-surface-menu-bar">
			<AppSidebar />
		</div>
		<div class="flex-1 flex flex-col h-full overflow-auto bg-surface-white">
			<slot />
			<SourceCodeLink />
		</div>
	</div>
</template>
<script setup>
import AppSidebar from '@/components/Sidebar/AppSidebar.vue'
import SourceCodeLink from '@/components/SourceCodeLink.vue'
</script>
