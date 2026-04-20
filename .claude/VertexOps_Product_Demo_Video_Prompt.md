# VertexOps Product Demo Video - Cursor IDE Prompt

## 🎯 Objective
Create a professional, interactive HTML5-based product demo video/walkthrough for VertexOps that demonstrates the complete user journey from login to key feature usage. This demo will be embedded in the landing page and serve as an interactive tutorial for potential customers.

---

## 📋 Project Context

**Product**: VertexOps - AI-Powered Infrastructure Operations & DevOps Intelligence Platform
**Target Audience**: DevOps Engineers, SREs, Platform Engineers, CTOs
**Demo Duration**: 3-4 minutes (can be skipped/fast-forwarded)
**Format**: Interactive HTML5 video player OR step-by-step interactive tutorial
**Technology**: HTML5, CSS3, JavaScript (vanilla or React component)

---

## 🎬 Demo Flow & Storyboard

### **Scene 1: Login & Authentication** (0:00 - 0:20)
**Screen to Show**: Login page with SSO options

**Visual Elements**:
- Clean login form with VertexOps logo at top
- Email/password fields
- "Continue with Google" button (SSO)
- "Continue with Okta" button (SSO)
- "Continue with Azure AD" button (SSO)
- 2FA code entry screen (brief flash)
- Success animation → dashboard transition

**Voiceover/Text Overlay**:
"Welcome to VertexOps. Login securely with your SSO provider or enterprise credentials. Multi-factor authentication ensures your infrastructure data stays protected."

**Key Actions to Highlight**:
1. Click "Continue with Google"
2. SSO authentication success
3. 2FA verification (6-digit code entry)
4. Smooth transition to dashboard

**Animation Notes**:
- Smooth fade-in for login form
- Button hover states (scale 1.02, shadow)
- Success checkmark animation after login
- Transition: Fade out login → Fade in dashboard (0.5s)

---

### **Scene 2: Dashboard Overview** (0:20 - 0:45)
**Screen to Show**: Main dashboard with real-time metrics

**Visual Elements**:
- Top navigation bar (logo, search, notifications, profile)
- Left sidebar menu (Dashboard, Infrastructure, Incidents, Cost, Compliance, Settings)
- 4 metric cards at top:
  - **847 Resources Monitored** (with upward trend arrow)
  - **23 Incidents Auto-Resolved Today** (green checkmark)
  - **$47,324 Saved This Month** (dollar icon)
  - **98.7% Compliance Score** (shield icon)
- Real-time activity feed (right panel)
- Multi-cloud resource topology graph (center)
- Recent incidents timeline (bottom)

**Voiceover/Text Overlay**:
"Your command center. Get instant visibility into your entire multi-cloud infrastructure across GCP, AWS, and Azure. Monitor resources, track incidents, and visualize cost savings in real-time."

**Key Actions to Highlight**:
1. Animated counter incrementing on metric cards
2. Hover over topology graph nodes (show resource details tooltip)
3. Activity feed auto-scrolling with new events
4. Click on "View All Incidents" link

**Animation Notes**:
- Counters animate from 0 to target value (1.5s, ease-out)
- Topology graph: nodes pulse with different colors (green=healthy, yellow=warning, red=critical)
- Activity feed: new items slide in from top every 2 seconds
- Hover tooltips: fade in (0.2s)

---

### **Scene 3: Multi-Cloud Infrastructure Discovery** (0:45 - 1:15)
**Screen to Show**: Infrastructure page with topology map

**Visual Elements**:
- Top filters: Cloud Provider (GCP/AWS/Azure), Resource Type, Region, Status
- Interactive topology map showing:
  - GCP resources (blue nodes): GKE clusters, Cloud SQL, Compute Engine
  - AWS resources (orange nodes): EC2, RDS, Lambda
  - Azure resources (cyan nodes): VMs, AKS, SQL Database
- Connection lines between dependent resources
- Resource details panel (right side) when node is clicked
- Real-time metrics sparklines for selected resource

**Voiceover/Text Overlay**:
"VertexOps automatically discovers and maps your entire infrastructure. Visualize dependencies, monitor health, and identify bottlenecks across all your cloud providers from a single pane of glass."

