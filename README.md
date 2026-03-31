# habit-tracker-monorepo




## Code owners PR Review Assignment
This repo contains a `CODEOWNERS` file that assigns groups to a PR when it is created.
Reviewers can be set by a group to protect their features from breaking during shared file merges.

### How it works
When a pull request is created, codeowner group(s) are automatically assigned to review the pull request.
The groups are relevant to files changed in the pull request.
The pull request must receive a review from a member of the assigned group(s) before it can be closed.

### How to add a codeowner
Ownership of a folder or a file can be set by adding a line inside the `CODEOWNERS` file.
A single line in the `CODEOWNERS` file can target either a (set of) file(s) or a folder.

The `CODEOWNERS` file has some assignments prepared that need specifications on file and folder names, placeholdered by `{...}`.
Otherwise, teams can specify other files and folders by themselves using documentation provided below.

Team names are simply `Group-xx` for groups 1-4 and `group-xx` for groups 5-27.
Do be mindful of capitalization when assigning ownership.
The lines for assigning codeowners are as follows:

#### Folder ownership:
`/{path}/{from}/{root}/{folder}/ @comp354-habit-tracker-2026/{team}`

#### File ownership:
`/{path}/{from}/{root}/{file}.{ext} @comp354-habit-tracker-2026/{team}` for single files.

`/{path}/{from}/{root}/*.{ext} @comp354-habit-tracker-2026/{team}` for all files of the same extension.

#### Multiple team ownership:
`/{path}/{from}/{root}/{folder}/ @comp354-habit-tracker-2026/{team1} @comp354-habit-tracker-2026/{team2}`
for a folder shared between 2 groups. This can also be done with files.
Setting ownership through multiple lines will not add but override ownership.
This will require 

Further documentation can be found [here](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners).