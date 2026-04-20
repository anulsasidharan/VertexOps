# VertexOps Platform - Landing Page Design & Development Prompt

## 📋 Context & Setup

**Project**: VertexOps - Enterprise-Grade AI-Powered Infrastructure Operations & DevOps Intelligence Platform

**Documentation References**:
- `@CLAUDE.md` - Core product documentation
- `@task.md` - Current task specifications
- `@.cursor/rules/*` - Development rules and guidelines
- `@docs/*.md` - Additional documentation files

---

## 🎯 Objective

Create a comprehensive, production-ready landing page for **VertexOps Platform** that serves as the primary marketing and informational hub for this enterprise-grade AI-powered infrastructure operations platform. The landing page must effectively communicate VertexOps' value proposition to DevOps Engineers, SREs, Platform Engineers, CTOs, and Infrastructure Architects.

---

## 📊 Product Overview (From Documentation Analysis)

### Platform Description
VertexOps is an enterprise-grade AI-powered infrastructure operations and DevOps intelligence platform that transforms multi-cloud chaos into clarity through intelligent automation, proactive monitoring, and cost optimization.

### Core Technology Stack
- **Cloud Infrastructure**: GCP (primary deployment - GKE, Cloud SQL PostgreSQL, Memorystore Redis, Cloud Storage, Cloud CDN)
- **AI/ML Stack**: LangGraph, GPT-4o, Gemini, Pinecone/Vertex AI Vector Search
- **Backend**: FastAPI, Celery (distributed task queue)
- **Frontend**: Next.js 14, React, Tailwind CSS
- **Multi-Cloud Support**: GCP, AWS, Azure monitoring and automation

### Design System
- **Primary Color**: #0A66C2 (LinkedIn Blue - professional, enterprise-grade)
- **Secondary Color**: #00A4BD (Teal accent)
- **Success**: #57A639 (Green)
- **Warning**: #F5C26B (Amber)
- **Error**: #E74C3C (Red)
- **Background**: #F9FAFB (Light gray)
- **Text**: #1F2937 (Dark gray)
- **Typography**: Inter (headings: Bold, body: Regular), JetBrains Mono (code)
- **UI Style**: Enterprise SaaS aesthetic, LinkedIn-inspired clean interface

### Target Audience
1. **Primary**: DevOps Engineers, Site Reliability Engineers (SREs), Platform Engineers
2. **Secondary**: CTOs, VP Engineering, Infrastructure Architects, Engineering Managers
3. **Tertiary**: Cloud Architects, Security Engineers, FinOps Teams

---

## 🎨 Content Requirements - Comprehensive Documentation Analysis

### 1. Key Features & Capabilities

#### **Core Platform Features**
1. **AI-Powered Infrastructure Intelligence**
   - Automated infrastructure topology mapping
   - Real-time resource monitoring across GCP, AWS, Azure
   - Multi-modal analysis: logs, metrics, traces, cost data
   - Anomaly detection with confidence scores

2. **Incident Detection & Auto-Remediation**
   - AI-powered root cause analysis
   - Automated detection: resource exhaustion, security vulnerabilities, configuration drift, performance degradation
   - Automated remediation workflows with approval gates
   - Timeline-based incident tracking with exact timestamps
   - Visual highlighting of problematic resources

3. **Cost Optimization Intelligence (FinOps)**
   - Idle resource detection and rightsizing suggestions
   - Reserved instance/commitment optimization
   - Multi-cloud cost comparison and savings opportunities
   - Automated cost allocation and chargeback reporting
   - AI-driven cost recommendations

4. **AI-Powered ChatOps & Runbooks**
   - Natural language infrastructure queries (RAG-powered)
   - Conversational troubleshooting assistant
   - Automated runbook execution
   - Knowledge base search across documentation, incidents, logs
   - GitOps integration for configuration management

5. **Multi-Channel Notification & Escalation**
   - SendGrid email, Slack, PagerDuty, Microsoft Teams, in-app alerts
   - Customizable notification rules and escalation workflows
   - On-call rotation management
   - SLA tracking and breach alerts

6. **Compliance & Audit Trail**
   - Complete audit log with AI agent activity and change tracking
   - Compliance reporting: SOC 2, ISO 27001, GDPR, HIPAA
   - Infrastructure-as-Code (IaC) drift detection
   - Security posture assessment
   - PDF report generation and export

7. **Enterprise Security & Access Control**
   - SSO/OAuth integration (Google, Okta, Azure AD)
   - Role-based access control (RBAC)
   - API key management
   - 2FA authentication
   - Multi-cloud account/project connection management

### 2. Value Propositions & Key Benefits

#### **Primary Value Pillars**
1. **Intelligence**: AI-driven insights that go beyond traditional monitoring
2. **Automation**: Reduce toil and manual interventions by 67% MTTR reduction
3. **Multi-Cloud**: Unified operations across GCP, AWS, and Azure
4. **Cost Efficiency**: FinOps intelligence that directly impacts bottom line (40% cost savings)
5. **Compliance**: Built-in governance and security posture management (95% automation coverage)

#### **Quantifiable ROI Metrics**
- **67% Reduction in MTTR** (Mean Time To Resolution)
- **40% Cost Savings** on infrastructure spend
- **95% Automation Coverage** of routine operations
- **$47,000+ Monthly Savings** (example customer metric)
- **847+ Resources Monitored** per deployment
- **23 Incidents Auto-Resolved** daily average

### 3. Use Cases & Industry Applications

#### **Primary Use Cases**
1. **Multi-Cloud Operations Management**
   - Unified visibility across GCP, AWS, Azure
   - Cross-cloud resource optimization
   - Standardized incident response

2. **Proactive Incident Prevention**
   - Anomaly detection before failures
   - Predictive capacity planning
   - Automated remediation

3. **FinOps & Cost Optimization**
   - Continuous cost monitoring
   - Waste identification and elimination
   - Budget forecasting and alerts

4. **Compliance Automation**
   - Continuous compliance monitoring
   - Automated audit trail generation
   - Policy-as-code enforcement

