() => {
    document.documentElement.lang = "vi";
    const root = document.getElementById("regulations");
    const question = root.querySelector("#question textarea");
    const results = root.querySelector("#search-results");
    const status = root.querySelector("#search-status");
    const feedback = root.querySelector("#search-feedback");
    status.setAttribute("role", "status");

    const messages = {
        draft: "Câu hỏi đã thay đổi. Nhấn Tra cứu để xem kết quả mới.",
        loading: "Đang tra cứu…",
        error: "Chưa nhận được kết quả. Nhấn Tra cứu để thử lại.",
        ready: ""
    };
    let submitted = null;

    function update() {
        const current = question.value.trim();
        const response = results.querySelector("#ranked-tab [data-query]");
        let state = "ready";
        if (submitted !== null && submitted !== current) {
            state = "draft";
        } else if (status.querySelector(".error")) {
            state = "error";
        } else if (status.querySelector(".pending")) {
            state = "loading";
        } else if (response && response.dataset.query !== current) {
            state = "draft";
        }
        root.dataset.searchState = state;
        const message = state === "draft" && !current ? "Nhập câu hỏi mới để tra cứu." : messages[state];
        if (feedback.textContent !== message) feedback.textContent = message;
    }

    root.addEventListener("input", event => {
        if (event.target === question) update();
    });
    root.addEventListener("keydown", event => {
        if (event.target === question && event.key === "Enter" && !event.shiftKey && !event.isComposing) {
            submitted = question.value.trim();
        }
    }, true);
    root.addEventListener("click", event => {
        const button = event.target.closest("button");
        if (button?.id === "search-button") submitted = question.value.trim();
        if (button?.closest("#sample-questions")) submitted = button.textContent.trim();
    }, true);

    results.addEventListener("keydown", event => {
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

    // Gradio reports transport failures on its output component, even when the server was never reached.
    const observer = new MutationObserver(update);
    const options = {subtree: true, childList: true, characterData: true, attributes: true, attributeFilter: ["class", "data-query"]};
    observer.observe(status, options);
    observer.observe(results, options);
    update();
}
