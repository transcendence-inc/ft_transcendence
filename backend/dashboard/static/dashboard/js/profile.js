import router from '/static/js/router.js';

export function loadProfile(username) {
	const dashboardAppContent = document.getElementById('dashboard-app-content');
	dashboardAppContent.innerHTML = `
	<div id="pv-profile-header">
		<img id="pv-profile-picture"></img>
		<h3 id="pv-profile-name"></h3>
	</div>
	<div id="pv-profile-second-div">
		<div id="pv-profile-settings-content" style="visibility: hidden;">
			<button id="pv-show-blocked-users" class="btn btn-primary">${gettext("Blocked Users")}</button>
			<div id="pv-blocked-users-list" style="visibility: hidden;"></div>
		</div>
		<div id="pv-profile-friends-content">
			<button id="pv-show-friends-button" class="btn btn-primary">${gettext("Friends")}</button>
			<div id="pv-friends-list" style="visibility: hidden;"></div>
			<button id="pv-show-friend-requests-button" class="btn btn-primary" style="visibility: hidden;">${gettext("Friend Requests")}</button>
			<div id="pv-friend-request-list" style="visibility: hidden;"></div>
		</div>
	</div>
	<div id="pv-profile-content">
		<div id="pv-quiz-stats">
			<h4>${gettext("Quiz Stats")}</h4>
			<ul id="pv-quiz-stats-list"></ul>
		</div>
	</div>
	`;
	fetchData(username);
	document.getElementById('pv-show-blocked-users').addEventListener('click', function () {
		const blockedUsersList = document.getElementById('pv-blocked-users-list');
		if (blockedUsersList.style.visibility === 'hidden') {
			addBlockedUsersList();
		} else {
			blockedUsersList.style.visibility = 'hidden';
			blockedUsersList.innerHTML = '';
		}
	});
}

function fetchData(username) {
	fetch(`/dashboard/api/get_profile/${username}/`)
		.then(response => {
			if (response.redirected) {
				router.navigateTo('/login/');
				return;
			}
			return response.json();
		})
		.then(data => {
			console.log('Data:', data);
			if (data.success) {
				if (data.blocked === true) {
					displayBlockedProfile(data);
				} else {
					console.log('Profile:', data.profile);
					displayProfile(data.profile);
				}
			} else {
				console.error('Failed to fetch profile');
			}
		})
		.catch(error => {
			console.error('Error:', error);
			dashboardAppContent.innerHTML = `<h3>${gettext("Error loading profile for")} ${username}</h3>`;
		});
}

function displayProfile(profile) {
	const profilePicture = document.getElementById('pv-profile-picture');
	profilePicture.src = profile.image_url;
	profilePicture.alt = `${profile.username}${gettext("'s profile picture")}`;
	const profileName = document.getElementById('pv-profile-name');
	profileName.textContent = `${profile.username}${gettext("'s Profile")}`;

	if (profile.is_requests_profile === false) {
		const profileHeader = document.getElementById('pv-profile-header');
		const blockButton = document.createElement('button');
		blockButton.id = 'pv-block-button';
		blockButton.className = 'btn btn-danger';
		profileHeader.appendChild(blockButton);

		if (profile.is_user_blocked_by_requester === true) {
			blockButton.textContent = gettext('Unblock');
		} else {
			blockButton.textContent = gettext('Block');
		}
		blockButton.addEventListener('click', function () {
			if (blockButton.textContent === gettext('Block')) {
				blockUser(profile.username);
			} else {
				unblockUser(profile.username);
			}
		});
		addFriendsAddButton(profile);
	} else {
		addSettingsButton();
		document.getElementById('pv-profile-settings-content').style.visibility = 'visible';
		addShowFriendRequestsButton(profile);
	}

	addFriendsButton(profile);

	const quizStatsList = document.getElementById('pv-quiz-stats-list');
	quizStatsList.innerHTML = `
		<li>${gettext("Games Played:")} ${profile.quiz_games_played}</li>
		<li>${gettext("Games Won:")} ${profile.quiz_games_won}</li>
		<li>${gettext("Total Score:")} ${profile.quiz_total_score}</li>
		<li>${gettext("High Score:")} ${profile.quiz_high_score}</li>
		<li>${gettext("Questions Asked:")} ${profile.quiz_questions_asked}</li>
		<li>${gettext("Correct Answers:")} ${profile.quiz_correct_answers}</li>
	`;
}