5. **Platform Engineering Enablement**
   - Self-service infrastructure insights
   - Developer experience enhancement
   - Internal platform documentation

#### **Industry Verticals**
- **Financial Services**: Compliance, security posture, uptime requirements
- **Healthcare**: HIPAA compliance, data security, infrastructure reliability
- **E-commerce**: Performance optimization, cost efficiency, scaling automation
- **SaaS Companies**: Multi-tenant infrastructure, cost allocation, reliability
- **Enterprises**: Governance, audit trails, multi-cloud management

### 4. Technical Specifications & Architecture

#### **Platform Architecture Highlights**
- **Microservices Architecture**: Containerized on GKE
- **Event-Driven**: Celery task queues for async processing
- **AI/ML Pipeline**: LangGraph orchestration, GPT-4o + Gemini models
- **Vector Search**: Pinecone/Vertex AI for semantic search
- **Real-Time Processing**: WebSocket support for live updates
- **API-First Design**: Comprehensive REST API with SDK support

#### **Integration Capabilities**
- **Cloud Providers**: Native GCP, AWS, Azure integrations
- **Infrastructure-as-Code**: Terraform, Pulumi, CloudFormation
- **CI/CD**: GitHub Actions, GitLab CI, Jenkins, CircleCI
- **Monitoring Tools**: Prometheus, Grafana, Datadog, New Relic
- **Communication**: Slack, Microsoft Teams, PagerDuty, Opsgenie
- **Version Control**: GitHub, GitLab, Bitbucket
- **Ticketing**: Jira, ServiceNow, Linear

#### **API & SDK Information**
- **REST API**: Fully documented OpenAPI/Swagger spec
- **Python SDK**: `vertexops-python` package
- **CLI Tool**: `vertexops-cli` for terminal automation
- **Webhooks**: Real-time event notifications
- **Authentication**: API keys, OAuth 2.0, service accounts

### 5. Security & Compliance Features

#### **Security Capabilities**
- **Data Encryption**: At-rest (AES-256) and in-transit (TLS 1.3)
- **Network Security**: VPC isolation, private endpoints, IP allowlisting
- **Access Control**: RBAC, SSO, MFA, service account management
- **Audit Logging**: Comprehensive activity logs with tamper-proof storage
- **Secrets Management**: Integration with GCP Secret Manager, AWS Secrets Manager, HashiCorp Vault

#### **Compliance Frameworks**
- SOC 2 Type II certified
- ISO 27001 compliant
- GDPR ready (data residency controls)
- HIPAA compliant deployments available
- PCI DSS controls for financial services

### 6. Performance Metrics & Benchmarks

- **Response Time**: <200ms average API latency
- **Uptime SLA**: 99.95% guaranteed
- **Scalability**: Supports 10,000+ monitored resources per deployment
- **Data Retention**: 90 days standard, 2 years enterprise
- **Real-Time Processing**: <5 second alert latency
- **AI Inference**: <3 second response time for ChatOps queries

---

## 🏗️ Landing Page Structure & Sitemap

### Section Breakdown (Scroll Order)

#### **Section 1: Navigation Bar** (Sticky)
- **Components**: Logo, Product nav, Docs, Pricing, About, Login, Sign Up CTA
- **Behavior**: Transparent on hero, solid background on scroll
- **Mobile**: Hamburger menu

#### **Section 2: Hero Section** (Above the fold)
- **Headline**: "AI-Powered Infrastructure Intelligence for Modern DevOps Teams"
- **Subheadline**: "Transform multi-cloud chaos into clarity with automated monitoring, intelligent incident response, and proactive cost optimization"
- **Primary CTA**: "Request Demo" (button)
- **Secondary CTA**: "View Live Demo" (link)
- **Visual**: Animated dashboard screenshot or interactive demo
- **Trust Indicators**: "Trusted by 200+ engineering teams" + logo cloud
- **Key Stats Row**: 67% MTTR Reduction | 40% Cost Savings | 95% Automation

#### **Section 3: Social Proof / Logo Cloud**
- **Content**: Customer logos (if available) or "Trusted by teams at" placeholder
- **Alternative**: Industry badges (SOC 2, ISO 27001, cloud partner badges)

#### **Section 4: Problem Statement** (Pain Points)
- **Headline**: "Infrastructure Complexity is Overwhelming Your Team"
- **3-Column Layout**:
  1. **Alert Fatigue**: "Too many alerts, not enough intelligence"
  2. **Multi-Cloud Chaos**: "Managing AWS, GCP, Azure separately is unsustainable"
  3. **Cost Overruns**: "Cloud spend is out of control with no visibility"
- **Visual**: Icons or illustrations for each pain point

#### **Section 5: Solution Overview** (Value Proposition)
- **Headline**: "One Platform to Monitor, Optimize, and Automate Your Entire Infrastructure"
- **Description**: Brief overview of how VertexOps solves the problems
- **Visual**: Platform architecture diagram or high-level feature overview
- **CTA**: "See How It Works" → scroll to next section

#### **Section 6: Core Features Showcase** (Detailed)
**Layout**: Alternating image-text sections (bento box or alternating left/right)

**Feature 1: AI-Powered Monitoring & Discovery**
- Screenshot: Topology map with real-time metrics
- Bullets: Automated discovery, multi-cloud visibility, anomaly detection
- Icon: Radar/network icon

**Feature 2: Intelligent Incident Response**
- Screenshot: Incident detail page with root cause analysis
- Bullets: Auto-remediation, approval workflows, timeline tracking
- Icon: Shield with checkmark

**Feature 3: Cost Optimization Intelligence**
- Screenshot: FinOps dashboard with savings recommendations
- Bullets: Idle resource detection, rightsizing, commitment optimization
- Icon: Dollar sign with upward trend

**Feature 4: AI ChatOps Assistant**
- Screenshot: Chat interface with natural language query
- Bullets: RAG-powered search, automated runbooks, conversational troubleshooting
- Icon: Chat bubble with sparkles

**Feature 5: Compliance & Audit**
- Screenshot: Compliance dashboard with posture scores
- Bullets: Continuous monitoring, IaC drift detection, automated reports
- Icon: Document with checkmark