**Key Actions to Highlight**:
1. Click "GCP" filter → map updates to show only GCP resources
2. Click on a GKE cluster node → right panel slides in with details
3. Show CPU/Memory/Network sparklines updating in real-time
4. Hover over connection line → tooltip shows "API calls: 1.2K/min"
5. Click "Anomaly Detected" badge → zooms into problematic resource

**Animation Notes**:
- Filter click: smooth transition, nodes fade out/in (0.4s)
- Node selection: scale to 1.1, glow effect, panel slides from right (0.3s)
- Sparklines: animated drawing effect (1s)
- Anomaly badge: pulsing red glow animation (infinite)

---

### **Scene 4: Incident Detection & Root Cause Analysis** (1:15 - 2:00)
**Screen to Show**: Incident detail page

**Visual Elements**:
- Incident header:
  - Title: "High Memory Usage - Production GKE Cluster"
  - Severity: CRITICAL (red badge)
  - Status: AUTO-RESOLVING (yellow badge)
  - Detected: 2 minutes ago
  - Affected Resources: 3 pods
- AI-powered root cause analysis section:
  - Decision tree diagram showing analysis path
  - Confidence score: 94%
  - Root cause: "Memory leak in app-v2.3 deployment"
- Timeline section (showing incident evolution):
  - 10:15 AM - Memory usage increased to 85%
  - 10:17 AM - Threshold breached (90%)
  - 10:18 AM - AI analysis initiated
  - 10:19 AM - Root cause identified
  - 10:20 AM - Auto-remediation proposed
- Affected resources table (pods with memory usage bars)
- Recommended remediation actions:
  1. ✅ Scale down app-v2.3 deployment (auto-applied)
  2. ⏸️ Restart high-memory pods (awaiting approval)
  3. 📊 Enable memory profiling (manual)

**Voiceover/Text Overlay**:
"When incidents occur, VertexOps doesn't just alert you—it analyzes root causes using AI and proposes automated remediation. Approve with one click or let the system auto-resolve based on your policies."

**Key Actions to Highlight**:
1. Scroll through timeline (auto-scroll animation)
2. Hover over decision tree nodes → tooltips explain analysis steps
3. Click "Approve Remediation" button
4. Success animation → Status changes to "RESOLVED" (green)
5. Show before/after memory usage graph

**Animation Notes**:
- Timeline auto-scroll: smooth vertical scroll (2s)
- Decision tree: nodes highlight sequentially showing analysis path (1.5s)
- Approval click: button → spinner → success checkmark (1s total)
- Status badge color transition: yellow → green (0.3s)
- Before/after graph: bar chart animates downward (1s)

---

### **Scene 5: AI ChatOps Assistant** (2:00 - 2:35)
**Screen to Show**: ChatOps interface (can be sidebar or full page)

**Visual Elements**:
- Chat input box at bottom: "Ask me anything about your infrastructure..."
- Conversation bubbles showing Q&A:
  - **User**: "Why is production GKE cluster latency high?"
  - **AI Assistant**: 
    - Typing indicator (animated dots)
    - Response with sections:
      - **Analysis**: "I've analyzed logs, metrics, and traces. The latency spike correlates with..."
      - **Root Cause**: "Network congestion on us-central1 region (95th percentile: 245ms)"
      - **Metrics Graph**: Line chart showing latency over time
      - **Suggested Actions**: 
        1. Enable CDN for static assets
        2. Scale up regional load balancer
        3. Review database query performance
- Quick action buttons: "Show me affected services" | "Run diagnostics" | "Create incident"
- Knowledge base search results panel (related docs, past incidents)

**Voiceover/Text Overlay**:
"Need answers fast? Ask VertexOps in natural language. Our AI assistant searches across logs, metrics, documentation, and past incidents to give you instant, actionable insights."

**Key Actions to Highlight**:
1. Type query (animated typing effect)
2. Press Enter → typing indicator appears
3. Response streams in (typewriter effect)
4. Metrics graph animates into view
5. Click "Show me affected services" → navigates to filtered infrastructure view
6. Show suggested runbook: "High Latency Troubleshooting" → click to execute

