import { createResource } from 'frappe-ui'

const LANGUAGE_STORAGE_KEY = 'lms_preferred_language'

export default function translationPlugin(app) {
	app.config.globalProperties.__ = translate
	window.__ = translate
	window.setLanguage = setLanguage
	window.getCurrentLanguage = getCurrentLanguage

	const stored = localStorage.getItem(LANGUAGE_STORAGE_KEY)
	if (stored) {
		window.boot = window.boot || {}
		window.boot.language = stored
	}

	fetchTranslations(stored || window.boot?.language)
}

function translate(message) {
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
	return (
		localStorage.getItem(LANGUAGE_STORAGE_KEY) ||
		window.boot?.language ||
		'en'
	)
}

export function fetchTranslations(lang) {
	return createResource({
		url: 'lms.lms.api.get_translations',
		params: lang ? { lang } : {},
		cache: false,
		auto: true,
		onSuccess(data) {
			window.translatedMessages = data
		},
	})
}

export async function setLanguage(language) {
	const { call } = await import('frappe-ui')
	const result = await call('lms.lms.api.set_language', { language })

	localStorage.setItem(LANGUAGE_STORAGE_KEY, result.language)
	window.translatedMessages = result.translations
	if (window.boot) {
		window.boot.language = result.language
	}

	// Reload so route-level strings and cached components pick up the new locale.
	window.location.reload()
}
