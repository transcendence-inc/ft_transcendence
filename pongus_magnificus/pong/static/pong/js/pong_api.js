export function CreateGameForm(event, socket) {
	event.preventDefault();
	const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
	const oppName = document.getElementById("opp_name").value.trim();
	const userName = document.querySelector('meta[name="username-token"]').content;

	if (userName == oppName) {
		document.getElementById('game-creation-fail').innerText = "Error, you can not play against yourself!!";
		return;
	}
	document.getElementById('game-creation-fail').innerText = "";

	if (oppName) {
		console.log("Opponent Name:", oppName, "User Name:", userName);

		fetch('/pong/api/create-game/', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': csrfToken,
			},
			body: JSON.stringify({ opponent: oppName, username: userName }),
		})
			.then(response => response.json())
			.then(data => {
				if (data.game_id) {
					console.log("Created game", data.game_id);
					const all_game_data = {
						message: "create_game",
						player1: userName,
						player2: oppName,
						game_id: data.game_id,
					};
					socket.send(JSON.stringify(all_game_data));
					console.log("sended Game info")
				} else {
					if (data.invalid_jwt && data.is_logged === false) {
						document.getElementById('game-creation-fail').innerText = gettext("Please login to do this action");
					} else if (data.invalid_jwt && data.is_logged === true) {
						document.getElementById('game-creation-fail').innerText = gettext("Invalid JWT, please login again");
					} else {
						document.getElementById('game-creation-fail').innerText = gettext("Error, enter a valid Username!!");
					}
				}
			})
			.catch(error => {
				console.error('Error with API', error);
			});

	} else {
		document.getElementById('game-creation-fail').innerText = gettext("Error, enter a Username!!");
	}
}
