# Overview

This document describes the testing strategy used by Group 21 (UX Research & Accessibility) to evaluate Grooups 17, 18 and 19s UIs.


## Persona Based Testing (#138)

Testing was done using the different personas devloped in Milestone 1 which mimics real-life users interacting with the system.
Each Test is performed from 3 distinct user profiles:

1. Beginner Users
2. Intermediate USers
3. Advanced USers

(Proficency skill based on their experience using the app)

This in turn helps evaluate:

1. Ease of Navigation
2. Clarity of Information
3. User satisfaction

## Usability Testing (#130)

Usability was assesesed through direct interaction with each UI, evaluating the ease of completion of each task.

We evaluate: 

1. Navigation (How easy it is to navigate)
2. Layout (Does the layout make sense?)
3. Readability(Is the text clear and understanable?)
4. User flow (Do users know what to do?)

By doing this we indentify: 

1. Elements that are confusing
2. Slow interactions
3. Unclear features

## Accesibility Tracing (#152)

Following the core principles of WCAG basics, we check:

1. Colur Contrast
2. Text Readability
3. Responsiveness Design
4. Keyboard Accesibility

Using Lighthouse and AXE DevTools

## UX Audit (#136)
A structured UX audit was conducted to assess design quality beyond basic, covering:

1. Consistency in layout
2. Visual hierarchy
3. System feedback
4. Overall perceived quality of the user experience

All issues identified were documented as GitHub issues

## Testing Methods

We manually interacted with the UI

and the automated tools consist of:

1. Lighthouse for performance and accesibility
2. AXE for accesebility


## Testing Context
Testing is performed under the following conditions:

1. Some features may use mock data
2. Some components may be incomplete
3. UI may not be fully integrated
   
These limitations are considered in evaluation

## Output Testing

Testing produces:

1. Test cases (qa/test-cases.md)
2. Screenshots (qa/evidence/)
3. GitHub issues for identified problems
4. UX improvement recommendations
   
All results are linked to relevant issues (#138, #152, #130, #136)





