<template>
	<div class="text-lg font-semibold mb-4 text-ink-gray-9">
		{{ __('My Notes') }}
	</div>
	<TextEditor
		:content="note"
		:placeholder="__('Make notes for quick revision. Press / for menu.')"
		@change="(val: string) => updateNoteText(val)"
		@transaction="handleEditorTransaction"
		:editable="true"
		:uploadArgs="{
			private: true,
		}"
		editorClass="prose prose-sm min-h-[200px] max-w-none"
	/>
</template>
<script setup lang="ts">
import { TextEditor } from 'frappe-ui'
import { useDebounceFn } from '@vueuse/core'
import { inject, nextTick, onMounted, ref, watch } from 'vue'
import type { Note, Notes } from '@/components/Notes/types'
import {
	blockQuotesClick,
	hasPendingMediaNodes,
	normalizeStoredRichTextMedia,
	resolveRichTextMediaHTML,
} from '@/utils/'

const note = ref<string | null>(null)
const currentNoteName = ref<string | null>(null)
const suppressNoteSync = ref(false)
let noteRenderRequestId = 0
const user = inject<any>('$user')
const notes = defineModel<Notes>('notes')

const props = defineProps<{
	lesson: string
}>()

onMounted(() => {
	updateCurrentNote()
})

watch(
	() => notes.value?.data,
	async () => {
		await updateCurrentNote()
		blockQuotesClick()
	}
)

const updateCurrentNote = async () => {
	const currentNote = notes.value?.data?.filter((row: Note) => {
		return !row.highlighted_text && row.note !== ''
	})
	if (currentNote?.length === 0) {
		note.value = null
		currentNoteName.value = null
		return
	} else if (currentNote && currentNote.length > 0) {
		currentNoteName.value = currentNote[0].name
		await renderNote(currentNote[0].note || null)
	}
}

const renderNote = async (html: string | null) => {
	const requestId = ++noteRenderRequestId
	suppressNoteSync.value = true
	const resolvedHTML = await resolveRichTextMediaHTML(html)
	if (requestId !== noteRenderRequestId) return
	note.value = resolvedHTML
	await nextTick()
	suppressNoteSync.value = false
}

const updateNoteText = (val: string) => {
	note.value = val
	if (suppressNoteSync.value) return
	if (hasPendingMediaNodes(val)) return
	debouncedSave()
}

const handleEditorTransaction = (editorInstance: { getHTML: () => string }) => {
	const html = editorInstance.getHTML()
	if (html === note.value) return

	if (suppressNoteSync.value) {
		note.value = html
		return
	}

	const hadPendingMedia = hasPendingMediaNodes(note.value)
	note.value = html
	if (hadPendingMedia && !hasPendingMediaNodes(html)) {
		debouncedSave()
	}
}

const debouncedSave = useDebounceFn(() => {
	saveNotes()
}, 2000)

const saveNotes = () => {
	if (hasPendingMediaNodes(note.value)) return
	if (currentNoteName.value) {
		updateNote()
	} else {
		createNote()
	}
}

const createNote = () => {
	notes.value?.insert.submit(
		{
			lesson: props.lesson,
			member: user?.data?.name,
			note: normalizeStoredRichTextMedia(note.value),
			color: 'Yellow',
			name: '',
		},
		{
			onSuccess(data: Note) {
				currentNoteName.value = data.name || null
			},
			onError(err: any) {
				console.error('Error creating note:', err)
			},
		}
	)
}

const updateNote = () => {
	if (!currentNoteName.value) return
	notes.value?.setValue.submit(
		{
			name: currentNoteName.value,
			lesson: props.lesson,
			member: user?.data?.name,
			note: normalizeStoredRichTextMedia(note.value),
		},
		{
			onSuccess(data: Note) {
				currentNoteName.value = data.name || currentNoteName.value
			},
			onError(err: any) {
				console.error('Error updating note:', err)
			},
		}
	)
}

</script>