function displayBlockedProfile(data) {
	console.log('Blocked:', data);
	const profilePicture = document.getElementById('pv-profile-picture');
	profilePicture.src = data.image_url;
	profilePicture.alt = `${data.username}${gettext("'s profile picture")}`;
	const profileName = document.getElementById('pv-profile-name');
	profileName.textContent = `${data.username}${gettext("'s Profile")}`;

	const profileContent = document.getElementById('pv-profile-content');
	profileContent.innerHTML = '';
	const paragraph = document.createElement('p');
	paragraph.id = 'profile-is-blocked';
	paragraph.innerHTML = `${gettext("This user has blocked you. You cannot view their profile.")}`;
	profileContent.appendChild(paragraph);

	const profileHeader = document.getElementById('pv-profile-header');
	const blockButton = document.createElement('button');
	blockButton.id = 'pv-block-button';
	blockButton.className = 'btn btn-danger';
	profileHeader.appendChild(blockButton);

	if (data.is_user_blocked_by_requester === true) {
		blockButton.textContent = gettext('Unblock');
	} else {
		blockButton.textContent = gettext('Block');
	}
	blockButton.addEventListener('click', function () {
		if (blockButton.textContent === gettext('Block')) {
			blockUser(data.username);
		} else {
			unblockUser(data.username);
		}
	});

}

function blockUser(username) {
	const csfrToken = document.querySelector('meta[name="csrf-token"]').content;

	fetch(`/users/api/block/${username}/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': csfrToken,
		}
	})
	.then(response => response.json())
	.then(data => {
		alert(data.message);
		if (data.success) {
			console.log('User blocked');
			const blockButton = document.getElementById('pv-block-button');
			blockButton.textContent = gettext('Unblock');
		} else {
			console.error('Failed to block user');
		}
	})
	.catch(error => {
		console.error('Error:', error);
	});
}

function unblockUser(username) {
	const csfrToken = document.querySelector('meta[name="csrf-token"]').content;

	fetch(`/users/api/unblock/${username}/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': csfrToken,
		}
	})
	.then(response => response.json())
	.then(data => {
		alert(data.message);
		if (data.success) {
			console.log('User unblocked');
			const blockButton = document.getElementById('pv-block-button');
			blockButton.textContent = gettext('Block');
		} else {
			console.error('Failed to unblock user');
		}
	})
	.catch(error => {
		console.error('Error:', error);
	});
}

function addSettingsButton() {
	const profileHeader = document.getElementById('pv-profile-header');
	const settingsButton = document.createElement('button');

	settingsButton.id = 'pv-settings-button';
	settingsButton.className = 'btn btn-primary';
	settingsButton.innerHTML = `
		<i class="bi bi-gear-fill"></i>
		<span class="sr-only">${gettext("Settings")}</span>
	`;
	profileHeader.appendChild(settingsButton);

	settingsButton.addEventListener('click', function () {
		router.navigateTo('/account/');
	});
}

function addFriendsAddButton(profile) {
	const profileHeader = document.getElementById('pv-profile-header');
	const friendsButton = document.createElement('button');
	friendsButton.id = 'pv-friends-add-remove-button';
	friendsButton.className = 'btn btn-primary';

	if (profile.friend_status === 'not_friends') {
		friendsButton.textContent = gettext('Add Friend');
	} else if (profile.friend_status === 'friends') {
		friendsButton.textContent = gettext('Remove Friend');
	} else if (profile.friend_status === 'friend_request_sent') {
		friendsButton.textContent = gettext('Cancel Request');
	} else if (profile.friend_status === 'friend_request_received') {
		friendsButton.textContent = gettext('Accept Request');
	}

	friendsButton.onclick = function () {
		if (friendsButton.textContent === gettext('Add Friend')) {
			addFriend(profile.username);
		} else if (friendsButton.textContent === gettext('Remove Friend')) {
			removeFriend(profile.username);
		} else if (friendsButton.textContent === gettext('Cancel Request')) {
			cancelFriendRequest(profile.username);
		} else if (friendsButton.textContent === gettext('Accept Request')) {
			acceptFriendRequest(profile.username);
		}
	};

	profileHeader.appendChild(friendsButton);
}

