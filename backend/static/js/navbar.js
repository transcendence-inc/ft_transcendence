import router from '/static/js/router.js';

document.addEventListener('DOMContentLoaded', function() {
	update_navbar();

	setup_language();

	document.getElementById('home-link').addEventListener('click', function(event) {
		event.preventDefault();
		router.navigateTo('/');
	});
	
	document.getElementById('transcendence-link').addEventListener('click', function(event) {
		event.preventDefault();
		router.navigateTo('/');
	});
	
	document.getElementById('quiz-link').addEventListener('click', function(event) {
		event.preventDefault();
		router.navigateTo('/quiz/');
	});
	
	document.getElementById('dashboard-link').addEventListener('click', function(event) {
		event.preventDefault();
		router.navigateTo('/dashboard/');
	});
	
	document.getElementById('register-link').addEventListener('click', function(event) {
		event.preventDefault();
		router.navigateTo('/register/');
	});
	
	document.getElementById('login-link').addEventListener('click', function(event) {
		event.preventDefault();
		router.navigateTo('/login/');
	});
	
	document.getElementById('logout-link').addEventListener('click', function(event) {
		event.preventDefault();
		router.navigateTo('/logout/');
	});
	
	document.getElementById('account-link').addEventListener('click', function(event) {
		event.preventDefault();
		router.navigateTo('/account/');
	});
});


export function clear_containers() {
	document.getElementById('home-content').innerHTML = '';
	document.getElementById('chat-app-content').innerHTML = '';
	document.getElementById('about-content').innerHTML = '';
	document.getElementById('quiz-app-content').innerHTML = '';
	document.getElementById('pong-app-content').innerHTML = '';
	document.getElementById('user-app-content').innerHTML = '';
	document.getElementById('error-content').innerHTML = '';
	document.getElementById('dashboard-app-content').innerHTML = '';
}

export function home_view() {
	const home = document.getElementById('home-content');
	home.innerHTML = `
	<h2>${gettext("Welcome to the Transcendence Webpage")}</h2>
	`;
}

export function update_navbar() {
	fetch('/users/api/check_authentication/')
	.then(response => response.json())
	.then(data => {
		const navbars = document.getElementById('navbar-right');
		if (data.is_authenticated) {
			const username = document.querySelector('meta[name="username-token"]').content;
			navbars.innerHTML = `
			<a class="nav-item nav-link" href="/dashboard/${username}" id="personal-profile-link">${username}</a>
			<a class="nav-item nav-link" href="/account/" id="account-link">${gettext("Account")}</a>
			<a class="nav-item nav-link" href="/logout/" id="logout-link">${gettext("Logout")}</a>
			`;
			document.getElementById('personal-profile-link').addEventListener('click', function(event) {
				event.preventDefault();
				router.navigateTo(`/dashboard/${username}`);
			});
			document.getElementById('account-link').addEventListener('click', function(event) {
				event.preventDefault();
				router.navigateTo('/account/');
			});
			document.getElementById('logout-link').addEventListener('click', function(event) {
				event.preventDefault();
				router.navigateTo('/logout/');
			});
		} else {
			navbars.innerHTML = `
			<a class="nav-item nav-link" href="/login/" id="login-link">${gettext("Login")}</a>
			<a class="nav-item nav-link" href="/register/" id="register-link">${gettext("Register")}</a>
			`;
			document.getElementById('register-link').addEventListener('click', function(event) {
				event.preventDefault();
				router.navigateTo('/register/');
			});
			
			document.getElementById('login-link').addEventListener('click', function(event) {
				event.preventDefault();
				router.navigateTo('/login/');
			});
		}
	});
}

function setup_language() {
	const languages = [
		{code: 'en', name: 'English', flag: '/media/flags/en.svg'},
		{code: 'sv', name: 'Svenska', flag: '/media/flags/sv.svg'},
		{code: 'de', name: 'Deutsch', flag: '/media/flags/de.svg'},
	];

	const currentLanguageCode = document.documentElement.lang || 'en';
	const currentLanguage = languages.find(language => language.code === currentLanguageCode);

	const currentLanguageFlag = document.getElementById('current-language-flag');
	currentLanguageFlag.src = currentLanguage.flag;
	currentLanguageFlag.alt = currentLanguage.code;

	const languageOptions = document.getElementById('language-options');
	languages.forEach(language => {
		if (language.code !== currentLanguageCode) {
			const li = document.createElement('li');
			const a = document.createElement('a');
			a.className = 'dropdown-item language-option';
			a.href = '';
			a.dataset.lang = language.code;
			a.innerHTML = `<img src="${language.flag}" alt="${language.code}" height="30"> ${language.name}`;
			li.appendChild(a);
			languageOptions.appendChild(li);
		}
	});

	document.querySelectorAll('.language-option').forEach(option => {
		option.addEventListener('click', function(event) {
			event.preventDefault();
			const selectedLanguage = option.getAttribute('data-lang');
			const formData = new FormData();
			formData.append('language', selectedLanguage);
			formData.append('next', window.location.pathname);
			const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
			formData.append('csrfmiddlewaretoken', csrfToken);

			console.log('Setting language to', selectedLanguage);

			fetch('/i18n/setlang/', {
				method: 'POST',
				credentials: 'same-origin',
				body: formData,
			})
			.then(response => {
				if (response.ok) {
					console.log('Language set successfully');
					window.location.reload();
				} else {
					console.error('Failed to set language');
				}
			})
			.catch(error => {
				console.error('Failed to set language:', error);
			});
		});
	});
}