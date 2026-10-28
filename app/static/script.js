const chat = document.getElementById("chat");
const form = document.getElementById("form");
const input = document.getElementById("question");
const sendBtn = document.getElementById("send");

function addMessage(text, cls) {
  const div = document.createElement("div");
  div.className = "msg " + cls;
  div.textContent = text; // textContent avoids HTML injection
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
  return div;
}

function addSources(msgEl, sources) {
  if (!sources || sources.length === 0) return;
  const details = document.createElement("details");
  details.className = "sources";
  const summary = document.createElement("summary");
  summary.textContent = `Sources (${sources.length})`;
  details.appendChild(summary);

  sources.forEach((s, i) => {
    const item = document.createElement("div");
    item.className = "source";
    const title = document.createElement("strong");
    title.textContent = `[${i + 1}] ${s.source}, page ${s.page}`;
    const snippet = document.createElement("small");
    snippet.textContent = `${s.snippet}... (match ${(s.score * 100).toFixed(0)}%)`;
    item.append(title, snippet);
    details.appendChild(item);
  });
  msgEl.appendChild(details);
}

async function ask(question) {
  addMessage(question, "user");
  const typing = addMessage("Searching the knowledge base...", "bot typing");
  sendBtn.disabled = true;
  input.disabled = true;

  try {
    const res = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();
    typing.remove();

    if (!res.ok) {
      addMessage(data.detail || "Something went wrong.", "bot error");
    } else {
      const el = addMessage(data.answer, data.grounded ? "bot" : "bot warn");
      addSources(el, data.sources);
    }
  } catch (err) {
    typing.remove();
    addMessage("Could not reach the server. Is it running?", "bot error");
  } finally {
    sendBtn.disabled = false;
    input.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const q = input.value.trim();
  if (!q) return;
  input.value = "";
  ask(q);
});

document.querySelectorAll("#examples button").forEach((btn) => {
  btn.addEventListener("click", () => ask(btn.textContent));
});
