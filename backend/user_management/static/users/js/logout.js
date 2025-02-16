import router from '/static/js/router.js';
import { update_navbar } from '/static/js/navbar.js';

/**
 * Logout a user
 */
export function logout_user() {
	const userAppContent = document.getElementById('user-app-content');

	logout_at_server();
	userAppContent.innerHTML = `
	<h2 id="logout-header">${gettext("Logout")}</h2>
	<div id="message-container"></div>

	<div class="border-top pt-3">
		<small class="text-muted" id="register-link-container">
			${gettext("Want to create an Account?")} <span class="ml-2 register-link" id="account-register-link">${gettext("Register")}</span>
		</small>
	</div>
	<div class="border-top pt-3">
		<small class="text-muted" id="login-link-container">
			${gettext("Already have an account?")} <span class="ml-2 sign-in-link" id="sign-in-link">${gettext("Sign In")}</span>
		</small>
	</div>
	`;

	document.querySelector('.register-link').addEventListener('click', function () {
		router.navigateTo('/register/');
	});
	document.querySelector('.sign-in-link').addEventListener('click', function () {
		router.navigateTo('/login/');
	});
}

async function logout_at_server() {
	const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

	const response = await fetch('/users/api/logout/', {
		method: 'POST',
		headers: {
			'X-Requested-With': 'XMLHttpRequest',
			'X-CSRFToken': csrfToken,
		},
	});
	const data = await response.json();
	const messageContainer = document.getElementById('message-container');
	messageContainer.innerHTML = '';
	if (data.success) {
		messageContainer.innerHTML = '<p>' + data.message + '</p>';
		if (data.csrf_token) {
			document.querySelector('meta[name="csrf-token"]').content = data.csrf_token;
			document.querySelector('meta[name="username-token"').content = undefined;
		}
		update_navbar();
	} else {
		messageContainer.innerHTML = '<p>' + data.message + '</p>';
	}
}
