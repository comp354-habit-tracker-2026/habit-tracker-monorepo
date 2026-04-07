### Scope:

### Requirements / Acceptance Criteria:

---

### QA Checklist
- [x] **Tests Passing:** All automated tests run successfully before merge. *(N/A - Documentation only)*
- [x] **Test Coverage:** PR achieves/maintains a minimum overall test coverage of 70%. *(N/A - Documentation only)*
- [x] **Code Quality:** The code is clean, readable, and contains no unnecessary comments or commented-out code.
- [x] **Standards:** Commits follow the standard format, and the code adheres to project coding standards.
- [x] **Vulnerability Scans:** Dependency updates have been checked for vulnerabilities using scanning tools. *(N/A)*

### DevOps Checklist
- [x] **Pipelines:** GitHub Actions automated builds and deployment workflows execute successfully.
- [x] **Secrets Management:** Environment variables and secrets are handled securely without exposing them in the repository. *(N/A)*

### Related Issues:

### Validation Steps (Provide step-by-step instructions to clearly describe how to verify each item in the Definition of Done for the related issue):

---

An example of validation steps for Issue 55:
1. Check out this branch locally: `git checkout feature/issue-55-global-templates`
2. Navigate to the `.github/ISSUE_TEMPLATE` directory and verify the `global_issue.md` file exists and contains the Scope, Requirements, and Definition of Done sections.
3. Navigate to the `.github/PULL_REQUEST_TEMPLATE` directory and verify the `pull_request_template.md` file exists.
4. Open the `pull_request_template.md` file and confirm it includes the specific PR requirements (70% test coverage, passing tests, cross-team coordination).
5. On GitHub, attempt to open a new dummy Issue and a new dummy Pull Request on this branch to verify that the templates render correctly in the GitHub UI.
