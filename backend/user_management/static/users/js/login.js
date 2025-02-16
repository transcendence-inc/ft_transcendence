import router from '/static/js/router.js';
import { update_navbar } from '/static/js/navbar.js';

/**
 * Login a user
 */
export function login_user() {
	const userAppContent = document.getElementById('user-app-content');

	userAppContent.innerHTML = `
	<form id="login-form" class="form">
		<fieldset class="form-group">
			<legend class="border-bottom mb-4" id="login-headline">${gettext("Login")}</legend>
			<div class="form-group">
				<label for="id_username">${gettext("Username:")}</label>
				<input type="text" name="username" id="id_username" class="form-control">
				<div id="username-errors" class="text-danger"></div>
			</div>

			<div class="form-group">
				<label for="id_password">${gettext("Password:")}</label>
				<input type="password" name="password" id="id_password" class="form-control">
				<div id="password-errors" class="text-danger"></div>
			</div>

			<button class="btn btn-outline-info" id="login-signin-button" type="submit">${gettext("Sign In")}</button>
		</fieldset>
		<button class="btn btn-outline-info" id="oauth-authenticate">${gettext("OAuth2 using 42")}</button>
		<div id="message-container"></div>
		<div class="border-top pt-3">
			<small class="text-muted" id="register-link-container">
				${gettext("Want to create an Account?")} <span class="ml-2 register-link" id="account-register-link">${gettext("Register")}</span>
			</small>
		</div>
	`;

	document.getElementById('oauth-authenticate').addEventListener('click', function (event) {
		event.preventDefault();
		router.navigateTo('/users/oauth/');
	});
	add_login_form_listener();

	document.querySelector('.register-link').addEventListener('click', function () {
		router.navigateTo('/register/');
	});
}

function add_login_form_listener() {
	document.getElementById('login-form').addEventListener('submit', async function (event) {
		event.preventDefault();
		const form = event.target;
		const formData = new FormData(form);

		document.querySelectorAll('.text-danger').forEach(el => el.innerHTML = '');
		document.querySelectorAll('.form-control').forEach(el => el.classList.remove('is-invalid'));

		let valid = true;

		if (!formData.get('username')) {
			document.getElementById('username-errors').innerHTML = `${gettext("Username is required")}`;
			document.getElementById('id_username').classList.add('is-invalid');
			valid = false;
		}

		if (!formData.get('password')) {
			document.getElementById('password-errors').innerHTML = `${gettext("Password is required")}`;
			document.getElementById('id_password').classList.add('is-invalid');
			valid = false;
		}

		if (!valid) {
			return;
		}
		const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
		const response = await fetch('/users/api/login/', {
			method: 'POST',
			body: formData,
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
			form.reset();
			if (data.csrf_token) {
				document.querySelector('meta[name="csrf-token"]').content = data.csrf_token;
			}
			if (data.username) {
				document.querySelector('meta[name="username-token"]').content = data.username;
			}
			update_navbar();
			router.navigateTo('/dashboard/');
		} else {
			document.getElementById('id_username').classList.add('is-invalid');
			document.getElementById('username-errors').innerHTML = data.message;
			document.getElementById('id_password').classList.add('is-invalid');
			document.getElementById('password-errors').innerHTML = data.message;
		}
	});
}
