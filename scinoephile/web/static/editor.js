/** @file Shared autosave feedback and draft protection for local editors. */

/**
 * Update the shared accessible save indicator.
 * @param {HTMLOutputElement} indicator - Status element in the edit form.
 * @param {string} status - Saved, saving, unsaved, invalid, or error.
 * @param {string} message - Detailed status message.
 * @param {boolean} busy - Whether a save request is active.
 */
function showEditorSaveStatus(indicator, status, message, busy) {
    indicator.dataset.saveState = status;
    indicator.querySelector("span").textContent = {
        saved: "Saved",
        saving: "Saving…",
        unsaved: "Unsaved",
        invalid: "Invalid",
        error: "Error"
    } [status];
    indicator.title = message;
    indicator.setAttribute("aria-label", message);
    indicator.setAttribute("aria-busy", String(busy));
}

/**
 * Guard both the start and the completion of navigation against unsaved drafts.
 * @param {function(): boolean} hasDrafts - Whether an editor has unsaved input.
 * @param {string} message - Guidance to show when navigation is interrupted.
 */
function guardEditorNavigation(hasDrafts, message) {
    document.addEventListener("htmx:confirm", event => {
        if (event.detail.target?.id !== "workspace" || !hasDrafts()) return;
        event.preventDefault();
        document.querySelector("#messages").textContent = message;
    });
    document.addEventListener("htmx:beforeSwap", event => {
        if (event.detail.target?.id !== "workspace" || !hasDrafts()) return;
        event.detail.shouldSwap = false;
        document.querySelector("#messages").textContent = message;
    });
}
