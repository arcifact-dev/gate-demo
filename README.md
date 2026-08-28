# gate-demo

A working GitHub Actions setup with a required check that can pass while
the work it names fails. Three open pull requests demonstrate it, each
with a live result you can look at now.

**Synthetic repository, production GitHub App.** The workflow is written
to be representative rather than realistic. The App analysing it is the
same one a customer installs.

---

## The two-minute version

Open [PR #1](https://github.com/arcifact-dev/gate-demo/pull/1) and look
at the checks.

GitHub says **`all tests passed` succeeded**. Arcifact Gate says **the
approved warrant is broken**. Both are correct, and that gap is the
entire product.

The pull request removes `windows-tests` from the aggregate's `needs`.
Every check is green. Nothing in the GitHub interface indicates that the
required check now proves less than it did an hour ago.

---

## The three scenarios

| | what the pull request does | required check says | Gate says |
|---|---|---|---|
| [#1](https://github.com/arcifact-dev/gate-demo/pull/1) | drops `windows-tests` from the aggregate, framed as a CI speed-up | `all tests passed` **success** | **approved warrant broken** |
| [#2](https://github.com/arcifact-dev/gate-demo/pull/2) | narrows the aggregate to `pull_request` only | `all tests passed` **success** | **weakened by this change** |
| [#3](https://github.com/arcifact-dev/gate-demo/pull/3) | the same drop as #1, and its own CI fails for an unrelated reason | `all tests passed` **failure** | **also a reduction** |

**#1 and #2 are the point.** The required check reports success and the
change still reduces what merging establishes. That is the gap this tool
exists to close, and nothing in the platform reports it.

**#3 is honest about a limit rather than a win.** It makes the same
change as #1, so Gate reports the same reduction. What differs is that
its own CI happens to fail, so the platform blocks the merge anyway. Gate
adds nothing you would not already have known from the red check.

An earlier version of this table described #3 as a case where Gate has
nothing to say. That was wrong: Gate says the same thing about #3 as
about #1, because it is the same change. The corrected claim is narrower
and it is the true one.

---

## Why #1 and #2 differ from each other

**#1 breaks a declared warrant.** This repository has a
[`WARRANT`](WARRANT) file naming what `all tests passed` is supposed to
cover. Removing `windows-tests` contradicts a claim the maintainer wrote
down, so Gate can be specific about which promise is no longer kept.

**#2 has no declaration to break.** Conditioning the aggregate on
`pull_request` means it does not run in a merge queue, which delivers
`merge_group` instead. Gate reports that as a weakening rather than a
violation, because nobody declared what should happen there.

The difference matters. A structural fact is not a defect until somebody
says what the job is for, and only the maintainer can say.

---

## What Gate does not claim

It does not say these pull requests are bad. Dropping a Windows job may
be exactly the right decision, and if `windows-tests` is deliberately
advisory the [`WARRANT`](WARRANT) file can say so and Gate will stop
asking.

It also does not ask to be a required check here. Nothing merges or
fails on its opinion.

---

## Try it on your own repository

No installation and no account:

```
https://arcifact.io/r/<org>/<repo>
```

Any public repository. Static analysis, nothing executed, and unknown
stays unknown.

To watch it on your own commits, fork this repository, install the App
on the fork, and reopen any of the three pull requests against your copy.

---

## What is in here

- `.github/workflows/ci.yml` four jobs and one aggregate, written so
  the aggregate is genuinely load-bearing
- `WARRANT` machine-readable declaration of what the required check is
  meant to cover, which is what makes #1 a broken promise rather than an
  observation

---

## Links

- [What Gate does](https://arcifact.io/gate)
- [How it reasons](https://arcifact.io/gate-technical)
- [Nine undocumented GitHub Actions behaviours](https://arcifact.io/actions-semantics)
- [Verify a record yourself](https://arcifact.io/verify)
