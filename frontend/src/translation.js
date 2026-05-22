import { ref } from 'vue'
import { createResource } from 'frappe-ui'

const LANGUAGE_STORAGE_KEY = 'lms_preferred_language'
const FORCED_LANGUAGE = 'zh'

/** Bump to re-run Vue computeds that call __() after translations load. */
export const i18nRevision = ref(0)

export default function translationPlugin(app) {
	app.config.globalProperties.__ = translate
	window.__ = translate
	window.setLanguage = setLanguage
	window.getCurrentLanguage = getCurrentLanguage

	// C-side UI is locked to Chinese; clear any previously stored
	// preference so users coming back from the old switcher land on zh.
	localStorage.setItem(LANGUAGE_STORAGE_KEY, FORCED_LANGUAGE)
	window.boot = window.boot || {}
	window.boot.language = FORCED_LANGUAGE

	fetchTranslations(FORCED_LANGUAGE)
}

function translate(message) {
	// Vue computed() must depend on this to refresh after async translations arrive.
	i18nRevision.value

	let translatedMessages = window.translatedMessages || {}
	let translatedMessage = translatedMessages[message] || message

	const hasPlaceholders = /{\d+}/.test(message)
	if (!hasPlaceholders) {
		return translatedMessage
	}
	return {
		format: function (...args) {
			return translatedMessage.replace(/{(\d+)}/g, function (match, number) {
				return typeof args[number] != 'undefined' ? args[number] : match
			})
		},
	}
}

export function getCurrentLanguage() {
	return FORCED_LANGUAGE
}

export function fetchTranslations(lang) {
	return createResource({
		url: 'lms.lms.api.get_translations',
		params: lang ? { lang } : {},
		cache: false,
		auto: true,
		onSuccess(data) {
			window.translatedMessages = data || {}
			i18nRevision.value += 1
		},
	})
}

export async function setLanguage(language) {
	const { call } = await import('frappe-ui')
	const result = await call('lms.lms.api.set_language', { language })

	localStorage.setItem(LANGUAGE_STORAGE_KEY, result.language)
	window.translatedMessages = result.translations || {}
	i18nRevision.value += 1
	if (window.boot) {
		window.boot.language = result.language
	}

	window.location.reload()
}