**Animation Notes**:
- User input: typewriter effect (0.1s per character)
- Typing indicator: 3 bouncing dots (infinite loop)
- AI response: stream in word-by-word (fast typewriter, 0.05s per word)
- Graph: draws line from left to right (1s)
- Buttons: fade in after response completes (0.3s stagger)

---

### **Scene 6: Cost Optimization Dashboard (FinOps)** (2:35 - 3:00)
**Screen to Show**: FinOps cost optimization page

**Visual Elements**:
- Top metric cards:
  - **Monthly Spend**: $47,324 (↓ 40% vs last month)
  - **Projected Savings**: $23,150
  - **Idle Resources**: 17 detected
  - **Optimization Score**: 78/100
- Cost breakdown donut chart (by service):
  - Compute: 45%
  - Storage: 25%
  - Networking: 15%
  - Databases: 10%
  - Other: 5%
- AI-driven recommendations table:
  - "Idle GCE instance in us-east1" → Est. savings: $456/month → "Terminate" button
  - "RDS over-provisioned" → Est. savings: $1,200/month → "Rightsize to db.t3.large"
  - "Unused EBS volumes (5)" → Est. savings: $340/month → "Delete"
- Cost trend chart (last 90 days) showing downward trend
- Reserved instance/commitment recommendations

**Voiceover/Text Overlay**:
"Cut cloud costs by 40% with AI-driven recommendations. VertexOps identifies idle resources, suggests rightsizing, and optimizes commitments—saving you thousands every month."

**Key Actions to Highlight**:
1. Donut chart segments hover → show exact amounts
2. Click "Idle Resources" → table filters to show only idle
3. Hover over recommendation → detailed analysis tooltip
4. Click "Approve All Savings" → batch approve 3 recommendations
5. Show projected vs actual savings comparison

**Animation Notes**:
- Donut chart: segments animate in clockwise (1.5s, stagger 0.2s)
- Metric cards: count up animation (1s)
- Recommendations table: rows slide in from bottom (0.3s stagger)
- Approval click: checkmark animation on each row (0.2s stagger)
- Trend chart: line draws from left to right (1.5s)

---

### **Scene 7: Compliance & Audit Trail** (3:00 - 3:25)
**Screen to Show**: Compliance dashboard

**Visual Elements**:
- Compliance posture gauge (circular progress):
  - Overall Score: 98.7%
  - Color gradient: red (0%) → yellow (50%) → green (100%)
- Compliance frameworks tabs:
  - SOC 2 (selected)
  - ISO 27001
  - GDPR
  - HIPAA
- Controls checklist (SOC 2):
  - ✅ Access Controls (100% compliant)
  - ✅ Encryption at Rest (100%)
  - ⚠️ Log Retention (85% - 3 resources non-compliant)
  - ✅ Network Security (100%)
- Failed checks table:
  - "GCS bucket 'prod-logs' has 60-day retention (policy requires 90)"
  - Severity: MEDIUM
  - Remediation: "Update lifecycle policy"
- Audit log table (recent AI agent actions):
  - "AI Agent scaled down dev-cluster (cost optimization)" - 5 min ago
  - "AI Agent enabled Cloud Armor WAF (security recommendation)" - 1 hour ago
  - User: system@vertexops.ai
- PDF export button: "Generate Compliance Report"

**Voiceover/Text Overlay**:
"Stay audit-ready 24/7. VertexOps continuously monitors compliance across SOC 2, ISO 27001, GDPR, and HIPAA. Every AI action is logged, and reports are one click away."

**Key Actions to Highlight**:
1. Gauge animates to 98.7% (circular fill animation)
2. Click "GDPR" tab → controls update
3. Click failed check row → remediation panel slides in
4. Click "Auto-Remediate" → success animation
5. Click "Generate Compliance Report" → PDF download modal

**Animation Notes**:
- Gauge: circular progress fill (2s, ease-in-out)
- Tab switch: content fade out/in (0.3s)
- Remediation panel: slide from right (0.4s)
- Auto-remediate: button → spinner → checkmark (1.5s)
- PDF modal: scale in from center (0.3s)

---

### **Scene 8: Multi-Channel Notifications** (3:25 - 3:45)
**Screen to Show**: Notification center / Alert rules configuration

