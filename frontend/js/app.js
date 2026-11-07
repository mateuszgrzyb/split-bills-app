import { getApiHealth } from "./api.js";

const apiStatus = document.querySelector("#api-status");
const dialog = document.querySelector("#expense-dialog");
const form = document.querySelector("#expense-form");
const expenseList = document.querySelector("#expense-list");

try {
  const health = await getApiHealth();
  apiStatus.classList.add("connected");
  apiStatus.innerHTML = `<i></i> API: ${health.status}`;
} catch {
  apiStatus.classList.add("disconnected");
  apiStatus.innerHTML = "<i></i> API niedostępne";
}

document.querySelector("#open-expense").addEventListener("click", () => dialog.showModal());
document.querySelector("#close-expense").addEventListener("click", () => dialog.close());
document.querySelector("#cancel-expense").addEventListener("click", () => dialog.close());

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const data = new FormData(form);
  const description = String(data.get("description")).trim();
  const amount = Number(data.get("amount"));
  if (!description || !Number.isFinite(amount) || amount <= 0) return;

  const row = document.createElement("div");
  row.className = "expense-row new-expense-row";
  const icon = document.createElement("span");
  icon.className = "expense-icon groceries";
  icon.textContent = "＋";
  const info = document.createElement("span");
  info.className = "expense-info";
  const title = document.createElement("strong");
  title.textContent = description;
  const meta = document.createElement("small");
  meta.textContent = "Mateusz · przed chwilą · podgląd lokalny";
  info.append(title, meta);
  const share = document.createElement("span");
  share.className = "expense-share";
  share.textContent = "Do podziału";
  const value = document.createElement("strong");
  value.className = "expense-amount";
  value.textContent = `${amount.toLocaleString("pl-PL", { minimumFractionDigits: 2 })} zł`;
  row.append(icon, info, share, value);
  expenseList.prepend(row);
  form.reset();
  dialog.close();
});

document.querySelector("#settle-button").addEventListener("click", (event) => {
  event.currentTarget.textContent = "Podgląd: rozliczenie zapisze się po dodaniu API";
});
