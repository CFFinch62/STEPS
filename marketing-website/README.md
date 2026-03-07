# Steps Programming Language - Marketing Website

This folder contains the marketing website for the Steps Programming Language, designed to introduce CS educators to this educational programming tool.

## Overview

The marketing website showcases Steps' unique features and benefits for teaching programming fundamentals. It's designed to be informative, visually appealing, and easy for educators to navigate.

## Website Structure

```
marketing-website/
├── index.html              # Homepage with overview and value proposition
├── features.html           # Detailed feature explanations
├── getting-started.html    # Installation and setup guide
├── examples.html           # Code examples and tutorials showcase
├── css/
│   └── styles.css          # Complete stylesheet with responsive design
├── images/                 # (placeholder for images/screenshots)
├── js/                     # (placeholder for future interactivity)
└── README.md              # This file
```

## Pages

### 1. Homepage (index.html)
**Purpose:** Introduce Steps and capture educator interest

**Sections:**
- Hero section with value proposition
- "Why Steps?" - Core benefits
- Building metaphor explanation
- Code comparison examples
- Educator benefits
- Quick start preview
- Testimonials
- Call-to-action

**Target:** First-time visitors, educators researching educational programming languages

### 2. Features (features.html)
**Purpose:** Deep dive into what makes Steps unique

**Sections:**
- Architectural metaphor
- English-readable syntax
- Enforced decomposition
- Educational error messages
- Complete development environment
- Comprehensive tutorial system
- Design philosophy

**Target:** Educators evaluating whether Steps fits their curriculum

### 3. Getting Started (getting-started.html)
**Purpose:** Help educators install and begin using Steps

**Sections:**
- Prerequisites
- Step-by-step installation
- First program walkthrough
- Development tools overview (CLI, REPL, IDE)
- Learning path recommendations
- Teaching tips
- Troubleshooting

**Target:** Educators ready to try Steps with their students

### 4. Examples (examples.html)
**Purpose:** Show real Steps code and project structure

**Sections:**
- Simple programs (Hello World)
- Intermediate applications (Tip Calculator, Price Calculator)
- Syntax demonstrations (loops, conditionals, data structures)
- Tutorial lesson overview
- Project ideas for students

**Target:** Educators wanting to see actual code before committing

## Design Features

### Visual Design
- **Color Scheme:**
  - Primary: Blue (#2563eb) - Trust, education
  - Secondary: Green (#10b981) - Success, growth
  - Accent: Amber (#f59e0b) - Attention, highlights
  - Gradient: Purple gradient for hero sections

- **Typography:**
  - Headings: System font stack (clean, professional)
  - Code: Monospace font stack (SF Mono, Monaco, Consolas)
  - Body: Sans-serif for readability

- **Code Presentation:**
  - Syntax-highlighted code blocks
  - Mac-style code windows with colored dots
  - Dark theme for code (reduces eye strain)
  - Scrollable for long examples

### Responsive Design
- Mobile-first approach
- Breakpoints at 768px and 480px
- Flexible grid layouts
- Readable font sizes across devices

### User Experience
- Sticky navigation for easy access
- Smooth scrolling for in-page links
- Clear call-to-action buttons
- Consistent section layout
- Visual hierarchy through spacing and typography

## Key Messages

### For Educators
1. **Visible Structure** - Students can literally see program organization
2. **Forced Decomposition** - No monolithic code possible
3. **English Syntax** - Lower cognitive load, focus on logic
4. **Educational Errors** - Messages that teach, not frustrate
5. **Complete Tooling** - REPL, IDE, CLI all included
6. **Ready to Teach** - Tutorial and examples included

### Value Propositions
- Teaches programming concepts without syntax overhead
- Makes abstract concepts (modularity, decomposition) tangible
- Students develop good habits from day one
- Concepts transfer to any mainstream language
- Reduces instructor time explaining cryptic errors

## Content Strategy

### Tone
- Professional but approachable
- Educational and informative
- Enthusiastic without being hyperbolic
- Evidence-based claims
- Educator-to-educator voice

### Key Differentiators
1. **Architectural Metaphor** - Unique teaching approach
2. **Mandatory File Structure** - Physical enforcement of decomposition
3. **English Syntax** - True readability, not just "clean" code
4. **Educational Design** - Built for teaching, not production

## Technical Notes

### Browser Compatibility
- Modern browsers (Chrome, Firefox, Safari, Edge)
- CSS Grid and Flexbox for layouts
- CSS Variables for theming
- No JavaScript required (pure HTML/CSS)

### Performance
- Minimal external dependencies
- Optimized CSS (single file)
- No large images or media files
- Fast load times

### Accessibility
- Semantic HTML structure
- Sufficient color contrast
- Readable font sizes
- Keyboard navigation support
- Screen reader friendly

## Future Enhancements

### Potential Additions
- [ ] Screenshot gallery of IDE and examples
- [ ] Video walkthrough/demo
- [ ] Interactive code playground (REPL in browser)
- [ ] Downloadable lesson plans for educators
- [ ] Community forum integration
- [ ] Blog for teaching tips and updates
- [ ] Case studies from actual classrooms
- [ ] Comparison table with other educational languages

### Content Improvements
- Add real testimonials from beta testers
- Include metrics (lines of code saved, student performance)
- Create downloadable PDF guide
- Add FAQ section
- Include syllabus integration examples

## Deployment

### Local Testing
Simply open `index.html` in a web browser to view the site locally. All pages are linked and functional without a server.

### Hosting Options
- **GitHub Pages:** Free, easy deployment from repository
- **Netlify/Vercel:** Automatic deployment, CDN, free tier
- **Traditional Web Host:** Any host supporting static HTML

### Deployment Steps (GitHub Pages)
1. Create `gh-pages` branch or use docs folder
2. Copy marketing-website contents
3. Enable GitHub Pages in repository settings
4. Site will be available at `https://CFFinch62.github.io/Steps/`

## Maintenance

### Regular Updates
- Keep installation instructions current
- Update tutorial lesson count if expanded
- Add new examples as they're created
- Refresh testimonials periodically
- Update version numbers and badges

### Content Review
- Check all links quarterly
- Verify code examples still work
- Update screenshots if IDE changes
- Review and update browser compatibility

## Contributing

When updating the website:
1. Maintain consistent tone and style
2. Test on multiple devices/browsers
3. Ensure all internal links work
4. Keep code examples accurate and tested
5. Update this README if structure changes

## Contact & Feedback

For questions about the website or Steps:
- Check the main project README
- Open an issue on GitHub
- Contact project maintainers

---

**Note:** This website is designed to be viewed alongside the actual Steps documentation in `/docs/`. Links in the footer point to those documentation files for educators who want deeper technical details.
