const container = document.getElementById("player");

function showError(message) {
  container.id = "error";
  container.textContent = message;
}

window.addEventListener("load", async () => {
  try {
    if (!window.RufflePlayer) {
      showError("Ruffle failed to load. Refresh Discord or open the page in a browser.");
      return;
    }

    const ruffle = window.RufflePlayer.newest();
    const player = ruffle.createPlayer();
    container.appendChild(player);
    await player.load("osake_riesz_e.swf");
  } catch (error) {
    console.error(error);
    showError("The game failed to start. Open the page in an external browser and check the console.");
  }
});