**Visual Elements**:
- Notification inbox (left panel):
  - Recent alerts with icons (Slack, Email, PagerDuty, Teams)
  - "Critical: Memory threshold breached" - Slack (2 min ago)
  - "Info: Cost savings recommendation" - Email (1 hour ago)
  - "Warning: SSL cert expiring in 7 days" - PagerDuty (3 hours ago)
- Alert rule builder (right panel):
  - Trigger: "When incident severity = CRITICAL"
  - Channels: ☑ Slack, ☑ PagerDuty, ☐ Email, ☑ In-App
  - Escalation policy: 
    - → Notify on-call engineer (immediate)
    - → Escalate to manager (if not acked in 10 min)
    - → Page VP Eng (if not acked in 30 min)
  - Schedule: 24/7 or business hours selector
- Live notification preview: Mock Slack message and PagerDuty alert

**Voiceover/Text Overlay**:
"Never miss a critical alert. Configure intelligent routing across Slack, PagerDuty, email, and Teams. Set up escalation policies and on-call rotations to ensure the right person is notified at the right time."

**Key Actions to Highlight**:
1. Click notification → detail panel expands
2. Toggle "Email" checkbox → preview updates
3. Drag escalation steps to reorder
4. Click "Test Alert" → live notification sent to Slack (show animation)
5. Show on-call calendar integration

**Animation Notes**:
- Notification click: row highlights, panel slides from right (0.3s)
- Channel toggle: checkbox animation, preview updates (0.2s)
- Drag-and-drop: smooth reordering with placeholder (0.3s)
- Test alert: ripple effect from button → Slack icon pulse (1s)
- Calendar: slide in from bottom (0.4s)

---

### **Scene 9: Settings & Integrations** (3:45 - 4:05)
**Screen to Show**: Settings page - Integrations tab

**Visual Elements**:
- Integration categories (left sidebar):
  - Cloud Providers ✅ (3 connected)
  - Monitoring Tools (2 connected)
  - Communication (4 connected)
  - IaC Tools (1 connected)
  - CI/CD (2 connected)
- Integration cards grid:
  - **Google Cloud Platform** - CONNECTED (green badge)
    - 3 projects linked
    - Last sync: 2 min ago
    - "Manage" button
  - **Slack** - CONNECTED
    - #alerts, #incidents channels
    - "Configure" button
  - **Terraform Cloud** - NOT CONNECTED
    - "Connect" button
- Connection modal (when clicking "Connect"):
  - OAuth flow for Slack
  - API key input for Terraform Cloud
  - Test connection button
- API key management panel:
  - Generate new key
  - List of active keys with last used timestamp
  - Revoke option

**Voiceover/Text Overlay**:
"Connect VertexOps to your existing stack in minutes. Native integrations with GCP, AWS, Azure, Slack, PagerDuty, Terraform, and 20+ more tools. Manage API keys and permissions securely."

**Key Actions to Highlight**:
1. Click "Connect" on Terraform Cloud card
2. Modal appears with API key input field
3. Paste API key (masked: ••••••••)
4. Click "Test Connection" → success checkmark
5. Click "Save" → card updates to CONNECTED
6. Show newly connected integration in sidebar count

**Animation Notes**:
- Modal: scale in from center with backdrop fade (0.3s)
- API key input: typing animation (masked characters)
- Test connection: button → spinner → checkmark (1.5s)
- Card state change: NOT CONNECTED → CONNECTED with color transition (0.5s)
- Sidebar count: increment animation (0.3s)

---

### **Scene 10: Closing Summary** (4:05 - 4:20)
**Screen to Show**: Dashboard with success metrics overlaid

**Visual Elements**:
- Return to main dashboard view
- Animated overlay showing key accomplishments:
  - ✅ Logged in securely with SSO
  - ✅ Monitored 847 resources across 3 clouds
  - ✅ Detected and auto-resolved 23 incidents
  - ✅ Saved $47K+ this month
  - ✅ Maintained 98.7% compliance
  - ✅ Connected 10 integrations
- Final metric cards pulse with success animation
- VertexOps logo animates in center
- CTA overlay: "Ready to transform your infrastructure?"
  - "Start Free Trial" button
  - "Request Demo" button