**Feature 6: Multi-Channel Alerts**
- Screenshot: Notification center with escalation rules
- Bullets: Slack, PagerDuty, email integration, on-call management
- Icon: Bell with connections

#### **Section 7: How It Works** (Process Flow)
- **Headline**: "Get Started in Minutes, Not Weeks"
- **3-4 Step Process**:
  1. **Connect**: Link your GCP/AWS/Azure accounts (5 min)
  2. **Discover**: Auto-discover and map all resources (automated)
  3. **Monitor**: Real-time insights and AI-powered alerts (immediate)
  4. **Optimize**: Automated remediation and cost savings (ongoing)
- **Visual**: Animated timeline or step-by-step illustration
- **CTA**: "Start Free Trial"

#### **Section 8: Interactive Product Demo** (Optional)
- **Embedded Demo**: Live interactive demo or video walkthrough
- **Alternative**: Screenshot carousel with annotations
- **CTA**: "Book Personalized Demo"

#### **Section 9: Use Cases / Industry Applications**
- **Headline**: "Built for Modern Infrastructure Teams"
- **Tab Navigation or Cards**:
  - Multi-Cloud Operations
  - FinOps Teams
  - Platform Engineering
  - Compliance & Security
- **Each Tab**: Problem → Solution → Results (with metrics)

#### **Section 10: Integration Ecosystem**
- **Headline**: "Integrates with Your Existing Stack"
- **Visual**: Integration grid or connection diagram
- **Categories**:
  - Cloud Providers (GCP, AWS, Azure logos)
  - Monitoring (Prometheus, Grafana, Datadog)
  - Communication (Slack, Teams, PagerDuty)
  - IaC (Terraform, Pulumi, CloudFormation)
  - CI/CD (GitHub Actions, GitLab CI, Jenkins)
- **CTA**: "View All Integrations" → link to docs

#### **Section 11: Technical Specifications**
- **Headline**: "Enterprise-Grade Architecture"
- **2-Column Layout**:
  - **Left**: Architecture diagram
  - **Right**: Key specs list
    - API-first design
    - Microservices on GKE
    - 99.95% uptime SLA
    - <200ms API latency
    - SOC 2 Type II certified
    - GDPR compliant
- **CTA**: "Read Technical Docs"

#### **Section 12: API & Developer Experience**
- **Headline**: "Built for Developers, by Developers"
- **Code Example**: Live code snippet with syntax highlighting
  ```python
  from vertexops import Client
  
  client = Client(api_key="your_api_key")
  
  # Get infrastructure health
  health = client.infrastructure.get_health()
  
  # Query with natural language
  response = client.chatops.query(
      "Why is production GKE cluster latency high?"
  )
  ```
- **Features**:
  - Python SDK
  - REST API
  - CLI tool
  - Comprehensive docs
- **CTA**: "Explore API Docs"

#### **Section 13: ROI Calculator** (Interactive)
- **Headline**: "Calculate Your Potential Savings"
- **Interactive Form**:
  - Number of cloud accounts
  - Monthly cloud spend
  - Number of incidents/month
  - Engineering team size
- **Output**: Estimated savings, MTTR reduction, ROI timeline
- **CTA**: "Get Detailed ROI Report"

#### **Section 14: Pricing / Plans** (If Applicable)
- **Headline**: "Transparent Pricing for Teams of All Sizes"
- **3-Tier Layout**:
  
  **Starter** (For small teams)
  - Up to 100 resources monitored
  - Basic integrations
  - 30-day data retention
  - Community support
  - $499/month
  - CTA: "Start Free Trial"
  
  **Professional** (Most Popular)
  - Up to 1,000 resources
  - All integrations
  - 90-day data retention
  - Priority support
  - Advanced AI features
  - $1,999/month
  - CTA: "Request Demo"
  
  **Enterprise** (Custom)
  - Unlimited resources
  - Custom integrations
  - 2-year data retention
  - Dedicated support
  - On-premise deployment option
  - White-glove onboarding
  - Custom pricing
  - CTA: "Contact Sales"

- **Features Comparison Table** (expandable)
- **FAQ**: "How does billing work?" "Can I change plans?" "Is there a free trial?"

#### **Section 15: Trust & Security**
- **Headline**: "Security and Compliance Built-In"
- **Badge Grid**:
  - SOC 2 Type II
  - ISO 27001
  - GDPR Ready
  - HIPAA Compliant
  - GCP Partner
  - AWS Advanced Technology Partner
- **Key Security Features**:
  - AES-256 encryption
  - TLS 1.3
  - RBAC & SSO
  - Comprehensive audit logs
- **CTA**: "View Security Documentation"

#### **Section 16: Customer Testimonials** (If Available)
- **Headline**: "Loved by DevOps Teams Worldwide"
- **3-Card Carousel**:
  - Customer quote
  - Name, title, company
  - Company logo
  - Key metric achieved
- **Alternative**: "Join 200+ engineering teams transforming their infrastructure"

#### **Section 17: FAQ Section**
- **Headline**: "Frequently Asked Questions"
- **Accordion Layout** (8-12 questions):
  1. What cloud providers does VertexOps support?
  2. How long does setup take?
  3. Do you offer a free trial?
  4. How does AI-powered incident response work?
  5. Can VertexOps integrate with our existing monitoring tools?
  6. What's the difference between Starter and Professional plans?
  7. Is my data secure?
  8. Do you offer on-premise deployment?
  9. What kind of support do you provide?
  10. How does billing work?
  11. Can I cancel anytime?
  12. Do you have an API?

#### **Section 18: Final CTA Section**
- **Headline**: "Transform Your Infrastructure Operations Today"
- **Subheadline**: "Join hundreds of engineering teams reducing MTTR by 67% and cutting costs by 40%"
- **Dual CTAs**:
  - **Primary**: "Request Demo" (button - opens calendar/form)
  - **Secondary**: "Start Free Trial" (button)
- **Trust Line**: "No credit card required • 14-day free trial • Setup in 5 minutes"
- **Visual**: Dashboard screenshot or team illustration

