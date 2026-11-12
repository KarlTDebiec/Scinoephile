/** @file Appearance controls, blur saves, and concern actions for the OCR editor. */

/** Keep size-map pixels at the display's physical pixel size as zoom or DPI changes. */
function syncOcrDevicePixels() {
    const ratio = window.devicePixelRatio;
    document.documentElement.style.setProperty("--ocr-device-pixel-ratio", ratio);
    window.matchMedia(`(resolution: ${ratio}dppx)`).addEventListener("change",
        syncOcrDevicePixels, {
            once: true
        });
}

syncOcrDevicePixels();

/** Restore display preferences when the toolbar is rendered or replaced. */
function syncOcrAppearance() {
    const controls = document.querySelector("[data-ocr-appearance-controls]");
    if (!controls) return;
    const style = document.documentElement.style;
    for (const input of controls.querySelectorAll("[data-ocr-appearance]")) {
        const property = input.dataset.ocrAppearance;
        let value = style.getPropertyValue(property);
        if (!value) {
            try {
                value = localStorage.getItem(input.dataset.ocrAppearanceKey);
            } catch {
                // The current page can still keep preferences without browser storage.
            }
        }
        input.value = value || input.defaultValue;
        if (!input.validity.valid) input.value = input.defaultValue;
        style.setProperty(property, input.value);
    }
    controls.hidden = false;
}

syncOcrAppearance();
document.addEventListener("htmx:load", event => {
    if (event.detail.elt.id === "workspace") syncOcrAppearance();
});
document.addEventListener("htmx:historyRestore", syncOcrAppearance);
document.addEventListener("input", event => {
    const input = event.target;
    if (!input.matches("[data-ocr-appearance]") || !input.validity.valid)
        return;
    const property = input.dataset.ocrAppearance;
    document.documentElement.style.setProperty(property, input.value);
    try {
        localStorage.setItem(input.dataset.ocrAppearanceKey, input.value);
    } catch {
        // The live preview also works without browser storage.
    }
});
document.addEventListener("focusout", event => {
    const input = event.target;
    if (input.matches("[data-ocr-appearance]") && !input.validity.valid) {
        syncOcrAppearance();
    }
});

/** @type {WeakMap<HTMLFormElement, {sent: string|null, pending: boolean, error: string}>} */
const ocrSaves = new WeakMap();
/**
 * Get the save state for an OCR text form.
 * @param {HTMLFormElement} form - OCR text form.
 * @returns {{sent: string|null, pending: boolean, error: string}} Current request state.
 */
function ocrSaveState(form) {
    if (!ocrSaves.has(form)) {
        ocrSaves.set(form, {
            sent: null,
            pending: false,
            error: ""
        });
    }
    return ocrSaves.get(form);
}

/**
 * Find unsaved text, including text currently being sent.
 * @param {HTMLFormElement} form - OCR text form.
 * @returns {boolean} Whether leaving could lose text.
 */
function hasOcrDraft(form) {
    const input = form.elements.namedItem("text");
    return ocrSaveState(form).sent !== null || input.value !== input.defaultValue;
}

/** @returns {boolean} Whether a subtitle has a draft or pending validation action. */
function hasOcrDrafts() {
    return Array.from(document.querySelectorAll("[data-ocr-text]")).some(form =>
        hasOcrDraft(form) || form.elements.namedItem("text").readOnly
    );
}

/**
 * Reflect OCR autosave state using the shared save indicator.
 * @param {HTMLFormElement} form - OCR text form.
 */
function syncOcrSave(form) {
    const state = ocrSaveState(form);
    const busy = state.sent !== null;
    let status = "saved";
    let message = "Saved";
    if (state.error) {
        status = "error";
        message = state.error;
    } else if (busy) {
        status = "saving";
        message = "Saving…";
    } else if (hasOcrDraft(form)) {
        status = "unsaved";
        message = "Leave the field to save.";
    }
    const row = form.closest(".ocr-row");
    showEditorSaveStatus(row.querySelector(".save-status"), status, message, busy);
}

/**
 * Submit changed text, or remember to save again after an active request.
 * @param {HTMLFormElement} form - OCR text form.
 */
function requestOcrSave(form) {
    if (!hasOcrDraft(form)) return;
    const state = ocrSaveState(form);
    if (state.sent !== null) {
        state.pending = true;
        return;
    }
    form.requestSubmit();
}

/**
 * Enable shared save indicators on native forms enhanced by HTMX.
 * @param {Document|Element} root - Document or newly loaded fragment.
 */
function enhanceOcrForms(root) {
    for (const form of root.querySelectorAll("[data-ocr-text]")) {
        form.closest(".ocr-row").classList.add("is-enhanced");
        syncOcrSave(form);
    }
}

/**
 * Apply a fresh row version if it preserves the text the user is editing.
 * @param {HTMLFormElement} form - OCR text form.
 * @param {HTMLElement} result - Updated validation fragment for the row.
 * @param {boolean} replaceText - Whether the saved text can replace the input value.
 */
function applyOcrResult(form, result, replaceText) {
    const input = form.elements.namedItem("text");
    const saved = result.dataset.text;
    if (replaceText) input.value = saved;
    input.defaultValue = saved;
    form.elements.namedItem("version").value = result.dataset.version;
}

/**
 * Remove a card outside the active filter when its text is safe to leave.
 * @param {HTMLFormElement} form - OCR text form.
 */
function removeHiddenOcrRow(form) {
    const row = form.closest(".ocr-row");
    const result = row.querySelector(".ocr-validation");
    if (result.dataset.visible !== "false" || hasOcrDraft(form) ||
        form.elements.namedItem("text").matches(":focus")) return;
    const block = row.closest(".subtitle-block");
    row.remove();
    if (block && !block.querySelector(".ocr-row")) {
        block.remove();
        syncBlockToggle();
    }
}