**Voiceover/Text Overlay**:
"That's VertexOps—your AI-powered infrastructure copilot. From automated incident response to proactive cost optimization, VertexOps transforms how modern engineering teams manage multi-cloud infrastructure. Ready to get started?"

**Key Actions to Highlight**:
1. Checklist items appear sequentially (0.3s stagger)
2. Metric cards pulse in sync (1s)
3. Logo scales in with glow effect (1s)
4. CTA buttons slide up from bottom (0.5s)
5. Cursor hovers over "Start Free Trial" → button scales slightly

**Animation Notes**:
- Checklist: items slide in from left with checkmark animation (0.3s stagger)
- Metric cards: simultaneous pulse (scale 1.05, glow) (1s)
- Logo: scale from 0 to 1 with rotation (1s, ease-out)
- CTA overlay: backdrop fade in (0.3s), buttons slide up (0.5s, stagger 0.2s)
- Button hover: scale 1.05, shadow increase (0.2s)

---

## 🛠️ Technical Implementation Requirements

### **Format Options**

#### **Option 1: Interactive HTML5 Demo (Recommended)**
Build a fully interactive, clickable demo where users can:
- Click through each screen
- Interact with UI elements (hover, click buttons)
- Control playback (play, pause, skip, restart)
- Jump to specific sections via chapter markers

**Tech Stack**:
- HTML5, CSS3, JavaScript (vanilla or React)
- Libraries: 
  - `driver.js` or `intro.js` for guided tour overlays
  - `anime.js` or `GSAP` for smooth animations
  - `Prism.js` for code syntax highlighting (if showing code)

#### **Option 2: HTML5 Video with Interactive Overlays**
- Embed an MP4 video background
- Add clickable hotspots and interactive elements on top
- Use `video.js` or `plyr.js` for custom video player

#### **Option 3: Animated SVG/Canvas Tutorial**
- Build entirely with SVG animations and Canvas
- Frame-by-frame control
- Fully customizable and lightweight

### **Required Features**

1. **Video Player Controls**:
   - Play/Pause button
   - Progress bar (seekable)
   - Speed controls (0.5x, 1x, 1.5x, 2x)
   - Fullscreen toggle
   - Mute/Unmute
   - Chapter markers (9 clickable sections)

2. **Interactive Elements**:
   - Clickable UI elements that respond to hover/click
   - Tooltips on hover (explain features)
   - Skip to section buttons
   - "Try it yourself" CTA at the end

3. **Responsive Design**:
   - Works on desktop (1920x1080)
   - Tablet (1024x768)
   - Mobile (375x667) - simplified version

4. **Accessibility**:
   - Keyboard navigation (Space to play/pause, Arrow keys to skip)
   - Screen reader friendly
   - Closed captions/transcripts available
   - ARIA labels on interactive elements

5. **Performance**:
   - Lazy load video/assets
   - Optimized animations (60fps)
   - Total size <5MB (compressed)
   - Fast initial load (<2s)

### **File Structure**

```
vertexops-demo/
├── index.html                 # Main demo player
├── styles/
│   ├── demo.css              # Demo-specific styles
│   ├── animations.css        # Animation keyframes
│   └── player.css            # Video player controls
├── scripts/
│   ├── demo-controller.js    # Main demo orchestration
│   ├── animations.js         # Animation functions
│   ├── player.js             # Video player logic
│   └── interactions.js       # Click/hover handlers
├── assets/
│   ├── screenshots/          # UI screenshots for each scene
│   │   ├── login.png
│   │   ├── dashboard.png
│   │   ├── infrastructure.png
│   │   ├── incident.png
│   │   ├── chatops.png
│   │   ├── cost.png
│   │   ├── compliance.png
│   │   ├── notifications.png
│   │   └── integrations.png
│   ├── icons/                # UI icons
│   ├── logos/                # Brand assets
│   └── video/
│       ├── demo-full.mp4     # Full video (if using video approach)
│       └── voiceover.mp3     # Voiceover audio track
├── data/
│   ├── scenes.json           # Scene definitions and timings
│   ├── captions.vtt          # Closed captions
│   └── chapters.json         # Chapter markers
└── README.md                 # Setup instructions
```

### **Data Structure (scenes.json)**

