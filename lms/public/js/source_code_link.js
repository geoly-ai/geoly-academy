(function () {
	const loginPath = window.location.pathname.replace(/\/+$/, '') || '/'
	if (loginPath !== '/login') return

	const renderSourceLink = (sourceUrl) => {
		if (!sourceUrl || document.getElementById('lms-source-code-link')) return

		const wrapper = document.createElement('div')
		wrapper.id = 'lms-source-code-link'
		wrapper.style.cssText = [
			'margin-top:16px',
			'text-align:center',
			'font-size:12px',
			'line-height:18px',
			'color:#6b7280',
		].join(';')

		const prefix = document.createElement('span')
		prefix.textContent = 'Modified under AGPL-3.0. Corresponding source: '

		const link = document.createElement('a')
		link.href = sourceUrl
		link.target = '_blank'
		link.rel = 'noopener noreferrer'
		link.textContent = 'Source Code / 源代码'
		link.style.cssText = 'color:#374151;text-decoration:underline'

		wrapper.appendChild(prefix)
		wrapper.appendChild(link)

		const form = document.querySelector('form')
		const target = form?.parentElement || form || document.querySelector('main') || document.body
		target.appendChild(wrapper)
	}

	const loadSourceUrl = async () => {
		try {
			const response = await fetch('/api/method/lms.lms.api.get_source_code_url', {
				credentials: 'same-origin',
			})
			if (!response.ok) return
			const data = await response.json()
			renderSourceLink(data?.message?.source_code_url)
		} catch (error) {
			console.error(error)
		}
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', loadSourceUrl, { once: true })
	} else {
		loadSourceUrl()
	}
})()
