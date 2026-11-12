/** @file Shared autosave feedback and draft protection for local editors. */

/**
 * Update the shared accessible save indicator.
 * @param {HTMLOutputElement} indicator - Status element in the edit form.
 * @param {Object} state - Save status inputs.
 * @param {string} [state.error] - Request error, or empty if none.
 * @param {string} [state.invalid] - Validation error, or empty if valid.
 * @param {boolean} state.busy - Whether a save request is active.
 * @param {string} state.unsaved - Draft guidance, or empty if clean.
 */
function showEditorSaveStatus(indicator, {
    error,
    invalid,
    busy,
    unsaved
}) {
    let status = "saved";
    let message = "";
    if (error) {
        status = "error";
        message = error;
    } else if (invalid) {
        status = "invalid";
        message = invalid;
    } else if (busy) {
        status = "saving";
    } else if (unsaved) {
        status = "unsaved";
        message = unsaved;
    }
    const label = {
        saved: "Saved",
        saving: "Saving…",
        unsaved: "Unsaved",
        invalid: "Invalid",
        error: "Error"
    } [status];
    indicator.dataset.saveState = status;
    indicator.querySelector("span").textContent = label;
    message ||= label;
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

/** Reflect loaded native disclosure states in the optional bulk control. */
function syncBlockToggle() {
    const button = document.querySelector("[data-toggle-blocks]");
    if (!button) return;
    const blocks = document.querySelectorAll("details.subtitle-block");
    const expanded = Array.from(blocks).some(block => block.open);
    let label = "Expand all blocks";
    if (expanded) {
        label = "Collapse all blocks";
        document.querySelector("#workspace").removeAttribute("data-loading-paused");
    }
    button.setAttribute("aria-expanded", String(expanded));
    button.setAttribute("aria-label", label);
    button.title = label;
}

document.addEventListener("click", event => {
    if (!event.target.closest("[data-toggle-blocks]")) return;
    const expand = !document.querySelector("details.subtitle-block[open]");
    document.querySelector("#workspace").toggleAttribute("data-loading-paused",
        !expand);
    for (const block of document.querySelectorAll("details.subtitle-block")) {
        block.open = expand;
    }
    syncBlockToggle();
});
// Native toggle does not bubble; capture also handles individual summary clicks.
document.addEventListener("toggle", event => {
    if (event.target.matches("details.subtitle-block")) syncBlockToggle();
}, true);

// Enable the bulk control once per document; CSS follows the native disclosure states.
document.documentElement.classList.add("has-block-controls");
document.addEventListener("htmx:load", syncBlockToggle);
document.addEventListener("htmx:historyRestore", syncBlockToggle);
syncBlockToggle();

// Leave the native search submit visible when HTMX is unavailable.
if (window.htmx) document.documentElement.classList.add("has-live-search");
