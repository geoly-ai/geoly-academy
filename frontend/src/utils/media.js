export const videoFileTypes = ['mov', 'mp4', 'avi', 'mkv', 'webm']

export const videoUrlPattern =
	/^https?:\/\/[^\s"'<>]+\.(?:mov|mp4|avi|mkv|webm)(?:[?#][^\s"'<>]*)?$/i

export const isVideoUrl = (text) => {
	return videoUrlPattern.test((text || '').trim())
}

export const getVideoTypeFromUrl = (url) => {
	try {
		const extension = new URL((url || '').trim()).pathname
			.split('.')
			.pop()
			?.toLowerCase()
		return videoFileTypes.includes(extension) ? extension : null
	} catch {
		return null
	}
}

export const normalizeVideoUrlBlocks = (editorData) => {
	if (!editorData?.blocks || !Array.isArray(editorData.blocks)) {
		return editorData
	}

	return {
		...editorData,
		blocks: editorData.blocks.map((block) => {
			if (!['markdown', 'paragraph'].includes(block.type)) {
				return block
			}

			const text = getPlainText(block.data?.text)
			if (!isVideoUrl(text)) return block

			return {
				...block,
				type: 'upload',
				data: {
					file_url: text,
					file_type: getVideoTypeFromUrl(text),
				},
			}
		}),
	}
}

export const isEmptyTextBlock = (block) => {
	if (!['markdown', 'paragraph'].includes(block.type)) return false
	return !getPlainText(block.data?.text)
}

const getPlainText = (value) => {
	const html = `${value || ''}`
		.replace(/<br\s*\/?>/gi, '')
		.replace(/<[^>]*>/g, '')
		.trim()

	if (typeof document === 'undefined') return html

	const textarea = document.createElement('textarea')
	textarea.innerHTML = html
	return textarea.value.trim()
}