#### **Section 19: Footer**
- **Multi-Column Layout**:
  - **Column 1**: Logo, tagline, social links
  - **Column 2**: Product (Features, Integrations, Pricing, Docs)
  - **Column 3**: Company (About, Careers, Blog, Contact)
  - **Column 4**: Resources (Help Center, API Docs, Status Page, Community)
  - **Column 5**: Legal (Privacy, Terms, Security, Compliance)
- **Bottom Bar**: © 2024 OrionVexa. All rights reserved. | Powered by VertexOps

---

## 🛠️ Technical Architecture & Development Plan

### Recommended Tech Stack

#### **Framework Choice: Next.js 14 (App Router)**
**Justification**:
- Server-side rendering (SSR) for SEO optimization
- Static site generation (SSG) for performance
- Image optimization out-of-the-box
- API routes for form submissions/lead capture
- TypeScript support for type safety
- Excellent developer experience
- Aligns with existing VertexOps frontend stack

#### **Core Dependencies**
```json
{
  "dependencies": {
    "next": "^14.2.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "typescript": "^5.4.0",
    "tailwindcss": "^3.4.0",
    "framer-motion": "^11.0.0",
    "@headlessui/react": "^2.0.0",
    "@heroicons/react": "^2.1.0",
    "react-syntax-highlighter": "^15.5.0",
    "react-intersection-observer": "^9.8.0",
    "swiper": "^11.0.0",
    "lucide-react": "^0.350.0"
  },
  "devDependencies": {
    "eslint": "^8.57.0",
    "prettier": "^3.2.0",
    "@types/react": "^18.3.0",
    "@types/node": "^20.12.0"
  }
}
```

#### **Third-Party Services**
- **Analytics**: Google Analytics 4, Plausible (privacy-focused alternative)
- **Form Handling**: Formspree, Basin, or custom API route
- **Email**: SendGrid API for demo requests
- **Calendly**: Embedded calendar for demo booking
- **Video**: Vimeo or YouTube for product demos
- **Monitoring**: Vercel Analytics, Sentry for error tracking

### Component Architecture

#### **File Structure**
```
vertexops-landing/
├── app/
│   ├── layout.tsx                    # Root layout
│   ├── page.tsx                      # Home page (landing)
│   ├── globals.css                   # Global styles
│   └── api/
│       ├── demo-request/route.ts     # Demo form handler
│       └── newsletter/route.ts       # Newsletter signup
├── components/
│   ├── layout/
│   │   ├── Header.tsx                # Navigation bar
│   │   ├── Footer.tsx                # Footer
│   │   └── MobileMenu.tsx            # Mobile navigation
│   ├── sections/
│   │   ├── HeroSection.tsx           # Hero with CTA
│   │   ├── ProblemSection.tsx        # Pain points
│   │   ├── SolutionSection.tsx       # Value prop
│   │   ├── FeaturesSection.tsx       # Core features
│   │   ├── HowItWorksSection.tsx     # Process steps
│   │   ├── DemoSection.tsx           # Interactive demo
│   │   ├── UseCasesSection.tsx       # Industry applications
│   │   ├── IntegrationsSection.tsx   # Integration grid
│   │   ├── TechnicalSpecsSection.tsx # Architecture
│   │   ├── APISection.tsx            # Developer experience
│   │   ├── ROICalculatorSection.tsx  # Interactive calculator
│   │   ├── PricingSection.tsx        # Pricing tiers
│   │   ├── SecuritySection.tsx       # Trust indicators
│   │   ├── TestimonialsSection.tsx   # Customer quotes
│   │   ├── FAQSection.tsx            # Accordion FAQ
│   │   └── FinalCTASection.tsx       # Conversion section
│   ├── ui/
│   │   ├── Button.tsx                # Reusable button
│   │   ├── Card.tsx                  # Feature cards
│   │   ├── Badge.tsx                 # Trust badges
│   │   ├── CodeBlock.tsx             # Syntax highlighted code
│   │   ├── StatCard.tsx              # Metric display
│   │   ├── Accordion.tsx             # FAQ component
│   │   ├── Modal.tsx                 # Demo request modal
│   │   └── Input.tsx                 # Form inputs
│   └── shared/
│       ├── AnimatedCounter.tsx       # Counting animations
│       ├── LogoCloud.tsx             # Customer logos
│       ├── FeatureCard.tsx           # Feature showcase
│       └── IntegrationLogo.tsx       # Integration icons
├── public/
│   ├── images/
│   │   ├── hero-dashboard.png        # Hero screenshot
│   │   ├── features/                 # Feature screenshots
│   │   ├── logos/                    # Company logos
│   │   ├── integrations/             # Integration icons
│   │   └── architecture.svg          # Architecture diagram
│   ├── videos/
│   │   └── product-demo.mp4          # Demo video
│   └── icons/
│       └── favicon.ico
├── lib/
│   ├── utils.ts                      # Utility functions
│   └── constants.ts                  # Site-wide constants
├── styles/
│   └── animations.css                # Custom animations
├── types/
│   └── index.ts                      # TypeScript types
└── config/
    ├── site.ts                       # Site metadata
    └── features.ts                   # Feature data
```

#### **State Management**
- **No global state library needed** for landing page
- **React Context** for theme/mobile menu state if needed
- **URL State** for tab navigation, accordion expansion
- **Form State**: React Hook Form for demo request forms

#### **Component Patterns**

**Button Component** (Reusable CTA)
```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'outline';
  size: 'sm' | 'md' | 'lg';
  href?: string;
  onClick?: () => void;
  children: React.ReactNode;
}
```

**Feature Card Component**
```typescript
interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  image?: string;
  imagePosition?: 'left' | 'right';
  bullets?: string[];
}
```

**Stat Card Component** (For metrics)
```typescript
interface StatCardProps {
  value: string | number;
  label: string;
  trend?: 'up' | 'down';
  prefix?: string;
  suffix?: string;
}
```

### Design System Implementation

