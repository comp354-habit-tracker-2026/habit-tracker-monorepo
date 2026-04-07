# Testing Strategy

## Overview

This document describes the testing strategy used by Group 21 (UX Research & Accessibility) to evaluate the UIs of Groups 17, 18, and 19.

## Persona-Based Testing (#138)

Testing was conducted using the personas developed in Milestone 1, which simulate real-life users interacting with the system.

Each test is performed from three distinct user profiles:

1. Beginner users
2. Intermediate users
3. Advanced users

(These profiles are based on the user’s level of experience with the application.)

This approach helps evaluate:

1. Ease of navigation
2. Clarity of information
3. Overall user satisfaction


## Usability Testing (#130)

Usability was assessed through direct interaction with each UI, focusing on how easily users can complete tasks.

We evaluate:

1. Navigation (how intuitive the interface is)
2. Layout (whether content is logically organized)
3. Readability (clarity and understandability of text)
4. User flow (whether users know what actions to take)

Through this process, we identify:

1. Confusing elements
2. Slow or inefficient interactions
3. Unclear or incomplete features


## Accessibility Testing (#152)

Following core WCAG principles, we evaluate:

1. Color contrast
2. Text readability
3. Responsive design
4. Keyboard accessibility

We use the following tools:

* Lighthouse (accessibility and performance reports)
* AXE DevTools (accessibility issue detection)


## UX Audit (#136)

A structured UX audit is conducted to assess overall design quality beyond basic usability.

This includes:

1. Consistency across layouts
2. Visual hierarchy
3. System feedback (e.g., loading states, errors)
4. Overall perceived user experience

All issues identified are documented and tracked as GitHub issues.


## Testing Methods

### Manual Testing

We manually interact with the UI to simulate real user behavior and identify usability issues.

### Automated Tools

We use:

1. Lighthouse → performance and accessibility analysis
2. AXE → accessibility issue detection


## Testing Context

Testing is performed under the following conditions:

1. Some features may use mock data
2. Some components may be incomplete
3. The UI may not be fully integrated

These limitations are considered during evaluation.


## Testing Output

Testing produces:

1. Test cases (`qa/test-cases.md`)
2. Screenshots (`qa/evidence/`)
3. GitHub issues for identified problems
4. UX improvement recommendations

All results are linked to relevant issues (#138, #152, #130, #136) to ensure traceability.
