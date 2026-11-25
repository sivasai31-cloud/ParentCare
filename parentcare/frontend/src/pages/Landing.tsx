import React from 'react';
import { Link } from 'react-router-dom';
import { Activity, CalendarDays, FileHeart, HeartHandshake, Pill, ShieldCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const features = [
  { icon: Pill, title: 'Medicine records', text: 'Keep medication names, instructions, and status organized.' },
  { icon: CalendarDays, title: 'Appointments', text: 'Track upcoming visits and keep appointment details together.' },
  { icon: FileHeart, title: 'Health records', text: 'Store reports securely and access them through your account.' },
  { icon: Activity, title: 'Health readings', text: 'Record family-entered readings and review their history.' },
];

export const Landing: React.FC = () => {
  const { user } = useAuth();

  return (
    <main className="landing-page">
      <header className="landing-header">
        <Link to="/" className="landing-brand" aria-label="ParentCare home">
          <HeartHandshake size={25} />
          <span>ParentCare</span>
        </Link>
        <nav aria-label="Account navigation">
          {user ? (
            <Link to="/dashboard" className="btn-primary">Open care dashboard</Link>
          ) : (
            <>
              <Link to="/login" className="landing-login-link">Sign in</Link>
              <Link to="/register" className="btn-primary">Create account</Link>
            </>
          )}
        </nav>
      </header>

      <section className="landing-hero">
        <div className="landing-hero-copy">
          <span className="landing-eyebrow"><ShieldCheck size={16} /> Family care, thoughtfully organized</span>
          <h1>Make caring for your parents feel a little more manageable.</h1>
          <p>Keep family health details, medicines, appointments, and emergency contacts together in one private workspace.</p>
          <div className="landing-hero-actions">
            <Link to={user ? '/dashboard' : '/register'} className="btn-primary">
              {user ? 'Open care dashboard' : 'Get started'}
            </Link>
            <Link to="/login" className="landing-secondary-link">I already have an account</Link>
          </div>
          <p className="landing-disclaimer">ParentCare helps organize information. It does not provide medical advice or contact emergency services.</p>
        </div>
        <div className="landing-care-card" aria-label="ParentCare helps families coordinate care">
          <div className="landing-care-icon"><HeartHandshake size={34} /></div>
          <h2>One place for the details that matter.</h2>
          <p>Build a clearer picture of care by keeping family-entered information organized and accessible.</p>
          <div className="landing-care-rule" />
          <span>Designed for families and caregivers</span>
        </div>
      </section>

      <section className="landing-features" aria-labelledby="landing-features-heading">
        <div>
          <span className="landing-eyebrow">A calmer way to coordinate</span>
          <h2 id="landing-features-heading">The essentials, together.</h2>
        </div>
        <div className="landing-feature-grid">
          {features.map(({ icon: Icon, title, text }) => (
            <article key={title} className="landing-feature-card">
              <span><Icon size={21} aria-hidden="true" /></span>
              <h3>{title}</h3>
              <p>{text}</p>
            </article>
          ))}
        </div>
      </section>

      <footer className="landing-footer">
        <span>ParentCare · Family healthcare coordination</span>
        <span>For urgent medical concerns, contact a healthcare professional or local emergency service.</span>
      </footer>
    </main>
  );
};
