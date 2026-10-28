/** @file Draft presentation, validated HTMX autosave, and bulk disclosure enhancement. */

/** @type {WeakMap<HTMLFormElement, {saved: string, sent: Object|null, inFlight: boolean, pending: boolean, error: string}>} */
const saveStates = new WeakMap();

/**
 * Synchronize one editable subtitle without saving or replacing other drafts.
 * @param {HTMLTextAreaElement} input - Proofread text with its original in data-original.
 */
function syncProofread(input) {
    const normalize = value => value.replace(/\r\n?/g, "\n");
    const changed = normalize(input.value) !== normalize(input.dataset.original);
    const preview = input.closest(".inline-proofread");
    preview.classList.toggle(
        "is-dirty", normalize(input.value) !== normalize(preview.querySelector("pre").textContent)
    );
    const status = input.form.querySelector("[data-proofreading-status]");
    status.dataset.proofreadingStatus = "unchanged";
    if (changed) status.dataset.proofreadingStatus = "changed";
    for (const field of input.form.querySelectorAll("[data-revision-note]")) {
        field.hidden = !changed;
    }
    input.form.classList.add("is-enhanced");
    syncSaveStatus(input.form);
}

/**
 * Initialize new fragments and restored history; safe to repeat on existing forms.
 * @param {Document|Element} root - Container owning the inserted subtitle rows.
 */
function syncReviewFields(root) {
    syncBlockToggle();
    for (const input of root.querySelectorAll("textarea[data-original]")) {
        syncProofread(input);
    }
}

document.addEventListener("input", event => {
    const form = event.target.closest(".audit-row form");
    if (!form) return;
    const state = getSaveState(form);
    state.error = "";
    state.pending = false;
    if (event.target.matches("textarea[data-original]")) syncProofread(event.target);
    else syncSaveStatus(form);
});
// Keep the ordinary search submit available until HTMX has initialized.
document.addEventListener("htmx:load", event => {
    document.documentElement.classList.add("has-live-search");
    syncReviewFields(event.detail.elt);
});
document.addEventListener("htmx:historyRestore", () => syncReviewFields(document));
syncReviewFields(document);

/** Reflect loaded native disclosure states in the optional bulk control. */
function syncBlockToggle() {
    const button = document.querySelector("[data-toggle-blocks]");
    if (!button) return;
    const blocks = document.querySelectorAll("details.audit-block");
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
    const expand = !document.querySelector("details.audit-block[open]");
    document.querySelector("#workspace").toggleAttribute("data-loading-paused", !expand);
    for (const block of document.querySelectorAll("details.audit-block")) {
        block.open = expand;
    }
    syncBlockToggle();
});
// Native toggle does not bubble; capture also handles individual summary clicks.
document.addEventListener("toggle", event => {
    if (event.target.matches("details.audit-block")) syncBlockToggle();
}, true);

// Enable the bulk control once per document; CSS follows the native disclosure states.
document.documentElement.classList.add("has-block-controls");

/**
 * Read only persisted editable fields; ignore the CSRF token and version.
 * @param {HTMLFormElement} form - Subtitle edit form.
 * @returns {Object} Canonical field values used to distinguish newer drafts.
 */
function reviewValues(form) {
    const values = {};
    for (const name of ["reviewed", "review_note", "notes", "finding"]) {
        values[name] = form.elements.namedItem(name).value.replace(/\r\n?/g, "\n");
    }
    values.verified = form.elements.namedItem("verified").checked;
    return values;
}

/**
 * Retain request state without keeping detached forms alive.
 * @param {HTMLFormElement} form - Subtitle edit form.
 * @returns {Object} Saved baseline and in-flight request state.
 */
function getSaveState(form) {
    if (!saveStates.has(form)) {
        saveStates.set(form, {
            saved: JSON.stringify(reviewValues(form)), sent: null,
            inFlight: false, pending: false, error: ""
        });
    }
    return saveStates.get(form);
}

/**
 * Detect drafts that workspace navigation must preserve.
 * @returns {boolean} Whether a subtitle has unsaved values or an active save.
 */
function hasReviewDrafts() {
    return Array.from(document.querySelectorAll(".audit-row form")).some(form => {
        const state = getSaveState(form);
        return state.inFlight || JSON.stringify(reviewValues(form)) !== state.saved;
    });
}

/**
 * Apply native constraints and accessible inline errors before any save.
 * @param {HTMLFormElement} form - Subtitle edit form.
 * @returns {string} First validation message, or an empty string when valid.
 */
function validateReviewForm(form) {
    const text = form.elements.namedItem("reviewed");
    const note = form.elements.namedItem("review_note");
    const auditNote = form.elements.namedItem("notes");
    auditNote.required = form.elements.namedItem("finding").value === "review";
    note.required = text.value !== text.dataset.original;
    let textError = "";
    if (!text.value.trim()) textError = "Proofread text is required.";
    else if (text.value.length > 1000 || text.value.includes("\n\n")) {
        textError = "Use up to 1,000 characters without blank lines.";
    }
    text.setCustomValidity(textError);
    let noteError = "";
    if (note.required && !note.value.trim()) noteError = "A note is required for changed text.";
    else if (note.value.length > 1000) noteError = "Use up to 1,000 characters for the note.";
    note.setCustomValidity(noteError);
    let auditError = "";
    if (auditNote.required && !auditNote.value.trim()) {
        auditError = "Audit notes are required when audit status is Review.";
    } else if (form.elements.namedItem("finding").value === "ok" && auditNote.value) {
        auditError = "Clear audit notes when audit status is OK.";
    }
    auditNote.setCustomValidity(auditError);
    for (const field of [text, note, auditNote]) {
        if (field.validity.valid) field.removeAttribute("aria-invalid");
        else field.setAttribute("aria-invalid", "true");
    }
    return textError || noteError || auditError;
}

