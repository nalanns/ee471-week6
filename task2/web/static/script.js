const input = document.getElementById("image-input");
const preview = document.getElementById("preview");
const button = document.getElementById("classify-btn");
const statusEl = document.getElementById("status");
const results = document.getElementById("results");

input.addEventListener("change", () => {
  const file = input.files[0];
  results.innerHTML = "";
  statusEl.textContent = "";
  if (!file) {
    preview.hidden = true;
    button.disabled = true;
    return;
  }
  preview.src = URL.createObjectURL(file);
  preview.hidden = false;
  button.disabled = false;
});

button.addEventListener("click", async () => {
  const form = new FormData();
  form.append("image", input.files[0]);
  button.disabled = true;
  statusEl.textContent = "Classifying...";
  results.innerHTML = "";
  try {
    const resp = await fetch("/api/classify", { method: "POST", body: form });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error);
    const sorted = Object.entries(data.predictions).sort((a, b) => b[1] - a[1]);
    for (const [label, prob] of sorted) {
      const li = document.createElement("li");
      li.textContent = `${label}: ${(prob * 100).toFixed(1)}%`;
      results.appendChild(li);
    }
    statusEl.textContent = "";
  } catch (err) {
    statusEl.textContent = `Error: ${err.message}`;
  } finally {
    button.disabled = false;
  }
});