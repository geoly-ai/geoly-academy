import AudioBlock from '@/components/AudioBlock.vue'
import VideoBlock from '@/components/VideoBlock.vue'
import UploadPlugin from '@/components/UploadPlugin.vue'
import { h, createApp } from 'vue'
import { Upload as UploadIcon } from 'lucide-vue-next'
import { createDialog } from '@/utils/dialogs'
import translationPlugin from '../translation'
import {
	getVideoTypeFromUrl,
	videoFileTypes,
	videoUrlPattern,
} from '@/utils/media'

export class Upload {
	constructor({ data, api, block, readOnly }) {
		this.data = data || {}
		this.api = api
		this.block = block
		this.readOnly = readOnly
		this.insertIndex = null
	}

	static get toolbox() {
		const app = createApp({
			render: () =>
				h(UploadIcon, { size: 18, strokeWidth: 1.5, color: 'black' }),
		})

		const div = document.createElement('div')
		app.mount(div)

		return {
			title: (window.__ && window.__('Upload to COS')) || 'Upload to COS',
			icon: div.innerHTML,
		}
	}

	static get isReadOnlySupported() {
		return true
	}

	static get pasteConfig() {
		return {
			patterns: {
				video: videoUrlPattern,
			},
		}
	}

	render() {
		this.wrapper = document.createElement('div')

		if (this.data && this.data.file_url) {
			this.renderFile(this.data)
		} else {
			this.renderFileUploader()
		}

		return this.wrapper
	}

	renderFile(file) {
		this.wrapper.innerHTML = ''

		if (this.isVideo(file.file_type)) {
			const app = createApp(VideoBlock, {
				file: file.play_url || file.file_url,
				source: file.file_url,
				readOnly: this.readOnly,
				quizzes: file.quizzes || [],
				saveQuizzes: (quizzes) => {
					if (this.readOnly) return
					this.data.quizzes = quizzes
				},
			})
			app.use(translationPlugin)
			app.config.globalProperties.$dialog = createDialog
			app.mount(this.wrapper)
			return
		} else if (this.isAudio(file.file_type)) {
			const app = createApp(AudioBlock, {
				file: file.file_url,
			})
			app.mount(this.wrapper)
			return
		} else if (file.file_type?.toLowerCase() === 'pdf') {
			const src = file.file_url.startsWith('http')
				? encodeURI(file.file_url)
				: `${window.location.origin}${encodeURI(file.file_url)}`
			this.wrapper.innerHTML = `<iframe src="${src}" width='100%' height='700px' class="mb-4" type="application/pdf"></iframe>`
			return
		} else if (this.isCourseware(file.file_type)) {
			const href = file.file_url.startsWith('http')
				? encodeURI(file.file_url)
				: `${window.location.origin}${encodeURI(file.file_url)}`
			const label =
				(window.__ && window.__('Download courseware')) || 'Download courseware'
			this.wrapper.innerHTML = `<a class="mb-4 inline-flex items-center text-ink-blue-3 underline" href="${href}" target="_blank" rel="noopener noreferrer">${label} (${file.file_type})</a>`
			return
		} else {
			const src = file.file_url.startsWith('http')
				? encodeURI(file.file_url)
				: encodeURI(file.file_url)
			this.wrapper.innerHTML = `<img class="mb-4" src="${src}" width='100%'>`
			return
		}
	}

	renderFileUploader() {
		this.insertIndex = this.getCurrentBlockIndex()
		const app = createApp(UploadPlugin, {
			onFilesUploaded: (files) => this.addFiles(files),
		})
		app.use(translationPlugin)
		app.mount(this.wrapper)
	}

	addFiles(files) {
		files = Array.isArray(files) ? files : [files]
		if (!files.length) return

		const [firstFile, ...remainingFiles] = files
		this.data.file_url = firstFile.file_url
		this.data.file_type = firstFile.file_type
		this.renderFile(firstFile)

		remainingFiles.forEach((file, index) => {
			this.api?.blocks?.insert(
				'upload',
				{
					file_url: file.file_url,
					file_type: file.file_type,
				},
				{},
				this.getInsertIndex() + index + 1,
				false
			)
		})
	}

	onPaste(event) {
		if (event.type !== 'pattern') return

		const videoUrl = event.detail.data?.trim()
		const fileType = getVideoTypeFromUrl(videoUrl)
		if (!fileType) return

		this.data.file_url = videoUrl
		this.data.file_type = fileType
		if (this.wrapper) {
			this.renderFile(this.data)
		}
	}

	validate(savedData) {
		if (!savedData.file_url || !savedData.file_type) {
			return false
		}
		return true
	}

	save(blockContent) {
		return {
			file_url: this.data.file_url,
			file_type: this.data.file_type,
			quizzes: this.data.quizzes || [],
		}
	}

	isVideo(type) {
		return videoFileTypes.includes(type?.toLowerCase())
	}

	isAudio(type) {
		return ['mp3', 'wav', 'ogg'].includes(type?.toLowerCase())
	}

	isCourseware(type) {
		return [
			'ppt',
			'pptx',
			'doc',
			'docx',
			'xls',
			'xlsx',
			'zip',
			'rar',
			'txt',
		].includes(type?.toLowerCase())
	}

	getCurrentBlockIndex() {
		const ownBlockIndex = this.getOwnBlockIndex()
		if (ownBlockIndex !== null) return ownBlockIndex

		const currentIndex = this.api?.blocks?.getCurrentBlockIndex?.()
		if (Number.isInteger(currentIndex) && currentIndex >= 0) {
			return currentIndex
		}

		const blockCount = this.api?.blocks?.getBlocksCount?.()
		return Number.isInteger(blockCount) && blockCount > 0 ? blockCount - 1 : 0
	}

	getInsertIndex() {
		return Number.isInteger(this.insertIndex)
			? this.insertIndex
			: this.getCurrentBlockIndex()
	}

	getOwnBlockIndex() {
		const blockCount = this.api?.blocks?.getBlocksCount?.()
		if (!this.block?.id || !Number.isInteger(blockCount)) return null

		for (let index = 0; index < blockCount; index++) {
			if (this.api.blocks.getBlockByIndex(index)?.id === this.block.id) {
				return index
			}
		}
		return null
	}

}
