const uploadBtn = document.getElementById("upload-btn");
const datafileInput = document.getElementById("datafile");
const uploadStatus = document.getElementById("upload-status");
const previewSection = document.getElementById("preview-section");
const previewTable = document.getElementById("preview-table");
const chatSection = document.getElementById("chat-section");
const chatLog = document.getElementById("chat-log");
const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");
const resetBtn = document.getElementById("reset-btn");

uploadBtn.addEventListener("click", async () => {
  const file = datafileInput.files[0];
  if (!file) {
    uploadStatus.textContent = "Please choose a file first.";
    return;
  }

  const formData = new FormData();
  formData.append("datafile", file);

  uploadStatus.textContent = "Uploading...";

  try {
    const res = await fetch("/upload", { method: "POST", body: formData });
    const data = await res.json();

    if (!res.ok) {
      uploadStatus.textContent = data.error || "Upload failed";
      return;
    }

    uploadStatus.textContent = data.message;
    previewTable.innerHTML = data.preview;
    previewSection.classList.remove("hidden");
    chatSection.classList.remove("hidden");
    chatLog.innerHTML = "";
  } catch (err) {
    uploadStatus.textContent = "Something went wrong uploading the file.";
  }
});

function appendMessage(role, text, tableHtml) {
  const msg = document.createElement("div");
  msg.className = `msg ${role}`;
  msg.innerHTML = `<strong>${role === "user" ? "You" : "DataChat AI"}:</strong> <span>${text}</span>`;
  chatLog.appendChild(msg);

  if (tableHtml) {
    const tableWrap = document.createElement("div");
    tableWrap.className = "msg-table";
    tableWrap.innerHTML = tableHtml;
    chatLog.appendChild(tableWrap);
  }

  chatLog.scrollTop = chatLog.scrollHeight;
}

async function sendQuestion() {
  const question = chatInput.value.trim();
  if (!question) return;

  appendMessage("user", question, null);
  chatInput.value = "";

  const thinking = document.createElement("div");
  thinking.className = "msg ai thinking";
  thinking.textContent = "DataChat AI is thinking...";
  chatLog.appendChild(thinking);
  chatLog.scrollTop = chatLog.scrollHeight;

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();
    thinking.remove();

    if (!res.ok) {
      appendMessage("ai", data.error || "Something went wrong.", null);
      return;
    }

    appendMessage("ai", data.answer, data.table);
  } catch (err) {
    thinking.remove();
    appendMessage("ai", "Something went wrong reaching the server.", null);
  }
}

sendBtn.addEventListener("click", sendQuestion);
chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendQuestion();
});

resetBtn.addEventListener("click", async () => {
  await fetch("/reset", { method: "POST" });
  chatLog.innerHTML = "";
  previewSection.classList.add("hidden");
  chatSection.classList.add("hidden");
  uploadStatus.textContent = "";
  datafileInput.value = "";
});
