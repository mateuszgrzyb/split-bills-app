import { useState } from "react";
import { Link } from "react-router-dom";
import {
  LayoutDashboard,
  Users,
  Receipt,
  Settings,
  LogOut,
  Plus,
  ArrowUpRight,
  ArrowDownLeft,
  X
} from "lucide-react";

const initialExpenses = [
  { id: 1, title: "Dinner at restaurant", group: "Kraków Trip", amount: 120, paidBy: "John", date: "Nov 06" },
  { id: 2, title: "Apartment booking", group: "Kraków Trip", amount: 360, paidBy: "Sarah", date: "Nov 05" },
  { id: 3, title: "Groceries", group: "Apartment", amount: 85, paidBy: "You", date: "Nov 04" },
];

export default function DashboardPage() {
  const [expenses, setExpenses] = useState(initialExpenses);
  const [modalOpen, setModalOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [amount, setAmount] = useState("");

  const total = expenses.reduce((sum, expense) => sum + expense.amount, 0);

  function addExpense(e) {
    e.preventDefault();

    if (!title || Number(amount) <= 0) return;

    setExpenses([
      {
        id: Date.now(),
        title,
        group: "Kraków Trip",
        amount: Number(amount),
        paidBy: "You",
        date: "Today",
      },
      ...expenses,
    ]);

    setTitle("");
    setAmount("");
    setModalOpen(false);
  }

  return (
    <div className="dashboard-layout">
      <aside className="sidebar">
        <Link to="/" className="logo">split-bills</Link>

        <span className="sidebar-label">MENU</span>

        <a className="sidebar-link active"><LayoutDashboard /> Overview</a>
        <a className="sidebar-link"><Users /> Groups</a>
        <a className="sidebar-link"><Receipt /> Expenses</a>

        <div className="sidebar-bottom">
          <a className="sidebar-link"><Settings /> Settings</a>
          <Link to="/" className="sidebar-link"><LogOut /> Log out</Link>
        </div>
      </aside>

      <main className="dashboard-main">
        <header className="dashboard-header">
          <div>
            <span className="muted">MONDAY, NOVEMBER 7, 2026</span>
            <h1>Good morning, John 👋</h1>
            <p>Here's what's happening with your expenses.</p>
          </div>

          <button className="button" onClick={() => setModalOpen(true)}>
            <Plus size={18} /> Add expense
          </button>
        </header>

        <section className="stats-grid">
          <StatCard
            title="Total expenses"
            value={`€${total.toFixed(2)}`}
            icon={<Receipt />}
          />
          <StatCard
            title="You are owed"
            value="€125.00"
            icon={<ArrowDownLeft />}
            positive
          />
          <StatCard
            title="You owe"
            value="€45.00"
            icon={<ArrowUpRight />}
          />
        </section>

        <section className="dashboard-content">
          <div className="panel expenses-panel">
            <div className="panel-header">
              <div>
                <h2>Recent expenses</h2>
                <p>Your latest shared transactions</p>
              </div>
              <button className="text-button">View all</button>
            </div>

            <div className="expense-list">
              {expenses.map((expense) => (
                <div className="expense-item" key={expense.id}>
                  <div className="expense-icon">
                    <Receipt />
                  </div>

                  <div className="expense-details">
                    <strong>{expense.title}</strong>
                    <span>{expense.group} · Paid by {expense.paidBy}</span>
                  </div>

                  <div className="expense-amount">
                    <strong>€{expense.amount.toFixed(2)}</strong>
                    <span>{expense.date}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="panel groups-panel">
            <div className="panel-header">
              <div>
                <h2>Your groups</h2>
                <p>Shared spaces</p>
              </div>
              <button className="text-button">See all</button>
            </div>

            <Group name="Kraków Trip" members="4 members" amount="€480.00" />
            <Group name="Apartment" members="3 members" amount="€215.00" />

            <button className="create-group">
              <Plus size={16} /> Create new group
            </button>
          </div>
        </section>
      </main>

      {modalOpen && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="panel-header">
              <h2>Add expense</h2>
              <button onClick={() => setModalOpen(false)}>
                <X />
              </button>
            </div>

            <form onSubmit={addExpense}>
              <label>Expense name</label>
              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Dinner"
                required
              />

              <label>Amount (€)</label>
              <input
                type="number"
                min="0.01"
                step="0.01"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="0.00"
                required
              />

              <button className="button full-width" type="submit">
                Save expense
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ title, value, icon, positive }) {
  return (
    <div className="stat-card">
      <div className="stat-top">
        <span>{title}</span>
        <div className="stat-icon">{icon}</div>
      </div>
      <h2 className={positive ? "positive" : ""}>{value}</h2>
    </div>
  );
}

function Group({ name, members, amount }) {
  return (
    <div className="group-item">
      <div className="group-avatar"><Users /></div>
      <div>
        <strong>{name}</strong>
        <span>{members}</span>
      </div>
      <strong>{amount}</strong>
    </div>
  );
}