function addFriend(username) {
	const csfrToken = document.querySelector('meta[name="csrf-token"]').content;

	fetch(`/users/api/friends/request/${username}/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': csfrToken,
		}
	})
	.then(response => response.json())
	.then(data => {
		if (data.success) {
			console.log('Friend request sent');
			alert(data.message);
			const friendsButton = document.getElementById('pv-friends-add-remove-button');
			friendsButton.textContent = gettext('Cancel Request');
		} else {
			console.error('Failed to send friend request');
		}
	})
	.catch(error => {
		console.error('Error:', error);
	});
}

function removeFriend(username) {
	const csfrToken = document.querySelector('meta[name="csrf-token"]').content;

	const confirmed = confirm(gettext("Are you sure you want to remove this friend?"));

	if (!confirmed) {
		return;
	}

	fetch(`/users/api/friends/remove/${username}/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': csfrToken,
		}
	})
	.then(response => response.json())
	.then(data => {
		alert(data.message);
		if (data.success) {
			console.log('Friend removed');
			const friendsButton = document.getElementById('pv-friends-add-remove-button');
			friendsButton.textContent = gettext('Add Friend');
		} else {
			console.error('Failed to remove friend');
		}
	})
	.catch(error => {
		console.error('Error:', error);
	});
}

function cancelFriendRequest(username) {
	const csfrToken = document.querySelector('meta[name="csrf-token"]').content;

	const confirmed = confirm(gettext("Are you sure you want to cancel this friend request?"));

	if (!confirmed) {
		return;
	}

	fetch(`/users/api/friends/cancel/${username}/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': csfrToken,
		}
	})
	.then(response => response.json())
	.then(data => {
		alert(data.message);
		if (data.success) {
			console.log('Friend request cancelled');
			const friendsButton = document.getElementById('pv-friends-add-remove-button');
			friendsButton.textContent = gettext('Add Friend');
		} else {
			console.error('Failed to cancel friend request');
		}
	})
	.catch(error => {
		console.error('Error:', error);
	});
}

function acceptFriendRequest(username) {
	const csfrToken = document.querySelector('meta[name="csrf-token"]').content;

	fetch(`/users/api/friends/accept/${username}/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': csfrToken,
		}
	})
	.then(response => response.json())
	.then(data => {
		alert(data.message);
		if (data.success) {
			console.log('Friend request accepted');
			const friendsButton = document.getElementById('pv-friends-add-remove-button');
			friendsButton.textContent = gettext('Remove Friend');
		} else {
			console.error('Failed to accept friend request');
		}
	})
	.catch(error => {
		console.error('Error:', error);
	});
}