#### **Color System** (Tailwind Config)
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#0A66C2',
          50: '#E8F4FB',
          100: '#D1E9F7',
          500: '#0A66C2',
          600: '#085299',
          700: '#063E73',
        },
        secondary: {
          DEFAULT: '#00A4BD',
          500: '#00A4BD',
        },
        success: '#57A639',
        warning: '#F5C26B',
        error: '#E74C3C',
        gray: {
          50: '#F9FAFB',
          100: '#F3F4F6',
          900: '#1F2937',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
};
```

#### **Typography Scale**
- **H1 (Hero)**: 64px / 4rem - font-bold - tracking-tight
- **H2 (Section)**: 48px / 3rem - font-bold
- **H3 (Subsection)**: 36px / 2.25rem - font-semibold
- **H4 (Card titles)**: 24px / 1.5rem - font-semibold
- **Body Large**: 20px / 1.25rem - font-normal
- **Body**: 16px / 1rem - font-normal
- **Small**: 14px / 0.875rem - font-normal
- **Caption**: 12px / 0.75rem - font-normal

#### **Spacing System** (Tailwind defaults)
- **Section Padding**: py-24 (desktop), py-16 (mobile)
- **Container**: max-w-7xl mx-auto px-6
- **Card Padding**: p-8 (desktop), p-6 (mobile)
- **Element Gap**: gap-8, gap-12, gap-16

#### **Animation Patterns**

**Scroll-Triggered Animations**
```javascript
// Using Framer Motion
<motion.div
  initial={{ opacity: 0, y: 20 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true }}
  transition={{ duration: 0.6 }}
>
  {/* Content */}
</motion.div>
```

**Counter Animation** (For stats)
```typescript
// Animated counting from 0 to target value
const AnimatedCounter = ({ value, suffix = '' }) => {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    // Intersection observer + counting logic
  }, []);
  
  return <span>{count}{suffix}</span>;
};
```

**Hover Effects**
- **Cards**: Scale 1.02, shadow-lg transition
- **Buttons**: Background darken, scale 0.98
- **Links**: Underline slide-in animation

**Page Load Animations**
- **Hero**: Fade in from bottom (stagger children)
- **Features**: Fade in on scroll (stagger)
- **Stats**: Count up animation on scroll into view

---

## 📅 Implementation Roadmap

### **Phase 1: Project Setup & Scaffolding** (Day 1)
- [x] Initialize Next.js 14 project with TypeScript
- [x] Install and configure Tailwind CSS
- [x] Set up ESLint, Prettier
- [x] Configure folder structure
- [x] Create base layout (Header, Footer)
- [x] Set up design tokens in Tailwind config
- [x] Import Inter and JetBrains Mono fonts

### **Phase 2: Core UI Components** (Day 1-2)
- [ ] Build reusable Button component (variants: primary, secondary, outline)
- [ ] Build Card component (feature cards, stat cards)
- [ ] Build Badge component (trust badges, labels)
- [ ] Build Input/Form components
- [ ] Build Modal component (demo request)
- [ ] Build Accordion component (FAQ)
- [ ] Build CodeBlock component (syntax highlighting)
- [ ] Test component library in isolation

### **Phase 3: Section Components** (Day 2-4)
- [ ] **Hero Section**: Headline, CTA, animated dashboard visual
- [ ] **Problem Section**: 3-column pain point cards
- [ ] **Solution Section**: Value prop with visual
- [ ] **Features Section**: Alternating image-text layout (6 features)
- [ ] **How It Works**: 4-step process timeline
- [ ] **Demo Section**: Embedded video or interactive demo
- [ ] **Use Cases**: Tab navigation with case studies
- [ ] **Integrations**: Logo grid with categories
- [ ] **Technical Specs**: Architecture diagram + specs list
- [ ] **API Section**: Live code example with syntax highlighting
- [ ] **ROI Calculator**: Interactive form with results
- [ ] **Pricing Section**: 3-tier pricing cards + comparison table
- [ ] **Security Section**: Badge grid + feature list
- [ ] **Testimonials**: Carousel/slider (if content available)
- [ ] **FAQ Section**: Accordion with 10+ questions
- [ ] **Final CTA**: Large conversion section

### **Phase 4: Content Integration** (Day 4-5)
- [ ] Write all copy based on documentation
- [ ] Source/create all images (screenshots, diagrams, icons)
- [ ] Create or embed product demo video
- [ ] Set up logo cloud (customers or partners)
- [ ] Create architecture diagram (SVG)
- [ ] Prepare code examples for API section
- [ ] Write FAQ answers
- [ ] Create trust badge assets (SOC 2, ISO, etc.)

### **Phase 5: Interactivity & Animations** (Day 5-6)
- [ ] Implement scroll-triggered fade-in animations
- [ ] Add counter animations for stats
- [ ] Implement smooth scroll navigation
- [ ] Add hover effects to cards and buttons
- [ ] Build ROI calculator logic
- [ ] Implement tab navigation (Use Cases section)
- [ ] Add FAQ accordion behavior
- [ ] Implement mobile menu (hamburger)
- [ ] Add video embed/modal functionality

### **Phase 6: Forms & API Integration** (Day 6)
- [ ] Build demo request form (modal)
- [ ] Create API route for form submission
- [ ] Integrate with SendGrid for email notifications
- [ ] Add form validation (React Hook Form + Zod)
- [ ] Implement newsletter signup
- [ ] Add Calendly embed for demo scheduling
- [ ] Test form submissions end-to-end

### **Phase 7: Responsive Design** (Day 7)
- [ ] Mobile optimization (all sections)
- [ ] Tablet breakpoint adjustments
- [ ] Test on iOS Safari, Chrome mobile, Android
- [ ] Optimize touch interactions
- [ ] Test mobile menu navigation
- [ ] Ensure all CTAs are thumb-friendly

### **Phase 8: Performance Optimization** (Day 7-8)
- [ ] Optimize images (WebP format, responsive sizes)
- [ ] Implement lazy loading for images
- [ ] Code splitting for heavy components
- [ ] Minify CSS and JavaScript
- [ ] Enable Brotli compression
- [ ] Optimize font loading (font-display: swap)
- [ ] Run Lighthouse audit (target 90+ scores)
- [ ] Optimize Largest Contentful Paint (LCP)
- [ ] Reduce Cumulative Layout Shift (CLS)
- [ ] Improve First Input Delay (FID)

### **Phase 9: SEO Optimization** (Day 8)
- [ ] Add meta tags (title, description, OG tags)
- [ ] Implement JSON-LD structured data (Organization, SoftwareApplication)
- [ ] Create sitemap.xml
- [ ] Add robots.txt
- [ ] Implement canonical URLs
- [ ] Add Open Graph images (1200x630)
- [ ] Twitter Card meta tags
- [ ] Semantic HTML (proper heading hierarchy)
- [ ] Alt text for all images
- [ ] Internal linking strategy

### **Phase 10: Testing & QA** (Day 9)
- [ ] Cross-browser testing (Chrome, Firefox, Safari, Edge)
- [ ] Accessibility audit (WCAG 2.1 AA compliance)
- [ ] Screen reader testing
- [ ] Keyboard navigation testing
- [ ] Mobile device testing
- [ ] Form submission testing
- [ ] Link validation (all CTAs work)
- [ ] Performance testing (PageSpeed Insights)
- [ ] Analytics implementation testing

### **Phase 11: Launch Preparation** (Day 10)
- [ ] Set up Google Analytics 4
- [ ] Configure Vercel deployment
- [ ] Set up custom domain (orionvexa.ca/vertexops)
- [ ] SSL certificate verification
- [ ] Set up monitoring (Sentry, Vercel Analytics)
- [ ] Create deployment checklist
- [ ] Final stakeholder review
- [ ] Launch! 🚀

---

## 🎯 SEO & Performance Strategy

### **Meta Tags & Structured Data**

#### **Primary Meta Tags**
```html
<title>VertexOps - AI-Powered Infrastructure Operations & DevOps Intelligence</title>
<meta name="description" content="Transform multi-cloud chaos into clarity with VertexOps. AI-powered monitoring, automated incident response, and cost optimization for GCP, AWS, and Azure. Reduce MTTR by 67% and cut costs by 40%." />
<meta name="keywords" content="DevOps automation, infrastructure monitoring, multi-cloud management, FinOps, AI incident response, GCP monitoring, AWS monitoring, Azure monitoring, SRE tools, platform engineering" />
```

#### **Open Graph Tags**
```html
<meta property="og:title" content="VertexOps - AI-Powered Infrastructure Operations" />
<meta property="og:description" content="AI-powered monitoring, incident response, and cost optimization for modern DevOps teams" />
<meta property="og:image" content="https://orionvexa.ca/og-image.png" />
<meta property="og:url" content="https://orionvexa.ca/vertexops" />
<meta property="og:type" content="website" />
```

#### **Twitter Card**
```html
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="VertexOps - AI-Powered DevOps Intelligence" />
<meta name="twitter:description" content="Reduce MTTR by 67% and cut costs by 40% with AI-powered infrastructure operations" />
<meta name="twitter:image" content="https://orionvexa.ca/twitter-card.png" />
```

#### **JSON-LD Structured Data**
```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "VertexOps",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Web",
  "offers": {
    "@type": "Offer",
    "price": "499",
    "priceCurrency": "USD"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "ratingCount": "127"
  },
  "description": "AI-powered infrastructure operations and DevOps intelligence platform"
}
```

### **Core Web Vitals Optimization**

#### **Largest Contentful Paint (LCP)** - Target: <2.5s
- Hero image optimization (WebP, responsive sizes)
- Preload critical fonts and images
- Server-side rendering (Next.js SSR)
- CDN distribution (Vercel Edge Network)

#### **First Input Delay (FID)** - Target: <100ms
- Minimize JavaScript execution time
- Code splitting and lazy loading
- Remove unused third-party scripts
- Use web workers for heavy computations

#### **Cumulative Layout Shift (CLS)** - Target: <0.1
- Set explicit width/height for all images
- Reserve space for dynamic content
- Avoid inserting content above existing content
- Use CSS transforms for animations (not layout properties)

### **Image Optimization Strategy**

#### **Formats**
- **WebP** with JPEG fallback
- **AVIF** for cutting-edge browsers (optional)
- **SVG** for logos, icons, diagrams

#### **Responsive Images**
```html
<Image
  src="/hero-dashboard.png"
  alt="VertexOps Dashboard"
  width={1200}
  height={800}
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 80vw, 1200px"
  priority={true}  // for above-the-fold images