/**
 * Apply the saved version without discarding edits made during a request.
 * @param {HTMLFormElement} form - OCR text form.
 * @param {XMLHttpRequest} xhr - Completed HTMX request.
 * @param {boolean} action - Whether the request resolved a validation concern.
 */
function finishOcrRequest(form, xhr, action) {
    const input = form.elements.namedItem("text");
    const state = ocrSaveState(form);
    const success = xhr.status >= 200 && xhr.status < 300;
    const refreshed = success || (action && xhr.status === 409);

    if (action) {
        input.readOnly = false;
        if (!success && xhr.status !== 409) {
            document.querySelector("#messages").textContent =
                "The validation action failed. Check the row and try again.";
        }
    }
    if (refreshed) {
        const result = form.closest(".ocr-row").querySelector(".ocr-validation");
        applyOcrResult(form, result, action || input.value === state.sent);
    } else if (!action) {
        state.error = "Text could not be saved. Retry or reload the subtitle.";
    }
    const retry = state.pending;
    state.sent = null;
    state.pending = false;
    syncOcrSave(form);
    if (refreshed) {
        removeHiddenOcrRow(form);
        if (retry && form.isConnected) requestOcrSave(form);
    }
}

/**
 * Protect drafts when Back or Forward would leave a filter or block view.
 * @param {string} message - Guidance to show when a draft blocks traversal.
 */
function guardOcrHistory(message) {
    let position = history.state?.ocrPosition ?? 0;
    const markPosition = () => history.replaceState({
        ...history.state,
        ocrPosition: position
    }, "");
    markPosition();
    // HTMX overwrites the old entry's state before writing the new entry.
    document.addEventListener("htmx:beforeHistoryUpdate", markPosition);
    document.addEventListener("htmx:pushedIntoHistory", () => {
        position++;
        markPosition();
    });
    document.addEventListener("htmx:replacedInHistory", markPosition);
    window.addEventListener("popstate", event => {
        const destination = event.state?.ocrPosition;
        if (!Number.isInteger(destination)) return;
        event.stopImmediatePropagation();
        if (destination === position) return;
        if (hasOcrDrafts()) {
            history.go(position - destination);
            document.querySelector("#messages").textContent = message;
        } else {
            window.location.reload();
        }
    }, {
        capture: true
    });
}

if (window.htmx) {
    const draftMessage = "Wait for subtitle text to save, then try again.";
    guardEditorNavigation(hasOcrDrafts, draftMessage);
    guardOcrHistory(draftMessage);
    enhanceOcrForms(document);
    document.addEventListener("htmx:load", event => enhanceOcrForms(event.detail.elt));
    document.addEventListener("htmx:configRequest", event => {
        if (!event.detail.elt.matches("[data-ocr-text], [data-ocr-action]"))
            return;
        event.detail.parameters.loaded_rows = Array.from(
            document.querySelectorAll(".ocr-row"),
            row => row.id.slice("subtitle-".length)
        ).join(",");
        event.detail.parameters.pager_has_more = String(
            document.querySelector("#load-more").hasAttribute("hx-get")
        );
    });
    document.addEventListener("htmx:afterSwap", () => {
        for (const result of document.querySelectorAll("[data-ocr-related]")) {
            result.removeAttribute("data-ocr-related");
            const form = result.closest(".ocr-row").querySelector(
                "[data-ocr-text]");
            const draft = hasOcrDraft(form);
            const input = form.elements.namedItem("text");
            if (!draft || result.dataset.text === input.defaultValue) {
                applyOcrResult(form, result, !draft);
            }
            removeHiddenOcrRow(form);
        }
    });
    document.addEventListener("input", event => {
        const form = event.target.closest("[data-ocr-text]");
        if (!form) return;
        ocrSaveState(form).error = "";
        syncOcrSave(form);
    });
    document.addEventListener("focusout", event => {
        const form = event.target.closest("[data-ocr-text]");
        if (!form || !event.target.matches("textarea")) return;
        if (hasOcrDraft(form)) {
            requestOcrSave(form);
        } else {
            const result = form.closest(".ocr-row").querySelector(
                ".ocr-validation");
            applyOcrResult(form, result, true);
            removeHiddenOcrRow(form);
        }
    });
    document.addEventListener("htmx:confirm", event => {
        const action = event.detail.elt.closest("[data-ocr-action]");
        const form = action?.closest(".ocr-row").querySelector(
            "[data-ocr-text]");
        if (!form || !hasOcrDraft(form)) return;
        event.preventDefault();
        document.querySelector("#messages").textContent =
            "Wait for subtitle text to save, then check the concern before approving it.";
    });
    window.addEventListener("beforeunload", event => {
        if (hasOcrDrafts()) event.preventDefault();
    });
    document.addEventListener("htmx:beforeRequest", event => {
        const requestForm = event.detail.elt;
        const action = requestForm.matches("[data-ocr-action]");
        if (!action && !requestForm.matches("[data-ocr-text]")) return;
        const form = requestForm.closest(".ocr-row").querySelector(
            "[data-ocr-text]");
        const input = form.elements.namedItem("text");
        if (action && hasOcrDraft(form)) {
            event.preventDefault();
            return;
        }
        if (action) {
            input.readOnly = true;
        } else {
            const state = ocrSaveState(form);
            state.sent = input.value;
            state.error = "";
            syncOcrSave(form);
        }

        // The concern form may have been removed by the time HTMX finishes.
        const xhr = event.detail.xhr;
        xhr.addEventListener("loadend", () => finishOcrRequest(form, xhr,
            action), {
            once: true
        });
    });
}
