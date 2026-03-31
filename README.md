# habit-tracker-monorepo

## Stale PR Labeler

This repo uses an automated GitHub Action to manage stale pull requests.

### How it works
Pull requests with no activity (comments, commits, or reviews) for **14 days**
are automatically labeled as `stale` and the author is notified via a comment.
The stale label is removed if the PR becomes active again.

### Exemption Label
If a PR should **not** be marked as stale (e.g. it's intentionally on hold),
add the `do-not-stale` label to it. The action will skip that PR entirely.
