import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft, Eye, EyeOff } from "lucide-react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const navigate = useNavigate();

  function handleSubmit(e) {
    e.preventDefault();

    if (!email || !password) return;

    // Replace with FastAPI authentication.
    navigate("/dashboard");
  }

  return (
    <div className="auth-page">
      <Link to="/" className="logo">
        split-bills
      </Link>

      <div className="auth-card">
        <Link to="/" className="back-link">
          <ArrowLeft size={16} /> Back home
        </Link>

        <span className="eyebrow">WELCOME BACK</span>
        <h1>Let's get things sorted.</h1>
        <p>Sign in to manage your shared expenses.</p>

        <form onSubmit={handleSubmit}>
          <label>Email address</label>
          <input
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <label>Password</label>
          <div className="password-input">
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? <EyeOff /> : <Eye />}
            </button>
          </div>

          <button className="button full-width" type="submit">
            Sign in
          </button>
        </form>

        <div className="auth-footer">
          New to split-bills? <a href="mailto:support@example.com">Create an account</a>
        </div>
      </div>
    </div>
  );
}