```json
{
  "scenes": [
    {
      "id": 1,
      "title": "Login & Authentication",
      "duration": 20,
      "startTime": 0,
      "screenshot": "assets/screenshots/login.png",
      "voiceover": "Welcome to VertexOps. Login securely...",
      "interactions": [
        {
          "type": "click",
          "element": "sso-google-btn",
          "timestamp": 3,
          "action": "showSuccessAnimation"
        }
      ],
      "animations": [
        {
          "type": "fadeIn",
          "element": "login-form",
          "delay": 0,
          "duration": 0.5
        }
      ]
    },
    // ... 8 more scenes
  ],
  "chapters": [
    { "time": 0, "title": "Login" },
    { "time": 20, "title": "Dashboard" },
    { "time": 45, "title": "Infrastructure" },
    { "time": 75, "title": "Incidents" },
    { "time": 120, "title": "ChatOps" },
    { "time": 155, "title": "Cost Optimization" },
    { "time": 180, "title": "Compliance" },
    { "time": 205, "title": "Notifications" },
    { "time": 225, "title": "Integrations" },
    { "time": 245, "title": "Summary" }
  ]
}
```

---

## 🎨 Design Specifications

### **Color Palette** (Consistent with VertexOps Brand)
- **Primary Blue**: #0A66C2
- **Secondary Teal**: #00A4BD
- **Success Green**: #57A639
- **Warning Amber**: #F5C26B
- **Error Red**: #E74C3C
- **Background**: #F9FAFB
- **Text Dark**: #1F2937
- **Text Light**: #6B7280

### **Typography**
- **Font Family**: Inter (sans-serif)
- **Headings**: Inter Bold (600)
- **Body**: Inter Regular (400)
- **Code**: JetBrains Mono

### **Animation Timings**
- **Fast transitions**: 0.2s (hovers, toggles)
- **Medium transitions**: 0.5s (panel slides, modal opens)
- **Slow transitions**: 1s (scene transitions, complex animations)
- **Easing**: ease-in-out (default), ease-out (entrances), ease-in (exits)

### **UI Element Sizes**
- **Buttons**: 
  - Small: 32px height
  - Medium: 40px height (default)
  - Large: 48px height
- **Icons**: 20px, 24px, 32px
- **Cards**: 16px border-radius, 8px padding
- **Modal**: max-width 800px, 16px border-radius

---

## 📝 Voiceover Script (Complete)

**[Scene 1: Login]**
"Welcome to VertexOps, your AI-powered infrastructure copilot. Login securely with your enterprise SSO provider. Multi-factor authentication ensures your infrastructure data stays protected at all times."

**[Scene 2: Dashboard]**
"This is your command center. Get instant visibility into your entire multi-cloud infrastructure across Google Cloud, AWS, and Azure. Monitor eight hundred forty-seven resources, track incidents in real-time, and visualize cost savings—all from a single dashboard."

**[Scene 3: Infrastructure Discovery]**
"VertexOps automatically discovers and maps your entire infrastructure. Visualize dependencies, monitor resource health, and identify bottlenecks across all your cloud providers from a single pane of glass. No manual configuration required."

**[Scene 4: Incident Detection]**
"When incidents occur, VertexOps doesn't just alert you—it analyzes root causes using artificial intelligence and proposes automated remediation. Approve with one click, or let the system auto-resolve based on your predefined policies. Reduce mean time to resolution by sixty-seven percent."

**[Scene 5: AI ChatOps]**
"Need answers fast? Ask VertexOps in natural language. Our AI assistant searches across logs, metrics, historical data, and documentation to give you instant, actionable insights. It's like having a senior SRE on call, twenty-four seven."

**[Scene 6: Cost Optimization]**
"Cut cloud costs by forty percent with AI-driven recommendations. VertexOps identifies idle resources, suggests rightsizing opportunities, and optimizes reserved instance commitments—saving you thousands of dollars every month on autopilot."

**[Scene 7: Compliance]**
"Stay audit-ready around the clock. VertexOps continuously monitors compliance across SOC 2, ISO twenty-seven thousand one, GDPR, and HIPAA frameworks. Every AI action is logged in an immutable audit trail, and compliance reports are just one click away."

