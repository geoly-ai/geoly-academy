<template>
	<FileUploader
		:fileTypes="coursewareTypes"
		:validateFile="validateFile"
		@success="(data) => addFile(data)"
		ref="fileUploader"
		class="hide"
	/>
</template>
<script setup>
import { FileUploader } from 'frappe-ui'
import { onMounted, ref, nextTick } from 'vue'

const fileUploader = ref(null)
const emit = defineEmits(['fileUploaded'])

const props = defineProps({
	onFileUploaded: {
		type: Function,
		required: true,
	},
})

onMounted(async () => {
	await nextTick()
	const fileInput = fileUploader.value.$el.querySelector('input[type="file"]')
	if (fileInput) {
		fileInput.click()
	}
})

const addFile = (file) => {
	props.onFileUploaded({
		file_url: file.file_url,
		file_type: file.file_type,
	})
}

const coursewareTypes = [
	'image/*',
	'video/*',
	'audio/*',
	'.pdf',
	'.ppt',
	'.pptx',
	'.doc',
	'.docx',
	'.xls',
	'.xlsx',
	'.zip',
	'.rar',
	'.txt',
]

const allowedExtensions = [
	'jpg',
	'jpeg',
	'png',
	'gif',
	'webp',
	'mp4',
	'mov',
	'avi',
	'mkv',
	'webm',
	'mp3',
	'wav',
	'ogg',
	'pdf',
	'ppt',
	'pptx',
	'doc',
	'docx',
	'xls',
	'xlsx',
	'zip',
	'rar',
	'txt',
]

const validateFile = (file) => {
	let extension = file.name.split('.').pop().toLowerCase()
	if (!allowedExtensions.includes(extension)) {
		return __('Unsupported file type. Allowed: images, video, audio, PDF, Office, ZIP.')
	}
}

const isVideo = (type) => {
	return ['mov', 'mp4', 'avi', 'mkv', 'webm'].includes(type.toLowerCase())
}

const isAudio = (type) => {
	return ['mp3', 'wav', 'ogg'].includes(type.toLowerCase())
}
</script>
