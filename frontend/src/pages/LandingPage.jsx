import { Link } from "react-router-dom";
import { ArrowRight, Users, Receipt, Wallet } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="landing">
      <nav className="navbar">
        <Link to="/" className="logo">split-bills</Link>

        <div className="nav-links">
          <a href="#features">Features</a>
          <Link to="/login">Sign in</Link>
          <Link to="/login" className="button">Get started</Link>
        </div>
      </nav>

      <section className="hero">
        <div className="hero-content">
          <span className="eyebrow">SPLIT SMARTER. LIVE BETTER.</span>

          <h1>
            Money between friends.
            <span> Sorted.</span>
          </h1>

          <p>
            Track shared expenses, split bills fairly and always
            know who owes whom. Less awkward conversations,
            more memorable moments.
          </p>

          <div className="hero-actions">
            <Link to="/login" className="button">
              Start splitting <ArrowRight size={18} />
            </Link>
            <a href="#features" className="secondary-link">
              Discover how it works
            </a>
          </div>
        </div>

        <div className="hero-card">
          <div className="preview-header">
            <div>
              <span className="muted">YOUR GROUP BALANCE</span>
              <h2>€240.00</h2>
            </div>
            <span className="avatar">JD</span>
          </div>

          <div className="preview-divider" />

          <div className="balance-row">
            <span>Weekend in Kraków</span>
            <strong>€180.00</strong>
          </div>
          <div className="balance-row">
            <span>Apartment expenses</span>
            <strong>€60.00</strong>
          </div>

          <div className="preview-footer">
            <span>Everything balanced.</span>
            <span>✓</span>
          </div>
        </div>
      </section>

      <section id="features" className="features">
        <div className="section-heading">
          <span className="eyebrow">MADE FOR SHARED MOMENTS</span>
          <h2>Splitting shouldn't be complicated.</h2>
        </div>

        <div className="feature-grid">
          <Feature
            icon={<Users />}
            title="Create groups"
            description="Organize expenses with friends, roommates or travel companions."
          />
          <Feature
            icon={<Receipt />}
            title="Track expenses"
            description="Keep every shared purchase in one simple overview."
          />
          <Feature
            icon={<Wallet />}
            title="Settle balances"
            description="Know exactly who owes whom and how much."
          />
        </div>
      </section>
    </div>
  );
}

function Feature({ icon, title, description }) {
  return (
    <div className="feature-card">
      <div className="feature-icon">{icon}</div>
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}