**[Scene 8: Notifications]**
"Never miss a critical alert. Configure intelligent routing across Slack, PagerDuty, email, and Microsoft Teams. Set up escalation policies and on-call rotations to ensure the right person is notified at the right time, every time."

**[Scene 9: Integrations]**
"Connect VertexOps to your existing stack in minutes. Native integrations with all major cloud providers, monitoring tools, and DevOps platforms. Manage API keys and permissions securely from a centralized interface."

**[Scene 10: Closing]**
"That's VertexOps—your intelligent infrastructure copilot. From automated incident response to proactive cost optimization and continuous compliance monitoring, VertexOps transforms how modern engineering teams manage multi-cloud infrastructure. Ready to get started? Start your free trial today."

---

## ✅ Implementation Checklist

### **Pre-Development**
- [ ] Choose implementation approach (Interactive HTML5, Video, or SVG)
- [ ] Gather all UI screenshots (9 screens)
- [ ] Record or source voiceover audio (professional or AI-generated)
- [ ] Create chapter markers and timing breakdown
- [ ] Set up project structure

### **Development Phase**
- [ ] Build video player controls (play, pause, seek, speed, fullscreen)
- [ ] Implement scene navigation (9 chapters)
- [ ] Add interactive elements (clickable UI, tooltips)
- [ ] Implement all animations (fade, slide, scale, pulse, etc.)
- [ ] Add voiceover sync or text captions
- [ ] Build responsive layout (desktop, tablet, mobile)
- [ ] Add keyboard navigation
- [ ] Optimize performance (lazy load, 60fps animations)

### **Polish & Testing**
- [ ] Cross-browser testing (Chrome, Firefox, Safari, Edge)
- [ ] Mobile device testing (iOS, Android)
- [ ] Accessibility audit (keyboard nav, screen readers, ARIA)
- [ ] Performance testing (load time <2s, size <5MB)
- [ ] Add analytics tracking (scene views, completion rate)
- [ ] Test all interactive elements
- [ ] Proofread all text/captions

### **Integration**
- [ ] Embed in landing page (dedicated section)
- [ ] Add CTA after demo completion
- [ ] Test landing page integration
- [ ] Set up video hosting (if using video files)
- [ ] Configure CDN for assets

---

## 🚀 Cursor IDE Implementation Instructions

### **Step 1: Generate Base Structure**

**Prompt for Claude Code**:
```
Create an interactive HTML5 product demo for VertexOps with the following structure:

1. A custom video player interface with:
   - Play/pause button
   - Progress bar with chapter markers (9 chapters)
   - Speed controls (0.5x, 1x, 1.5x, 2x)
   - Fullscreen toggle
   - Chapter navigation sidebar

2. Scene data structure in JSON with 9 scenes:
   - Scene 1: Login (0-20s)
   - Scene 2: Dashboard (20-45s)
   - Scene 3: Infrastructure (45-75s)
   - Scene 4: Incidents (75-120s)
   - Scene 5: ChatOps (120-155s)
   - Scene 6: Cost (155-180s)
   - Scene 7: Compliance (180-205s)
   - Scene 8: Notifications (205-225s)
   - Scene 9: Integrations (225-260s)

3. Each scene should have:
   - Screenshot background (placeholder initially)
   - Voiceover text (display as captions)
   - Interactive hotspots for key UI elements
   - Smooth transitions between scenes

4. Use VertexOps design system:
   - Primary color: #0A66C2
   - Font: Inter
   - Clean, professional SaaS aesthetic

Generate the complete file structure with:
- index.html (demo player)
- styles/demo.css (styling)
- scripts/demo-controller.js (main logic)
- data/scenes.json (scene definitions)
```

### **Step 2: Implement Animations**

**Prompt for Claude Code**:
```
Add smooth animations to the VertexOps demo:

1. Scene transitions:
   - Fade out current scene (0.5s)
   - Fade in next scene (0.5s)
   - Crossfade for seamless transition

2. Interactive elements:
   - Hover effects: scale(1.05), shadow increase
   - Click effects: ripple animation
   - Tooltips: fade in on hover (0.2s delay)

3. Metric animations:
   - Counter animations (count from 0 to target value)
   - Progress bars filling
   - Donut chart segments drawing in

4. UI element animations:
   - Buttons: slide up from bottom
   - Panels: slide in from right/left
   - Modals: scale in from center with backdrop
   - Notifications: slide down from top

Use CSS animations and JavaScript for complex sequences.
Ensure all animations run at 60fps.
Add fallbacks for reduced motion preferences.
```