/>
```

#### **Lazy Loading**
- Native `loading="lazy"` for below-fold images
- Intersection Observer for advanced lazy loading
- Blur-up placeholders (LQIP - Low Quality Image Placeholders)

### **Loading Strategy**

#### **Server-Side Rendering (SSR)**
- Initial page load via Next.js SSR
- Hydration on client for interactivity
- Streaming SSR for faster TTFB

#### **Static Site Generation (SSG)**
- Pre-render landing page at build time
- Revalidate on deployment or on-demand
- Optimal for marketing pages (no dynamic data)

#### **Client-Side Rendering (CSR)**
- Interactive components (ROI calculator, forms)
- Lazy load heavy components
- Progressive enhancement approach

---

## 📝 Asset Requirements

### **Images Needed**

#### **Hero Section**
- [ ] Hero dashboard screenshot (1920x1080, WebP)
- [ ] Alternative: Animated dashboard GIF or video background

#### **Features Section** (6 images)
- [ ] Topology map screenshot (infrastructure discovery)
- [ ] Incident detail page screenshot (root cause analysis)
- [ ] FinOps dashboard screenshot (cost optimization)
- [ ] ChatOps interface screenshot (AI assistant)
- [ ] Compliance dashboard screenshot (audit trail)
- [ ] Notification center screenshot (multi-channel alerts)

#### **Integration Logos** (20-30 logos)
- Cloud: GCP, AWS, Azure
- Monitoring: Prometheus, Grafana, Datadog, New Relic, Splunk
- Communication: Slack, Microsoft Teams, PagerDuty, Opsgenie
- IaC: Terraform, Pulumi, CloudFormation, Ansible
- CI/CD: GitHub Actions, GitLab CI, Jenkins, CircleCI
- Version Control: GitHub, GitLab, Bitbucket
- Ticketing: Jira, ServiceNow, Linear

#### **Trust Badges**
- [ ] SOC 2 Type II badge
- [ ] ISO 27001 badge
- [ ] GDPR Ready badge
- [ ] HIPAA Compliant badge
- [ ] GCP Partner badge
- [ ] AWS Advanced Technology Partner badge

#### **Diagrams**
- [ ] Architecture diagram (SVG - showing GKE, Cloud SQL, Redis, AI pipeline)
- [ ] Multi-cloud topology diagram
- [ ] Data flow diagram (logs → AI → insights)

#### **Icons** (Custom or library)
- Feature icons (monitoring, automation, cost, compliance, security)
- Process step icons (connect, discover, monitor, optimize)
- Pain point icons (alert fatigue, complexity, cost overruns)

#### **Favicon & App Icons**
- [ ] Favicon (16x16, 32x32, ICO format)
- [ ] Apple Touch Icon (180x180)
- [ ] Android Chrome Icon (192x192, 512x512)

### **Video Assets**

#### **Product Demo Video** (3-4 minutes)
- [ ] Intro animation (VertexOps logo)
- [ ] Dashboard walkthrough
- [ ] Feature demonstrations
- [ ] Use case examples
- [ ] Closing CTA
- **Format**: MP4 (H.264), 1920x1080, 30fps
- **Hosting**: Vimeo or YouTube (embedded)

#### **Optional Micro-Interactions**
- [ ] Loading spinner animation (Lottie JSON)
- [ ] Success checkmark animation (form submission)
- [ ] Data visualization animations (chart transitions)

### **Copy Assets**

#### **Long-Form Content**
- [ ] Product descriptions (150-300 words per feature)
- [ ] Use case narratives (200-400 words each)
- [ ] FAQ answers (50-150 words each)
- [ ] Pricing tier descriptions (100-200 words)

#### **Short-Form Content**
- [ ] Value propositions (1-2 sentences)
- [ ] Feature bullets (5-8 words each)
- [ ] CTA button text
- [ ] Navigation labels
- [ ] Trust indicators
- [ ] Social proof quotes

---

## ❓ Content Gaps & Questions

### **Missing Information Needed**

#### **Company/Legal**
- [ ] Company legal name and registration details
- [ ] Privacy policy URL
- [ ] Terms of service URL
- [ ] Cookie policy details
- [ ] GDPR compliance statement
- [ ] Data processing agreement (DPA) availability

#### **Pricing**
- [ ] Exact pricing tiers and limits (Starter, Professional, Enterprise)
- [ ] Free trial details (duration, limitations, credit card requirement?)
- [ ] Custom enterprise pricing approach
- [ ] Billing cycle (monthly, annual, both?)
- [ ] Discounts for annual plans?
- [ ] Add-on pricing (extra resources, longer retention, etc.)

#### **Customer Proof**
- [ ] Customer logos (permission to display?)
- [ ] Testimonial quotes (with names, titles, companies)
- [ ] Case study availability (with metrics)
- [ ] Customer count or "Trusted by X teams" number
- [ ] Industry breakdown (% in fintech, healthcare, etc.)

#### **Support & SLA**
- [ ] Support channels (email, chat, phone?)
- [ ] Support hours (24/7, business hours, timezone?)
- [ ] Response time SLAs by tier
- [ ] Onboarding process details
- [ ] Training/documentation availability
- [ ] Community forum or Slack channel?

#### **Technical**
- [ ] Free trial technical limitations
- [ ] On-premise deployment details (if Enterprise tier)
- [ ] Data residency options (regional deployments?)
- [ ] API rate limits by tier
- [ ] Webhook reliability guarantees
- [ ] Backup and disaster recovery details
- [ ] Multi-region availability

#### **Integrations**
- [ ] Complete integration list with setup complexity
- [ ] Coming soon integrations roadmap
- [ ] Custom integration development (Professional Services?)
- [ ] Webhooks documentation URL
- [ ] SSO providers supported (beyond Google, Okta, Azure AD?)

#### **Security & Compliance**
- [ ] SOC 2 report availability (Type I or Type II?)
- [ ] ISO 27001 certificate number and validity
- [ ] Penetration testing frequency
- [ ] Bug bounty program?
- [ ] GDPR Data Processing Agreement (DPA) URL
- [ ] HIPAA Business Associate Agreement (BAA) availability
- [ ] Data retention policies by tier

#### **Sales & Marketing**
- [ ] Demo booking process (Calendly link? Salesforce form?)
- [ ] Sales team contact (email, phone?)
- [ ] Free trial signup flow (self-service or sales-led?)
- [ ] Lead magnet offers (whitepapers, guides, calculators?)
- [ ] Newsletter signup incentive?
- [ ] Referral program details?

### **Clarifications Required**

1. **Brand Identity**:
   - Is VertexOps a standalone product or part of OrionVexa suite?
   - Logo files available (SVG, PNG variants)?
   - Brand guidelines document?

2. **Target Persona Priority**:
   - Primary target: IC engineers or leadership?
   - Messaging tone: highly technical or business-value focused?
   - Decision-maker: hands-on engineer or CTO/VP Eng?

3. **Competitive Positioning**:
   - Main competitors (Datadog, New Relic, Dynatrace, PagerDuty?)
   - Key differentiators to emphasize?
   - Comparison page needed?

4. **Analytics & Tracking**:
   - Google Analytics property ID?
   - Conversion tracking goals (demo requests, trial signups?)
   - Attribution tracking (UTM parameters?)
   - A/B testing tools (Google Optimize, VWO?)

5. **Launch Timeline**:
   - Hard deadline for launch?
   - Soft launch vs. full launch?
   - Marketing campaign coordination?

### **Assumptions Being Made**

1. **Pricing**: Assuming 3-tier model (Starter $499, Pro $1,999, Enterprise custom) based on industry standards for similar platforms
2. **Free Trial**: Assuming 14-day free trial with no credit card required
3. **Target Geography**: Assuming global availability (primary: North America, Europe)
4. **Customer Logos**: Assuming no customer logos available yet (using "Trusted by 200+ engineering teams" generic messaging)
5. **Testimonials**: Assuming no customer quotes available yet (section can be hidden or show generic value props)
6. **Support**: Assuming tiered support (Community, Priority, Dedicated) aligned with pricing tiers
7. **Deployment**: Assuming SaaS-only for Starter/Pro, on-premise option for Enterprise
8. **Data Retention**: Assuming 30 days (Starter), 90 days (Pro), 2 years (Enterprise)
9. **Domain**: Assuming landing page hosted at `orionvexa.ca/vertexops` or subdomain `vertexops.orionvexa.ca`

---

## ✅ Development Checklist

### **Pre-Development**
- [ ] Review all available documentation
- [ ] Get approval on design mockups/wireframes
- [ ] Confirm copy and messaging with stakeholders
- [ ] Gather all required assets (images, logos, videos)
- [ ] Set up development environment
- [ ] Create GitHub repository
- [ ] Initialize Next.js project

### **During Development**
- [ ] Follow component-first approach (build UI library first)
- [ ] Implement responsive breakpoints from start
- [ ] Test accessibility as you build (not at the end)
- [ ] Commit frequently with clear messages
- [ ] Run Lighthouse audits on each section completion
- [ ] Test on real devices (not just browser DevTools)

### **Pre-Launch**
- [ ] Cross-browser testing completed
- [ ] Mobile testing on iOS and Android
- [ ] Accessibility audit (WCAG 2.1 AA)
- [ ] Performance optimization (90+ Lighthouse scores)
- [ ] SEO metadata verified
- [ ] Analytics tracking tested
- [ ] Forms tested end-to-end
- [ ] All links validated
- [ ] Legal pages linked (Privacy, Terms)
- [ ] Sitemap and robots.txt created
- [ ] 404 page created
- [ ] Favicon and app icons added
- [ ] Open Graph images tested (LinkedIn, Twitter preview)
- [ ] Load testing (handle expected traffic)
- [ ] Security headers configured (CSP, HSTS, etc.)
- [ ] SSL certificate verified
- [ ] Stakeholder final approval

### **Post-Launch**
- [ ] Submit sitemap to Google Search Console
- [ ] Monitor Core Web Vitals in real-user data
- [ ] Set up uptime monitoring (Pingdom, UptimeRobot)
- [ ] Monitor analytics (bounce rate, conversions)
- [ ] A/B test hero CTA variations
- [ ] Collect user feedback
- [ ] Iterate based on heatmaps (Hotjar, Microsoft Clarity)

---

## 🎨 Design Inspiration & References

### **Similar SaaS Landing Pages** (for inspiration)
- **Datadog**: datadog.com (multi-product navigation, integration showcase)
- **PagerDuty**: pagerduty.com (incident management messaging)
- **Terraform Cloud**: terraform.io (developer-focused, code examples)
- **Vercel**: vercel.com (clean, fast, developer experience)
- **Linear**: linear.app (beautiful animations, minimal design)
- **Stripe**: stripe.com (technical depth, developer tools showcase)

### **Color & Aesthetic**
- LinkedIn-inspired professional blue (#0A66C2)
- Enterprise SaaS aesthetic (clean, trustworthy, modern)
- Balance between technical depth and business value
- Not too playful, not too corporate

### **Animation Style**
- Subtle and professional (not distracting)
- Scroll-triggered fade-ins (Framer Motion)
- Smooth transitions (0.3s ease-in-out)
- Data visualization animations (counting numbers, chart reveals)
- Micro-interactions on hover (scale, shadow, color shift)

---

## 📊 Success Metrics

### **Performance KPIs**
- **Lighthouse Score**: 90+ (Performance, Accessibility, Best Practices, SEO)
- **LCP**: <2.5 seconds
- **FID**: <100ms
- **CLS**: <0.1
- **Page Load Time**: <3 seconds (on 3G)
- **Bundle Size**: <500KB (initial load)

### **Conversion KPIs** (to track post-launch)
- **Demo Request Rate**: Target 3-5% of visitors
- **Free Trial Signup Rate**: Target 1-2% of visitors
- **Bounce Rate**: <50%
- **Avg. Session Duration**: >2 minutes
- **Scroll Depth**: 60%+ reach pricing section
- **CTA Click-Through Rate**: 8-12%

### **SEO KPIs** (3 months post-launch)
- **Organic Traffic**: Growing month-over-month
- **Keyword Rankings**: Page 1 for "AI DevOps platform", "multi-cloud monitoring", "infrastructure automation"
- **Backlinks**: 10+ quality backlinks
- **Domain Authority**: 20+ (Moz)

---

## 🚀 Final Notes

This landing page is the digital storefront for VertexOps. It must:
1. **Educate**: Clearly explain what VertexOps does and why it matters
2. **Convince**: Demonstrate ROI and competitive advantages
3. **Convert**: Drive demo requests and free trial signups
4. **Delight**: Provide an excellent user experience that reflects product quality

The landing page should reflect the same level of polish and intelligence as the VertexOps platform itself. Every section, every word, every pixel should serve the goal of converting visitors into customers.

**Development Mindset**:
- Build mobile-first, enhance for desktop
- Accessibility is not optional
- Performance is a feature
- Every component should be reusable
- Test early, test often
- Ship fast, iterate faster

---

**End of Prompt**

**Next Steps**:
1. Review this prompt with stakeholders
2. Gather missing information (pricing, customers, assets)
3. Create design mockups in Figma (optional but recommended)
4. Begin Phase 1 development (setup & scaffolding)
5. Set up project management (Linear, Jira, or GitHub Projects)
6. Establish review cadence with stakeholders

**Estimated Timeline**: 10-12 days for full implementation (single developer, full-time)

**Questions or Clarifications?** Please provide:
- Missing documentation files
- Asset availability (logos, screenshots, videos)
- Pricing details
- Customer proof (if any)
- Legal page URLs
- Analytics/tracking requirements
- Launch deadline
