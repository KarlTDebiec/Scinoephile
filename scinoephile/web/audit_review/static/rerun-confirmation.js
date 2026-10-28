/** @file Enhance server-backed rerun confirmation with a final-click countdown. */

/** @type {WeakSet<HTMLButtonElement>} Buttons whose cooling-off timer is installed. */
const rerunTimers = new WeakSet();

/** Disable the third click until its server timestamp; detached controls stop ticking. */
function initRerunConfirmation() {
    for (const button of document.querySelectorAll("button[data-rerun-ready-at]")) {
        if (rerunTimers.has(button)) continue;
        rerunTimers.add(button);
        const readyAt = Number(button.dataset.rerunReadyAt) * 1000;
        const title = button.title;
        const update = () => {
            if (!button.isConnected || !button.hasAttribute("data-rerun-ready-at")) return;
            const remaining = readyAt - Date.now();
            button.disabled = button.hasAttribute("data-rerun-blocked") || remaining > 0;
            button.title = remaining > 0 ?
                `Wait ${Math.ceil(remaining / 1000)} seconds before starting (3/3)` : title;
            if (remaining > 0) setTimeout(update, Math.min(250, remaining));
        };
        update();
    }
}

// Changing configuration starts a fresh confirmation, including before the next swap.
document.addEventListener("change", (event) => {
    const form = event.target.closest("#proofreading form, #auditing form");
    if (!form || !["provider", "model", "effort"].includes(event.target.name)) return;
    form.querySelector('input[name="confirmation"]')?.remove();
    const button = form.querySelector("button[data-rerun-icon]");
    if (!button) return;
    button.removeAttribute("data-rerun-ready-at");
    button.disabled = button.hasAttribute("data-rerun-blocked");
    button.classList.remove("is-confirming");
    button.querySelector("use").setAttribute("href", button.dataset.rerunIcon);
    button.setAttribute("aria-label", button.getAttribute("aria-label").replace(/\(\d\/3\)/, "(1/3)"));
    button.title = "Click to prepare a rerun (1/3)";
});
document.addEventListener("htmx:load", initRerunConfirmation);
document.addEventListener("htmx:historyRestore", initRerunConfirmation);
initRerunConfirmation();
