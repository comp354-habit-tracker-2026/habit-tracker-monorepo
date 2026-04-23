## Group 17 – Dashboard Testing

### TC-10: Dashboard Usability

Steps:
1. Open dashboard
2. Observe layout and sections

Expected:
Dashboard should be intuitive and easy to use

Actual:
Partially successful

Notes:
Main sections are visible, but layout is not intuitive for beginner users.

Persona: Beginner User

UX Issues:
- No clear main action (e.g., Add Habit button)
- Navigation is not prominent
- Layout feels overwhelming

Accessibility Issues:
- Weak visual hierarchy
- Small navigation elements

Evidence:
See qa/evidence.md

### TC-11: Accessibility & Performance Audit (Lighthouse)

Tool: Lighthouse (Chrome DevTools)

Steps:
1. Open dashboard
2. Run Lighthouse audit

Expected:
High accessibility and performance scores

Actual:
- Performance: 49
- Accessibility: 81

Issues:
- Large JavaScript size (~4MB)
- Unused JavaScript code
- Missing form labels
- Low contrast elements
- Layout shifts (CLS issues)

Notes:
Performance is low due to heavy frontend and lack of optimization.

Evidence:
See qa/evidence.md


### Requirements Traceability

Related Requirements:
- Personas (#138)
- Accessibility Audit (#152)
- Usability Testing (#130)
- UX Audit (#136)
### Reported Issues

The following issues were identified and reported:

- #297 – Dashboard navigation and usability issues
- #299 – Accessibility issues (labels and contrast)
- #300 – Performance issues (JavaScript size)

## Group 18 – Mobile UI Testing

### TC-20: Mobile Responsiveness

Steps:
1. Open the app in Chrome
2. Toggle mobile view (iPhone SE / iPhone 12)
3. Navigate through all pages

Expected:
UI should adapt correctly to mobile screen sizes

Actual:
UI fits well on screen, but is too left aligned.

Notes:
Screenshots captured for each page, both landscape and portrait.

Persona: Beginner User

UX Issues:
- Layout shifts on scrolling
- Some elements too close together

Accessibility Issues:
- Text too small on larger phones/views/
- Navigation elements are hard to tap

Evidence:
- https://github.com/comp354-habit-tracker-2026/habit-tracker-monorepo/pull/327
  

### Related Requirements
- Personas (#138)
- Accessibility Audit (#152)
- Usability Testing (#130)
- UX Audit (#136)

## Group 19 – Data Visualization Testing

### TC-30: Chart Usability and Clarity
Steps:
1. Open data visualization section.
2. View activity pie charts and bar charts on both desktop and mobile views.
3. Attempt to toggle between different visualization modes.

Expected:
The charts should have distinct colors for each activity being displayed. There should be an intuitive way to swap between data views.

Actual:
The data is displayed in a very clear an intuitive manner where most users would understand what they are looking at. The problem arises when the toggling to different views as there is no such button that can swap between views.

Notes:
Missing button to toggle different views of data for different dates!

Persona: Beginner User

UX Issues:
- Bar charts lack clear axis labels for "sessions" and "activity".
- No navigation or toggle elements to change chart types.
- Data insight is a little cluttered with the bar charts. The legend (right side) isnt necessary when all the necessary data is already in the bar chart

Accessibility Issues:
-  Lower contrast ratio detected in the desktop version of the chart types
-  the list items in the legend (right side) are not properly contained in parent elements which may affect screen readers.

Evidence:
See qa/evidence.md

### TC-31: Accessibility and Perfomance Audit 
Tool: Lighthouse (Chrome DevTools)

Steps:
1. Open chart components
2. Run Lighthouse audit on mobile and desktop

Expected:
High accessibility and performance scores

Actual:
- Performance: Mobile (41-46), Desktop (73-75)
- Accessibility: Mobile (100), Desktop (94-97).

Issues:
- Very slow load times on mobile, with First Contentful Paint taking up to 14 seconds.
- Enormous network payloads exceeding 5MB due to unoptimized assets.
- Significant unused JavaScript (est. savings >2.5MB)
- Low contrast elements and improper HTML list structures

Notes:
Performance is low due to heavy network payloads and lack of optimization.

Evidence:
See qa/evidence.md

The following issues are also applicable for group 19:
- #299 – Accessibility issues (labels and contrast)
- #300 – Performance issues (JavaScript size)
