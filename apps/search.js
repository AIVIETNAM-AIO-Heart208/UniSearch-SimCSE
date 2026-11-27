() => {
    document.documentElement.lang = "vi";
    const root = document.getElementById("regulations");
    function bindSearch({field, selector, button, cards, status, feedback, stateKey, examples}) {
        const question = root.querySelector(field);
        const scopePicker = root.querySelector(selector);
        const submit = root.querySelector(button);
        const results = root.querySelector(cards);
        const progress = root.querySelector(status);
        const note = root.querySelector(feedback);
        const action = submit.textContent.trim();
        const scope = () => scopePicker.querySelector("input:checked")?.value;
        let submitted = null;

        function update() {
            const query = question.value.trim();
            const selection = scope();
            const response = results.querySelector("[data-query]");
            const responseScope = response?.closest("[data-scope]")?.dataset.scope;
            let state = "ready";
            let message = "";
            if (submitted && (submitted.query !== query || submitted.scope !== selection)) {
                state = "draft";
            } else if (progress.querySelector(".error")) {
                state = "error";
                message = `Chưa nhận được kết quả. Nhấn ${action} để thử lại.`;
            } else if (progress.querySelector(".pending")) {
                state = "loading";
                message = "Đang tra cứu…";
            } else if (response && (response.dataset.query !== query || responseScope !== selection)) {
                state = "draft";
            }
            if (state === "draft") {
                const changed = (submitted && submitted.scope !== selection) || (response && responseScope !== selection);
                const reason = changed ? "Lựa chọn đã thay đổi." : "Câu hỏi đã thay đổi.";
                message = query ? `${reason} Nhấn ${action} để xem kết quả mới.` : "Nhập câu hỏi mới để tra cứu.";
            }
            if (root.dataset[stateKey] !== state) root.dataset[stateKey] = state;
            if (note.textContent !== message) note.textContent = message;
        }

        function record(value) {
            submitted = {query: value.trim(), scope: scope()};
        }
        question.addEventListener("input", update);
        scopePicker.addEventListener("change", update);
        question.addEventListener("keydown", event => {
            if (event.key === "Enter" && !event.shiftKey && !event.isComposing) record(question.value);
        }, true);
        submit.addEventListener("click", () => record(question.value), true);
        if (examples) root.querySelector(examples).addEventListener("click", event => {
            const sample = event.target.closest("button");
            if (sample) record(sample.textContent);
        }, true);

        const observer = new MutationObserver(update);
        const options = {subtree: true, childList: true, characterData: true, attributes: true,
            attributeFilter: ["class", "data-query", "data-scope"]};
        observer.observe(progress, options);
        if (progress !== results) observer.observe(results, options);
        update();
    }

    root.querySelector("#search-status").setAttribute("role", "status");
    bindSearch({field: "#question textarea", selector: "#hcmus-cohort", button: "#search-button",
        cards: "#ranked-tab", status: "#search-status", feedback: "#search-feedback",
        stateKey: "searchState", examples: "#sample-questions"});
    if (root.querySelector("#d1-results")) {
        bindSearch({field: "#d1-question textarea", selector: "#uit-track", button: "#d1-submit",
            cards: "#d1-results", status: "#d1-results", feedback: "#d1-feedback", stateKey: "d1State"});
    }

    root.addEventListener("keydown", event => {
        const tab = event.target.closest('[role="tab"]');
        if (!tab || event.altKey || event.ctrlKey || event.metaKey) return;
        const tabs = [...tab.closest('[role="tablist"]').querySelectorAll('[role="tab"]:not(:disabled)')];
        const index = tabs.indexOf(tab);
        let next;
        switch (event.key) {
            case "ArrowRight": next = (index + 1) % tabs.length; break;
            case "ArrowLeft": next = (index + tabs.length - 1) % tabs.length; break;
            case "Home": next = 0; break;
            case "End": next = tabs.length - 1; break;
            default: return;
        }
        event.preventDefault();
        tabs[next].focus();
        tabs[next].click();
    });

}
