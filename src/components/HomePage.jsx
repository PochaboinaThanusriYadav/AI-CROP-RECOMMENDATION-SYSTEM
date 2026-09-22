import { ArrowUpRight, Check, ChevronRight, CloudSun, Droplets, Leaf, MapPin, ScanLine, Sprout, Tractor, Waves } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useState } from 'react'

const services = [
  { icon: ScanLine, title: 'Soil image analysis', copy: 'Understand the visual characteristics of your soil.' },
  { icon: MapPin, title: 'Location intelligence', copy: 'Bring your region and growing conditions into focus.' },
  { icon: Sprout, title: 'Crop advisory', copy: 'Move from field signals toward a considered recommendation.' },
]

const insights = [
  ['01', 'Why soil context matters', 'A practical guide to preparing a soil image for analysis.'],
  ['02', 'Reading your farm signals', 'How location and farmer knowledge strengthen an advisory.'],
  ['03', 'A more thoughtful planting plan', 'Weather and field signals organized for the next decision.'],
]

export default function HomePage() {
  const [activeSection, setActiveSection] = useState('about')
  const goToSection = (section) => {
    setActiveSection(section)
    document.getElementById(section)?.scrollIntoView({ behavior: 'smooth' })
  }

  return <main className="reference-home">
    <section className="reference-hero">
      <div className="reference-hero-image" role="img" aria-label="Green agricultural field ready for planting">
        <div className="reference-hero-nav"><Link className="reference-logo" to="/"><span><Leaf size={16} /></span> AgriVision</Link><div className="radio-inputs" role="navigation" aria-label="Home page sections">{[['about', 'About'], ['services', 'Solutions'], ['workflow', 'Workflow']].map(([section, label]) => <label className="radio" key={section}><input type="radio" name="home-section" checked={activeSection === section} onChange={() => goToSection(section)} /><span className="name">{label}</span></label>)}</div><Link className="start-analysis-button" to="/analysis" aria-label="Start analysis"><span className="start-analysis-bg" /><span className="start-analysis-wrap"><span className="start-analysis-outline" /><span className="start-analysis-content"><span className="start-analysis-label">Start analysis</span><span className="start-analysis-icon"><span /></span></span></span></Link></div>
        <div className="reference-hero-copy"><span className="reference-kicker">Connected crop advisory</span><h1>Smart agriculture<br /><em>for a stronger harvest.</em></h1><p>Bring together soil, place and farmer knowledge to make your next crop decision more informed.</p><div className="reference-hero-actions"><Link className="button2" to="/analysis">Explore the workflow</Link><Link className="learn-more" to="/about"><span className="circle" aria-hidden="true"><span className="icon arrow" /></span><span className="button-text">Learn more</span></Link></div></div>
        <div className="reference-hero-note"><span className="reference-avatar"><Sprout size={15} /></span><span><b>Built for the field</b></span></div>
      </div>
    </section>

    <section className="reference-intro" id="about"><span className="reference-kicker">About the platform</span><h2>We help farmers make more informed decisions through <em>connected agricultural signals.</em></h2><Link className="round-arrow" to="/about"><ArrowUpRight size={18} /></Link></section>

    <section className="reference-services" id="services"><div className="reference-section-heading"><div><span className="reference-kicker">What we bring together</span><h2>Solutions for agriculture</h2></div><div className="reference-heading-actions"><Link className="plant-based-button" to="/analysis"><span>Explore crops</span><Leaf className="plant-leaf plant-leaf-1" size={18} /><Leaf className="plant-leaf plant-leaf-2" size={22} /><Leaf className="plant-leaf plant-leaf-3" size={17} /><Leaf className="plant-leaf plant-leaf-4" size={25} /><Leaf className="plant-leaf plant-leaf-5" size={21} /></Link><Link className="reference-outline" to="/analysis">View workflow <ArrowUpRight size={14} /></Link></div></div><div className="service-list">{services.map(({ icon: Icon, title, copy }, index) => <Link className="service-row" to={index === 0 ? '/soil' : index === 1 ? '/location' : '/analysis'} key={title}><span className="service-icon"><Icon size={19} /></span><span className="service-number">0{index + 1}</span><span className="service-copy"><b>{title}</b><small>{copy}</small></span><ArrowUpRight className="service-arrow" size={17} /></Link>)}</div></section>

    <section className="reference-impact" id="workflow"><div className="impact-image"><div className="impact-overlay"><span className="reference-kicker">One connected view</span><h2>From soil signals<br />to planting context.</h2><div className="impact-metrics"><span><b>03</b><small>input pathways</small></span><span><b>01</b><small>future advisory</small></span></div></div></div><div className="impact-copy"><span className="reference-kicker">How it works</span><h2>Knowledge from the field, organized for the next decision.</h2><p>AgriVision gives soil images, location information and farmer-provided conditions a clear place in one workflow. It is designed to connect to Python services and real data when your backend is ready.</p><Link className="reference-dark-link" to="/analysis">Build your analysis <ArrowUpRight size={16} /></Link></div></section>

    <section className="reference-trust"><div><span className="reference-kicker">Designed with care</span><h2>A calm interface for complex field information.</h2></div><div className="trust-points"><span><Check size={16} /> No fabricated predictions</span><span><CloudSun size={16} /> Weather-ready data states</span><span><Waves size={16} /> Practical farmer inputs</span><span><Droplets size={16} /> Backend integration ready</span></div></section>

    <section className="reference-insights"><div className="reference-section-heading"><div><span className="reference-kicker">Field notes</span><h2>Latest insights & tips</h2></div><Link className="reference-outline" to="/about">See platform <ArrowUpRight size={14} /></Link></div><div className="insight-grid">{insights.map(([number, title, copy]) => <Link className="insight-card" to="/about" key={number}><span>{number}</span><div className="insight-art"><Tractor size={30} /></div><h3>{title}</h3><p>{copy}</p><ChevronRight size={17} /></Link>)}</div></section>
  </main>
}