/**
 * Reflect validation, request progress, or an unsaved draft in the status control.
 * @param {HTMLFormElement} form - Subtitle edit form, never replaced by autosave.
 */
function syncSaveStatus(form) {
    const button = form.querySelector(".save-status");
    if (!button) return;
    const state = getSaveState(form);
    const invalid = validateReviewForm(form);
    let status = "saved";
    let message = "Saved";
    if (state.error) { status = "error"; message = state.error; }
    else if (invalid) { status = "invalid"; message = invalid; }
    else if (state.inFlight) { status = "saving"; message = "Saving…"; }
    else if (JSON.stringify(reviewValues(form)) !== state.saved) {
        status = "unsaved"; message = "Unsaved changes — leave the field to save, or click to retry.";
    }
    button.type = "button";
    button.dataset.saveState = status;
    button.querySelector("span").textContent = {
        saved: "Saved", saving: "Saving…", unsaved: "Unsaved",
        invalid: "Invalid", error: "Error"
    }[status];
    button.title = message;
    button.setAttribute("aria-label", message);
    button.setAttribute("aria-busy", String(state.inFlight));
}

/**
 * Ask HTMX to save a valid changed form; coalesce edits during an active request.
 * @param {HTMLFormElement} form - Subtitle edit form.
 */
function requestReviewSave(form) {
    const state = getSaveState(form);
    if (state.inFlight) { state.pending = true; return; }
    if (validateReviewForm(form) || JSON.stringify(reviewValues(form)) === state.saved) {
        syncSaveStatus(form);
        return;
    }
    state.inFlight = true;
    state.error = "";
    syncSaveStatus(form);
    form.dispatchEvent(new Event("review:save", {bubbles: true}));
}

document.addEventListener("change", event => {
    const form = event.target.closest(".audit-row form");
    if (form && event.target.matches("select, input[type=checkbox]")) requestReviewSave(form);
});

document.addEventListener("htmx:beforeRequest", event => {
    const form = event.detail.elt;
    if (form.matches(".audit-block summary > a") && hasReviewDrafts()) {
        event.preventDefault();
        document.querySelector("#messages").textContent =
            "Save subtitle drafts before opening another block.";
        return;
    }
    if (!form.matches(".audit-row form")) return;
    const state = getSaveState(form);
    state.sent = reviewValues(form);
    state.inFlight = true;
    syncSaveStatus(form);
});

// A superseded preview must not overwrite either side of a newer draft's diff.
document.addEventListener("htmx:beforeSwap", event => {
    const input = event.detail.requestConfig.elt;
    if (!input.matches("textarea[data-original]")) return;
    if (input.value.replace(/\r\n?/g, "\n") !== event.detail.requestConfig.parameters.reviewed) {
        event.detail.shouldSwap = false;
    }
});

document.addEventListener("htmx:afterRequest", event => {
    const form = event.detail.elt;
    if (form.matches("textarea[data-original]")) {
        if (form.isConnected) syncProofread(form);
        return;
    }
    if (!form.matches(".audit-row form")) return;
    const state = getSaveState(form);
    const retry = state.pending;
    state.inFlight = false;
    state.pending = false;
    if (event.detail.xhr.status >= 200 && event.detail.xhr.status < 300 && state.sent) {
        state.saved = JSON.stringify(state.sent);
        // Updating defaults never replaces a focused textarea or its newer value.
        for (const name of ["reviewed", "review_note", "notes"]) {
            form.elements.namedItem(name).defaultValue = state.sent[name];
        }
        state.error = "";
    } else {
        state.error = "Not saved — click to retry. If this row changed elsewhere, reload first.";
    }
    state.sent = null;
    if (!form.isConnected) return;
    syncProofread(form.elements.namedItem("reviewed"));
    if (retry && !state.error) requestReviewSave(form);
});

// Shared proofreading decisions can update related rows; retain their active drafts.
document.addEventListener("htmx:oobBeforeSwap", event => {
    const row = event.detail.target;
    if (!row.matches(".audit-row")) return;
    const form = row.querySelector("form");
    const state = getSaveState(form);
    const signature = JSON.stringify(reviewValues(form));
    if (signature !== state.saved && signature !== JSON.stringify(state.sent)) {
        event.detail.shouldSwap = false;
        state.error = "A related subtitle changed — reload before saving this draft.";
        syncSaveStatus(form);
    }
});

// Blur commits text edits even when their change event is delayed by the browser.
document.addEventListener("focusout", event => {
    const form = event.target.closest(".audit-row form");
    if (form && event.target.matches("textarea")) requestReviewSave(form);
});
// The enhanced indicator retries drafts; clicking an already-saved check is a no-op.
document.addEventListener("click", event => {
    const button = event.target.closest(".save-status");
    if (button) requestReviewSave(button.form);
});
// Operations replace the workspace; preserve incomplete subtitle drafts.
document.addEventListener("submit", event => {
    if (!event.target.matches("#proofreading form, #auditing form, [data-verify-visible], [data-reaudit], [data-reproofread]")) return;
    if (!hasReviewDrafts()) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    const message = document.querySelector("[data-operations-message]");
    message.hidden = false;
    message.textContent = "Save subtitle drafts before running an operation.";
    if (event.target.matches("#auditing form")) {
        document.querySelector("[data-auditing-message]").textContent = message.textContent;
    }
}, true);
