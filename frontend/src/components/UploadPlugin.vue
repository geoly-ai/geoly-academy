<template>
	<div>
		<input
			ref="fileInput"
			type="file"
			class="hidden"
			multiple
			:accept="coursewareTypes.join(',')"
			@change="uploadSelectedFiles"
		/>
		<div
			v-if="queue.length"
			class="my-3 rounded-md border border-outline-gray-2 bg-surface-gray-1 p-3"
		>
			<div class="mb-2 text-sm font-medium text-ink-gray-8">
				{{ queueComplete ? __('Upload queue complete') : __('Uploading files') }}
			</div>
			<div class="space-y-2">
				<div
					v-for="item in queue"
					:key="item.id"
					class="rounded-md border border-outline-gray-2 bg-surface-white p-2"
				>
					<div class="flex items-center justify-between gap-3 text-sm">
						<div class="min-w-0 truncate text-ink-gray-8">
							{{ item.name }}
						</div>
						<div class="shrink-0 text-xs text-ink-gray-5">
							{{ getStatusLabel(item) }}
						</div>
					</div>
					<div
						class="mt-2 h-1 overflow-hidden rounded-full bg-surface-gray-3"
					>
						<div
							class="h-full rounded-full bg-surface-gray-7 transition-all duration-300"
							:class="{ 'bg-surface-red-5': item.status === 'failed' }"
							:style="{ width: `${item.progress}%` }"
						></div>
					</div>
					<div v-if="item.error" class="mt-1 text-xs text-ink-red-3">
						{{ item.error }}
					</div>
				</div>
			</div>
		</div>
	</div>
</template>
<script setup>
import { FileUploadHandler, toast } from 'frappe-ui'
import { computed, onMounted, ref, nextTick } from 'vue'

const fileInput = ref(null)
const queue = ref([])
const emit = defineEmits(['fileUploaded', 'filesUploaded', 'uploadFailed'])

const props = defineProps({
	onFileUploaded: {
		type: Function,
		default: null,
	},
	onFilesUploaded: {
		type: Function,
		default: null,
	},
	onUploadFailed: {
		type: Function,
		default: null,
	},
})

onMounted(async () => {
	await nextTick()
	fileInput.value?.click()
})

const queueComplete = computed(() => {
	return queue.value.every((item) => ['done', 'failed'].includes(item.status))
})

const uploadSelectedFiles = async (event) => {
	const files = Array.from(event.target.files || [])
	if (!files.length) return

	queue.value = files.map((file, index) => ({
		id: `${Date.now()}-${index}-${file.name}`,
		file,
		name: file.name,
		progress: 0,
		status: 'pending',
		error: '',
	}))

	const uploadedFiles = []

	for (const item of queue.value) {
		const validationError = validateFile(item.file)
		if (validationError) {
			markFailed(item, validationError)
			continue
		}

		try {
			const uploadedFile = await uploadFile(item)
			item.status = 'done'
			item.progress = 100
			uploadedFiles.push(await normalizeUploadedFile(uploadedFile, item.file))
		} catch (error) {
			const message = getUploadError(error)
			markFailed(item, message)
			props.onUploadFailed?.(error)
			emit('uploadFailed', error)
		}
	}

	if (uploadedFiles.length) {
		if (props.onFilesUploaded) {
			props.onFilesUploaded(uploadedFiles)
		} else {
			uploadedFiles.forEach((file) => props.onFileUploaded?.(file))
		}
		emit('filesUploaded', uploadedFiles)
		uploadedFiles.forEach((file) => emit('fileUploaded', file))
	}

	event.target.value = ''
}

const uploadFile = async (item) => {
	item.status = 'uploading'
	item.progress = 0

	const uploader = new FileUploadHandler()
	uploader.on('start', () => {
		item.status = 'uploading'
	})
	uploader.on('progress', (data) => {
		item.progress = data.total
			? Math.floor((data.uploaded / data.total) * 100)
			: 0
	})
	uploader.on('error', (error) => {
		item.error = getUploadError(error)
	})

	return uploader.upload(item.file, { private: 0 })
}

const normalizeUploadedFile = async (file, sourceFile) => {
	const extension = getExtension(sourceFile.name)
	if (!file?.file_url) {
		throw new Error(__('File upload failed. Please try again.'))
	}
	const fileType = file.file_type?.includes('/') ? extension : file.file_type
	const normalizedFileType = fileType || extension
	const playURL = await getSignedMediaURL(file.file_url, normalizedFileType)

	return {
		file_url: file.file_url,
		file_type: normalizedFileType,
		file_name: file.file_name || sourceFile.name,
		...(playURL ? { play_url: playURL } : {}),
	}
}

const getSignedMediaURL = async (fileURL, fileType) => {
	if (!allowedVideoExtensions.includes((fileType || '').toLowerCase())) {
		return null
	}

	try {
		const params = new URLSearchParams({
			file_url: fileURL,
			file_type: fileType,
		})
		const response = await fetch(
			`/api/method/lms.lms.cdn_auth.get_signed_media_url?${params}`,
			{ credentials: 'same-origin' }
		)
		const data = await response.json()
		return data?.message?.play_url || null
	} catch (error) {
		console.error(error)
		return null
	}
}

const markFailed = (item, message) => {
	item.status = 'failed'
	item.progress = 100
	item.error = message
	toast.error(message)
}

const getStatusLabel = (item) => {
	if (item.status === 'pending') return __('Queued')
	if (item.status === 'uploading')
		return __('Uploading {0}%').format(item.progress)
	if (item.status === 'done') return __('Uploaded')
	return __('Failed')
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

const allowedVideoExtensions = ['mp4', 'mov', 'avi', 'mkv', 'webm']

const validateFile = (file) => {
	let extension = getExtension(file.name)
	if (!allowedExtensions.includes(extension)) {
		return __('Unsupported file type. Allowed: images, video, audio, PDF, Office, ZIP.')
	}
}

const getExtension = (fileName) => {
	return fileName.split('.').pop()?.toLowerCase() || ''
}

const getUploadError = (error) => {
	try {
		if (error?._server_messages) {
			return JSON.parse(JSON.parse(error._server_messages)[0]).message
		} else if (error?.exc) {
			return JSON.parse(error.exc)[0].split('\n').slice(-2, -1)[0]
		}
	} catch (parseError) {
		console.error(parseError)
	}

	if (error?.message) {
		return error.message
	}
	return __('File upload failed. Please try again.')
}
</script>
