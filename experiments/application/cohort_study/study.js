"use strict";

const byId = (id) => document.getElementById(id);
const query = byId("query");
const admission = byId("admission");
const chooser = byId("cohort-panel");
const workspace = byId("workspace");
const list = byId("question-list");
const results = byId("results");
const content = byId("result-content");
const firstCohort = document.body.dataset.entry === "first";
const questions = window.studyQuestions;
let sessionYear = "";
let picker = "";
let active = null;

function normalize(text) {
    return text.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "")
        .replace(/đ/g, "d").replace(/[^a-z0-9]+/g, " ").trim();
}

const indexed = new Map(questions.map((item) => [normalize(item.question), item]));

function matchQuestion(text) {
    const normalized = normalize(text);
    if (indexed.has(normalized)) return {item: indexed.get(normalized), year: ""};
    // Accept a separately stated personal admission year. A school year or an edition stays in the question.
    const admissionWords = /^(?:em |minh |toi )?(?:thuoc |la sinh vien )?(?:k(2[1-6])|(?:nhap hoc(?: nam)?|khoa tuyen sinh(?: nam)?) (202[1-6]))$/;
    for (const [question, item] of indexed) {
        let note;
        if (normalized.startsWith(question + " ")) note = normalized.slice(question.length).trim();
        else if (normalized.endsWith(" " + question)) note = normalized.slice(0, -question.length).trim();
        else continue;
        const match = admissionWords.exec(note);
        if (match) return {item, year: match[2] || "20" + match[1]};
    }
    return null;
}

function describe(year) {
    return year === "earlier" ? "nhập học trước năm 2021" : "K" + year.slice(-2) + " (nhập học năm " + year + ")";
}

function updateSession() {
    byId("session-bar").hidden = !sessionYear;
    byId("session-cohort").textContent = sessionYear ? "Khóa trong phiên · " + describe(sessionYear) : "";
    byId("change-cohort").hidden = !sessionYear || !!picker;
    byId("restart").hidden = !sessionYear && !active && !query.value;
}

function closePicker() {
    picker = "";
    chooser.hidden = true;
    updateSession();
}

function showPicker(reason, focus = true) {
    picker = reason;
    chooser.hidden = false;
    admission.value = sessionYear;
    const alternative = byId("cohort-alternative");
    alternative.hidden = reason === "first";
    alternative.textContent = reason === "change" ? "Hủy đổi khóa" : "Xem quy định cho các khóa";
    byId("cohort-heading").textContent = reason === "needed" ? "Bạn nhập học năm nào?" : "Khóa tuyển sinh của bạn";
    byId("cohort-help").textContent = {
        first: "Chọn năm bạn bắt đầu học tại Trường để tiếp tục tra cứu.",
        needed: "Quy định áp dụng phụ thuộc vào khóa tuyển sinh. Bạn có thể đối chiếu các khóa nếu chưa rõ năm nhập học.",
        change: "Chọn năm nhập học muốn dùng cho lượt tra cứu này."
    }[reason];
    byId("confirm-cohort").textContent = reason === "first" ? "Tiếp tục" : "Xem kết quả";
    if (reason === "change") byId("confirm-cohort").textContent = "Lưu thay đổi";
    updateSession();
    if (focus) admission.focus();
}

function clearResult() {
    results.hidden = true;
    byId("no-match").hidden = true;
    list.querySelector("summary").removeAttribute("aria-describedby");
    byId("search-status").firstElementChild.textContent = "";
    content.replaceChildren();
}

function showScope(year) {
    const card = byId("scope-result").content.cloneNode(true);
    let answer = "Phạm vi áp dụng theo khóa tuyển sinh";
    if (year === "2026") {
        answer = "Quy chế 2026 áp dụng cho " + describe(year) + ".";
        card.querySelector('[data-clause="2"]').remove();
    } else if (year) {
        answer = "Với sinh viên " + describe(year) + ", Trường lựa chọn áp dụng quy định mới có lợi hơn cho người học.";
        card.querySelector('[data-clause="1"]').remove();
    }
    card.querySelector("h3").textContent = answer;
    content.replaceChildren(card);
}

function linkReviewedPages() {
    for (const link of content.querySelectorAll(".source-line a")) {
        const summary = link.closest(".topic-panel, .edition").querySelector(":scope > summary");
        // A secondary edition can append an article title after its reference.
        const reference = (summary.querySelector(".reference") || summary.firstChild).textContent.trim();
        const page = window.studyPages[reference];
        if (page) {
            link.setAttribute("href", link.getAttribute("href") + "#page=" + page);
            link.append(" (trang " + page + ")");
        }
    }
}

function display(match, general = false) {
    clearResult();
    active = match;
    closePicker();
    if (match.item.id === "personal") {
        const year = match.year || sessionYear;
        if (!year && !general) {
            showPicker("needed");
            return;
        }
        showScope(year);
    } else {
        byId("search-status").firstElementChild.textContent = match.item.warning;
        // Only verified, locally bundled regulation excerpts pass through this HTML sink.
        content.innerHTML = match.item.html;
        linkReviewedPages();
    }
    results.hidden = false;
    byId("result-heading").focus();
}

function submitQuestion() {
    if (firstCohort && !sessionYear) return;
    list.open = false;
    const match = matchQuestion(query.value);
    if (match) {
        display(match);
        return;
    }
    clearResult();
    active = null;
    closePicker();
    byId("no-match").hidden = false;
    const summary = list.querySelector("summary");
    summary.setAttribute("aria-describedby", "no-match");
    list.open = true;
    summary.focus();
}

function reset(focus) {
    sessionYear = "";
    active = null;
    query.value = "";
    list.open = false;
    clearResult();
    closePicker();
    workspace.hidden = firstCohort;
    if (firstCohort) showPicker("first", focus);
    else if (focus) query.focus();
}

for (const item of questions) {
    const row = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "question-option";
    button.textContent = item.question;
    button.addEventListener("click", () => {
        query.value = item.question;
        submitQuestion();
    });
    row.append(button);
    byId("question-options").append(row);
}

query.addEventListener("input", () => {
    active = null;
    clearResult();
    closePicker();
});
query.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
        event.preventDefault();
        byId("search-form").requestSubmit();
    }
});
byId("search-form").addEventListener("submit", (event) => {
    event.preventDefault();
    submitQuestion();
});
byId("cohort-form").addEventListener("submit", (event) => {
    event.preventDefault();
    sessionYear = admission.value;
    const reason = picker;
    closePicker();
    workspace.hidden = false;
    if (reason === "needed" || (reason === "change" && active?.item.id === "personal")) display(active);
    else query.focus();
});
byId("cohort-alternative").addEventListener("click", () => {
    if (picker === "needed") display(active, true);
    else {
        closePicker();
        byId("change-cohort").focus();
    }
});
byId("change-cohort").addEventListener("click", () => showPicker("change"));
byId("restart").addEventListener("click", () => reset(true));
reset(false);