### **Step 3: Add Interactivity**

**Prompt for Claude Code**:
```
Make the VertexOps demo fully interactive:

1. Clickable UI elements in screenshots:
   - Buttons should respond to clicks
   - Links should show hover states
   - Forms should have focus states
   - Tooltips appear on hover

2. Scene navigation:
   - Click chapter markers to jump to scene
   - Keyboard shortcuts (Space = play/pause, Arrow keys = skip)
   - Auto-advance to next scene when current finishes

3. Interactive demonstrations:
   - Scene 3: Click topology nodes to show resource details
   - Scene 4: Click "Approve Remediation" to trigger success animation
   - Scene 5: Type in ChatOps input (simulated)
   - Scene 6: Hover cost chart segments to show amounts
   - Scene 9: Click "Connect" to show modal

4. Track user interactions:
   - Log which scenes users watch
   - Track completion rate
   - Measure interaction engagement

Ensure all interactions feel smooth and responsive.
```

### **Step 4: Optimize for Production**

**Prompt for Claude Code**:
```
Optimize the VertexOps demo for production deployment:

1. Performance:
   - Lazy load screenshots (only load visible scene)
   - Compress all images (WebP format, <200KB each)
   - Minify CSS and JavaScript
   - Enable Brotli compression
   - Target bundle size: <2MB total

2. Accessibility:
   - Add ARIA labels to all interactive elements
   - Implement keyboard navigation (Tab, Enter, Space, Arrows)
   - Provide text transcripts for each scene
   - Ensure color contrast meets WCAG 2.1 AA
   - Test with screen readers

3. Responsive design:
   - Desktop: full interactive demo (1920x1080)
   - Tablet: simplified with touch controls (1024x768)
   - Mobile: vertical layout, essential interactions only (375x667)

4. Browser compatibility:
   - Test on Chrome, Firefox, Safari, Edge
   - Add polyfills for older browsers
   - Fallback for browsers without JS

5. Analytics:
   - Track play rate, completion rate, scene drop-off
   - Measure average watch time
   - Track CTA clicks after demo
```

---

## 📊 Success Metrics

**Engagement Metrics** (to track post-deployment):
- **Play Rate**: % of landing page visitors who start demo
  - Target: 40%+
- **Completion Rate**: % who watch entire demo
  - Target: 60%+
- **Average Watch Time**: Mean duration watched
  - Target: 2+ minutes (out of 4-minute demo)
- **Scene Drop-off**: Which scenes lose viewers
  - Goal: Identify weak points for improvement
- **CTA Click Rate**: % who click "Start Trial" after demo
  - Target: 15%+

**Quality Metrics**:
- Performance: <2s load time, 60fps animations
- Accessibility: WCAG 2.1 AA compliant
- Cross-browser: Works on 95%+ browsers
- Mobile: Functional on iOS & Android

---

## 🎬 Next Steps

1. **Review & Approve**: Confirm the demo flow and content
2. **Gather Assets**: Collect all UI screenshots (or create mockups)
3. **Record Voiceover**: Professional or AI-generated (ElevenLabs, Murf.ai)
4. **Implement in Cursor**: Use Claude Code CLI with the prompts above
5. **Test & Iterate**: QA on multiple devices and browsers
6. **Deploy**: Embed in VertexOps landing page
7. **Monitor**: Track engagement metrics and optimize

**Estimated Development Time**: 3-5 days (single developer)

**Tools Needed**:
- Cursor IDE with Claude Code
- Screenshot tool (for UI mockups)
- Voiceover tool (optional: ElevenLabs, Murf.ai)
- Image optimization (Squoosh, TinyPNG)
- Browser testing (BrowserStack or local)

---

**End of Prompt - Ready for Cursor IDE + Claude Code CLI**

Copy the prompts in Steps 1-4 directly into Cursor's Claude Code interface to generate the complete interactive demo!