function addBlockedUsersList(profile) {
	const csfrToken = document.querySelector('meta[name="csrf-token"]').content;

	fetch(`/users/api/blocked/`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': csfrToken,
		}
	})
	.then(response => response.json())
	.then(data => {
		if (data.success) {
			console.log('Blocked users:', data.blocked_users);
			const blockedUsersList = document.getElementById('pv-blocked-users-list');
			blockedUsersList.style.visibility = 'visible';
			blockedUsersList.innerHTML = '';
			if (data.blocked_users.length === 0) {
				const noBlockedUsers = document.createElement('p');
				noBlockedUsers.textContent = gettext('No blocked users');
				blockedUsersList.appendChild(noBlockedUsers);
			}
			else {
				data.blocked_users.forEach(username => {
					const userItem = document.createElement('div');
					userItem.className = 'pv-blocked-user-item';
					userItem.innerHTML = `
						<span class="pv-blocked-user-name">${username}</span>
						<button class="btn btn-danger pv-unblock-button" data-username="${username}">${gettext("Unblock")}</button>
					`;
					const usernameSpan = userItem.querySelector('.pv-blocked-user-name');
					usernameSpan.onclick = function () {
						router.navigateTo(`/dashboard/${username}/`);
					};
					blockedUsersList.appendChild(userItem);
				});
			}
			const unblockButtons = document.querySelectorAll('.pv-unblock-button');
			unblockButtons.forEach(button => {
				button.addEventListener('click', function () {
					const username = button.getAttribute('data-username');
					if (button.textContent === gettext('Unblock')) {
						console.log("HEllo");
						fetch(`/users/api/unblock/${username}/`, {
							method: 'POST',
							headers: {
								'Content-Type': 'application/json',
								'X-CSRFToken': csfrToken,
							}
						})
						.then(response => response.json())
						.then(data => {
							alert(data.message);
							if (data.success) {
								console.log('User unblocked');
								button.textContent = gettext('Block');
							} else {
								console.error('Failed to unblock user');
							}
						})
						.catch(error => {
							console.error('Error:', error);
						});
					} else {
						fetch(`/users/api/block/${username}/`, {
							method: 'POST',
							headers: {
								'Content-Type': 'application/json',
								'X-CSRFToken': csfrToken,
							}
						})
						.then(response => response.json())
						.then(data => {
							alert(data.message);
							if (data.success) {
								console.log('User blocked');
								button.textContent = gettext('Unblock');
							} else {
								console.error('Failed to block user');
							}
						})
						.catch(error => {
							console.error('Error:', error);
						});
					}
				});
			});
		}
	});
}

function addFriendsButton(profile) {
	const showFriendsButton = document.getElementById('pv-show-friends-button');

	if (profile.friend_count === 1) {
		showFriendsButton.textContent = `${profile.friend_count} ${gettext("Friend")}`;
	} else {
		showFriendsButton.textContent = `${profile.friend_count} ${gettext("Friends")}`;
	}

	showFriendsButton.onclick = function () {
		const friendsList = document.getElementById('pv-friends-list');
		friendsList.innerHTML = '';
		if (friendsList.style.visibility === 'hidden') {
			fetch(`/users/api/friends/active/${profile.username}/`)
			.then(response => response.json())
			.then(data => {
				if (data.success) {
					console.log('Friends:', data.friends_users);
					showFriendsButton.textContent = `0 ${gettext("Friends")}`;
					if (data.friends_users.length === 0) {
						const noFriends = document.createElement('p');
						noFriends.textContent = gettext('No friends');
						friendsList.appendChild(noFriends);
					} else {
						const new_length = data.friends_users.length;
						if (new_length === 1) {
							showFriendsButton.textContent = `${new_length} ${gettext("Friend")}`;
						} else {
							showFriendsButton.textContent = `${new_length} ${gettext("Friends")}`;
						}
						data.friends_users.forEach(friend => {
							const friendItem = document.createElement('div');
							friendItem.className = 'pv-friend-item';
							friendItem.innerHTML = `
							<span>${friend.username}</span>
							`;
							friendItem.onclick = function () {
								router.navigateTo(`/dashboard/${friend.username}/`);
							};
							friendsList.appendChild(friendItem);
						});
					}
				} else {
					console.error('Failed to fetch friends');
					const noFriends = document.createElement('p');
					noFriends.textContent = gettext('Fetching friends failed');
					friendsList.appendChild(noFriends);
				}
			});
			friendsList.style.visibility = 'visible';
		} else {
			friendsList.style.visibility = 'hidden';
		}
	};
}

