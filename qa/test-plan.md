# Test Plan – Group 21

## 1. Objective

The objective of this test plan is to evaluate the usability, accessibility, and performance of the Habit Tracker application developed by other teams.

---

## 2. Scope

The following components are tested:

- Group 17: Main Dashboard (calendar, activity tracking, goals)
- Group 18: Mobile-first responsive UI
- Group 19: Data visualization (charts and insights)

---

## 3. Testing Approach

Testing is performed using:

- Manual testing (user interaction)
- Persona-based testing (Beginner User)
- Tool-based testing (Lighthouse)

Focus areas:
- Usability (navigation, clarity)
- Accessibility (labels, contrast)
- Performance (load time, responsiveness)

---

## 4. Testing Tools

- Lighthouse (Chrome DevTools)
- AXE DevTools (optional)
- Manual UI inspection

---

## 5. Testing Context

- The system is partially implemented
- Some features (e.g., goals, insights) are incomplete
- Testing is performed using mock data
- Backend integration is not fully available

---

## 6. Defect Reporting

Issues identified during testing are reported using GitHub Issues.

Reported Issues:
- #297 – Dashboard navigation and usability issues
- #299 – Accessibility issues (labels and contrast)
- #300 – Performance issues (large JavaScript size)

---

## 7. Limitations

- Results may not fully reflect final system behavior
- Some features could not be fully tested due to incomplete implementation

---

## 8. Test Execution & Results (Member 1 - Salma Benlemlih)

### 8.1 Accessibility Audit (AXE & Lighthouse)
- **Target:** Group 17 Dashboard Components.
- **Action:** Ran automated Lighthouse scans on the Navigation Bar and Goal Cards.
- **Findings:** Identified critical missing `aria-label` tags on the "Add Activity" buttons.
- **Status:** Logged as Issue #299.

### 8.2 Manual Navigation Test
- **Target:** Group 18 Responsive UI.
- **Action:** Performed a "Keyboard-Only" navigation test (Tab key) to check for focus traps.
- **Findings:** Focus ring is missing on the mobile menu toggle; navigation is difficult for screen-reader users.
- **Status:** Report submitted to Group 18.

### 8.3 Evidence of Implementation
- **Tools Used:** Chrome DevTools, AXE-core extension.
- **Context:** Tests performed using static mock data as per Section 5.