function addShowFriendRequestsButton(profile) {
	const showFriendRequestsButton = document.getElementById('pv-show-friend-requests-button');
	showFriendRequestsButton.style.visibility = 'visible';

	showFriendRequestsButton.onclick = function () {
		const friendRequestList = document.getElementById('pv-friend-request-list');
		friendRequestList.innerHTML = '';
		if (friendRequestList.style.visibility === 'visible') {
			friendRequestList.style.visibility = 'hidden';
			return;
		}
		friendRequestList.style.visibility = 'visible';
		fetch(`/users/api/friends/inactive/`)
		.then(response => response.json())
		.then(data => {
			if (data.success) {
				console.log('Friend requests:', data);
				const receivedRequestsHeader = document.createElement('h5');
				receivedRequestsHeader.textContent = gettext('Received Friend Requests:');
				friendRequestList.appendChild(receivedRequestsHeader);
				if (data.received.length === 0) {
					const noReceivedRequests = document.createElement('p');
					noReceivedRequests.textContent = gettext('No friend requests');
					friendRequestList.appendChild(noReceivedRequests);
				} else {
					data.received.forEach(username => {
						const requestItem = document.createElement('div');
						requestItem.className = 'pv-friend-request-got-item';
						requestItem.innerHTML = `
						<span class="pv-fr-list-username">${username}</span>
						<button class="btn btn-primary pv-fr-list-accept-button">${gettext('Accept')}</button>
						<button class="btn btn-danger pv-fr-list-deny-button">${gettext('Deny')}</button>
						`;
						requestItem.querySelector('.pv-fr-list-username').onclick = function () {
							router.navigateTo(`/dashboard/${username}/`);
						};
						requestItem.querySelector('.pv-fr-list-accept-button').onclick = function () {
							acceptFRFriendRequest(username, requestItem);
						};
						requestItem.querySelector('.pv-fr-list-deny-button').onclick = function () {
							denyFRFriendRequest(username, requestItem);
						};
						friendRequestList.appendChild(requestItem);
					});
				}

				const sentRequestsHeader = document.createElement('h5');
				sentRequestsHeader.textContent = gettext('Sent Friend Requests:');
				friendRequestList.appendChild(sentRequestsHeader);
				if (data.sent.length === 0) {
					const noSentRequests = document.createElement('p');
					noSentRequests.textContent = gettext('No sent friend requests');
					friendRequestList.appendChild(noSentRequests);
				} else {
					data.sent.forEach(username => {
						const requestItem = document.createElement('div');
						requestItem.className = 'pv-friend-request-sent-item';
						requestItem.innerHTML = `
						<span class="pv-fr-list-username">${username}</span>
						<button class="btn btn-danger pv-fr-list-cancel-request-button">${gettext('Remove')}</button>
						`;
						requestItem.querySelector('.pv-fr-list-username').onclick = function () {
							router.navigateTo(`/dashboard/${username}/`);
						};
						requestItem.querySelector('.pv-fr-list-cancel-request-button').onclick = function () {
							cancelFRFriendRequest(username, requestItem);
						};
						friendRequestList.appendChild(requestItem);
					});
				}
			}
		});
	};
}

function acceptFRFriendRequest(username, requestItem) {
	const csftToken = document.querySelector('meta[name="csrf-token"]').content;

	fetch(`/users/api/friends/accept/${username}/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': csftToken,
		}
	})
	.then(response => response.json())
	.then(data => {
		alert(data.message);
		if (data.success) {
			console.log('Friend request accepted');
			requestItem.remove();
		} else {
			console.error('Failed to accept friend request');
		}
	});
}

function denyFRFriendRequest(username, requestItem) {
	const csftToken = document.querySelector('meta[name="csrf-token"]').content;

	fetch(`/users/api/friends/deny/${username}/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': csftToken,
		}
	})
	.then(response => response.json())
	.then(data => {
		alert(data.message);
		if (data.success) {
			console.log('Friend request denied');
			requestItem.remove();
		} else {
			console.error('Failed to deny friend request');
		}
	});
}

function cancelFRFriendRequest(username, requestItem) {
	const csftToken = document.querySelector('meta[name="csrf-token"]').content;

	fetch(`/users/api/friends/cancel/${username}/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': csftToken,
		}
	})
	.then(response => response.json())
	.then(data => {
		alert(data.message);
		if (data.success) {
			console.log('Friend request cancelled');
			requestItem.remove();
		} else {
			console.error('Failed to cancel friend request');
		}
	});
}