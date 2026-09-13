# Google Drive → Facebook Pages Automation

## Master Implementation Specification for Antigravity

------------------------------------------------------------------------

# 1. Executive Summary

Build a fully automated pipeline that takes AI-generated videos already
sitting in the user's Google Drive (one folder per Facebook Page,
synced from the user's PC) and posts them automatically to the
matching Facebook Page on a schedule, forever, with no PC, server, or
browser needing to stay open or powered on at run time.

This is a new, independent project — its own GitHub account, its own
Google Cloud project and service account, its own repository. It
follows the same proven pattern as the already-built Google Drive →
YouTube automation (Drive service account for reading source files,
GitHub Actions + cron-job.org for scheduling, per-destination
isolation, duplicate-protected SQLite tracking), but does not read
from, depend on, or require access to that other project's repository,
account, or credentials. Everything needed to build this is contained
in this document.

The one deliberate difference from that pattern: Facebook Pages
administered by the same personal Facebook identity are treated as one
group sharing one setup, not isolated one-by-one. Section 4 explains
why.

------------------------------------------------------------------------

# 2. Non-Negotiable Rules

1.  Antigravity performs every technical step itself: creating the
    Meta App, requesting permissions, writing all code, creating the
    repository, setting GitHub Secrets, configuring the workflow,
    configuring cron-job.org, and clicking through Meta's App Review
    submission form. The user does not do any of this.
2.  The user's role is strictly limited to actions that require his
    own identity and cannot legally or technically be delegated:
    logging into his own Facebook account, clicking "Allow" on a
    permission screen, completing 2FA/CAPTCHA if Facebook asks for it,
    and — only if Meta's business verification requires it — providing
    real business identity details (business name, address, and
    possibly a document). Nobody else can supply these on his behalf.
    If Antigravity is unsure whether a step needs the user's identity,
    it must pause and ask rather than guess.
3.  Do not build or suggest a Business Manager / System User setup.
    The user has explicitly rejected this path. Use the personal
    Facebook Login for Business flow: the user's own personal account
    is Admin on all target Pages, so one login grants access to all of
    them at once. A Business Manager may still be created automatically
    as part of registering the Meta App if Meta's current app-creation
    flow requires it, but no Page is added to it as a claimed asset,
    and no System User is created.
4.  Do not require the user's PC or phone to remain on, connected, or
    logged into anything for the automation to run. The PC only needs
    to be on when the user is adding new finished videos to the synced
    Drive folder — a separate concern from posting time.
5.  Create a dedicated Google Cloud Service Account for this project's
    Drive access. This is a new, independent credential — not shared
    with any other project. Only new folder-sharing (Share → paste the
    service account email, Viewer role) is needed per Page.
6.  Every Page gets its own Drive folder, its own row in the tracking
    database, and its own daily upload counter — even Pages that share
    one Meta App and one login. One Page's failure, rate limit, or
    scheduling must never block or delay another Page's uploads.
7.  Never post the same video file to more than one Page.
8.  The AI-disclosure question (Section 9) must be resolved and
    recorded once, during onboarding — not re-decided or re-checked on
    every scheduled post. Unlike YouTube, there is no confirmed simple
    API field for this; see Section 9 for exactly what to do.
9.  Do not silently retry a failed upload forever. Cap retries, then
    stop and log clearly.
10. Do not delete or move the user's source files in Drive automatically.
11. Never commit a token, API secret, or App Secret to source code. All
    credentials live in GitHub Secrets.
12. Do not invent a fixed IP. Standard GitHub-hosted runners use
    changing public IPs; Facebook's API does not require a fixed IP for
    this use case.
13. If Facebook returns an error whose cause is unclear (a permission
    error, an unexpected rejection, a review-status message), stop and
    report the exact error rather than guessing a workaround.
14. Do not ask the user to manually perform technical work Antigravity
    can safely perform itself.
15. Read this entire specification before writing or modifying any
    file. This project is self-contained — do not assume access to,
    or need for, any other repository or account.
16. Route every file to Reels or the classic endpoint based purely on
    that file's own measured duration and aspect ratio (Section 9),
    checked per file at upload time. Never route based on a
    per-Page or per-folder assumption about content length — the
    user's Pages regularly mix short and long videos in the same
    folder.

------------------------------------------------------------------------

# 3. Target Architecture

``` text
[User's PC] --(Google Drive Desktop sync)--> [Google Drive]
                                                    |
                                        (dedicated Service Account,
                                         Viewer access per folder)
                                                    |
                                                    v
[cron-job.org] --(HTTPS ping, scheduled)--> [GitHub Actions workflow]
                                                    |
                                    1. Pick next unposted video
                                       from a Page's Drive folder
                                    2. Upload + publish to that
                                       Facebook Page via Graph API
                                    3. Record result in SQLite
                                    4. Commit DB back to the repo
                                    5. Runner shuts down
```

No server. No VPS. No browser open at run time. No PC on at run time.

------------------------------------------------------------------------

# 4. Page Grouping Model

This is the one place this spec deliberately departs from the
YouTube spec's one-channel-one-of-everything isolation, and
Antigravity must understand why before building anything.

On YouTube, each channel has its own Gmail, so isolating everything
per channel was the only option and also the safest one. On Facebook,
the user administers multiple Pages from a single personal identity,
and Facebook's own permission model reflects that: one login, one
permission grant, one Meta App can cover every Page that identity
administers. Pretending otherwise and building six separate Meta Apps
and six separate App Review submissions for six Pages that already
share the exact same blast radius (if that one Facebook identity has a
problem, all six Pages are affected regardless of how many apps exist)
would add real setup cost — six App Review submissions instead of one —
for no real safety benefit.

**A Page Group is:** every Facebook Page administered by the same
personal Facebook identity. All Pages in a Page Group share:

-   one Meta App
-   one App Review approval
-   one OAuth login/consent event
-   one GitHub repository

Within a Page Group, each individual Page still gets its own:

-   Drive folder
-   Page Access Token (Facebook issues a separate token per Page even
    from one grant)
-   row in the tracking database
-   daily upload counter
-   retry state

So one Page's upload failure, rate limit, or a Facebook-side issue
specific to that Page does not touch its siblings — but the *setup
and login* overhead is paid once per group, not once per Page.

**A new Page Group is created only when** a Page is administered by a
*different* personal Facebook identity than the ones already covered.
That requires its own login/consent event (the existing Meta App can
usually be reused; only a fresh grant is needed), and — to keep the
same blast-radius logic — its own repository.

Today: 6 Pages, 1 identity → 1 Page Group → 1 repository.

------------------------------------------------------------------------

# 5. What the User Provides

-   His personal Facebook login, at the one moment Antigravity opens
    the permission screen.
-   Real business identity details, only if Meta's verification step
    for the App asks for them (business name, address, possibly a
    document).
-   A Google Drive folder per Page, kept populated with finished
    videos via the same PC-synced-folder setup used for YouTube.
-   Per-Page settings: display name, category/tags if wanted,
    posting frequency.

Everything else — the Meta App itself, the App Review submission
text and any required screen recording, the code, the repository, the
GitHub Actions workflow, the cron-job.org schedule, and the Drive
folder-sharing clicks (once he is logged into his own Google account
in that browser session) — is Antigravity's job.

------------------------------------------------------------------------

# 6. Google Drive Requirements

Identical mechanism to the YouTube automation: a Google Drive Desktop
synced folder per Page on the user's PC, mirrored automatically to
Drive. Do not build a second sync mechanism — this already exists.

The folders live under the user's own personal Google account. Access
them using a dedicated Google Cloud Service Account created for this
project (Section 23). Share each Page's folder with that service
account's email (Viewer role) — this is the only Drive-side setup
step needed on the user's part.

The implementation must tolerate partially synced files, non-video
files, and duplicate filenames the same way the YouTube version does.

------------------------------------------------------------------------

# 7. Google Drive File Selection

Same rules as the YouTube spec:

-   Only pick fully synced, valid video files.
-   Never re-select a file already recorded as posted for that Page.
-   Deterministic ordering (oldest file first, by Drive-reported
    creation time, unless configured otherwise) so behavior is
    predictable and testable.
-   Skip and log unsupported files rather than failing the whole run.

------------------------------------------------------------------------

# 8. Upload Pipeline

For each scheduled run, per Page configured to run at that time:

1.  Query that Page's Drive folder for the next unposted file.
2.  If none, log "nothing to post" and exit cleanly for that Page.
3.  Download the file to the runner's temporary storage.
4.  Validate the file (Section 22).
5.  Upload and publish it to that Page via the Facebook Graph API
    (Section 9).
6.  On confirmed success, record the file as posted in the database
    (Section 14) before doing anything else.
7.  Delete the temporary local copy. Never touch the Drive source file.
8.  Commit the database change back to the repository.

------------------------------------------------------------------------

# 9. Facebook Upload Requirements

Raj's source content is short vertical video, which Facebook's Reels
format fits far better — and gets meaningfully more organic reach on
— than a classic Page "video" post. Use the Reels publishing flow as
the primary path, not the older generic video endpoint.

**Primary path — Reels** (for any file that is 9:16, 3–90 seconds,
.mp4):

``` text
1. POST /<PAGE_ID>/video_reels   upload_phase=start
   → returns a video_id and an upload URL
2. Upload the file to that URL (Resumable Upload API)
3. POST /<PAGE_ID>/video_reels   upload_phase=finish
   video_id=<from step 1>
   video_state=PUBLISHED
   title=<...>
   description=<...>
```

Requires a Page Access Token from a person with the `CREATE_CONTENT`
task on the Page, plus `pages_show_list`, `pages_read_engagement`,
`pages_manage_posts`.

**Fallback path — classic Page video** (only for a file that does not
fit Reels — over 90 seconds, or not 9:16):

``` text
POST /<PAGE_ID>/videos
access_token=<PAGE_ACCESS_TOKEN>
title=<...>
description=<...>
fbuploader_video_file_chunk=<handle from Resumable Upload API>
```

Both endpoints and their exact parameter names are the part of this
section most likely to shift between Graph API versions — confirm
against Meta's current Video API and Reels documentation at build
time.

**This is a Facebook platform limit, not a design choice — it cannot
be configured away.** Facebook's Reels API enforces a hard 3–90 second
cap; a video over 90 seconds will be rejected by Facebook's servers if
sent to the Reels endpoint, regardless of what this code does. Note:
Meta has publicly announced merging "video" and "Reels" into one
format for human users posting through the Facebook app/website,
removing length restrictions there — but as of the most recently
updated official Reels Publishing API documentation, that change has
not reached the Graph API's `/video_reels` endpoint, which still
documents the 90-second cap. Do not assume the app-level announcement
applies to this API — verify directly against current developer
documentation, not against consumer-facing news, before changing this
assumption. The classic endpoint above is the only way to post a
longer video to a Page at all — there is no way to force a longer
video through as a Reel at the API level today.
The user's content mix includes both short clips and some longer
videos (5–7 minutes seen in practice). This is not an edge case to
handle defensively — both paths will run regularly. Route purely on
each file's own measured duration and aspect ratio (Section 22), not
on any per-Page or per-folder assumption about "this Page only posts
short content." A single Page's folder may contain a mix of both, and
the code must handle that mix correctly file by file.

**AI disclosure — flagged as unresolved, not solved:** Unlike
YouTube's `containsSyntheticMedia` field, there is no confirmed,
documented field on either endpoint above that lets an app
self-declare AI-generated content for organic Page posts as of this
writing. Meta's public "AI Info" labeling appears to rely on automatic
detection (industry-standard embedded content credentials such as
C2PA metadata) or a manual toggle in Meta's own posting interfaces,
not a documented API parameter. Antigravity must, once, during
onboarding (Section 24) — not on every scheduled run:

1.  Check the current Graph API reference for both endpoints above for
    any newly added disclosure field, and use it if one now exists.
2.  If no such field exists, check whether the video files themselves
    already carry embedded AI-content-credential metadata from the
    generation tool (Seedance, Veo, Kling, Runway) — if so, Meta's
    automatic detection may apply the label without any API call
    needed.
3.  If neither applies, this is an open compliance gap, not a bug to
    silently work around. Record the outcome clearly (in the config
    or a setup note) so the user can see which of the three outcomes
    applied. Make this determination once, not per post — do not
    block daily posting on it once it has been recorded; surface it
    clearly and move on.

------------------------------------------------------------------------

# 10. Facebook Metadata

``` yaml
facebook:
  description_footer: ""
  default_hashtags: []
  title_mode: "filename"
```

Same title-mode philosophy as the YouTube spec — filenames become the
visible caption/title unless configured otherwise, so name source
files meaningfully.

------------------------------------------------------------------------

# 11. Duplicate Protection

Identical principle to the YouTube spec: before uploading, check the
database for that Page + that Drive file ID. If already marked
posted, skip. Only mark posted after Facebook confirms success (a
returned video ID), never before.

------------------------------------------------------------------------

# 12. Retry System

Classify Facebook API errors into retryable (rate limit, transient
5xx, network timeout) and non-retryable (permission revoked, invalid
file, page-level restriction). Retry only the retryable class, with
backoff, up to a capped number of attempts, then stop and log the
failure clearly rather than looping forever.

------------------------------------------------------------------------

# 13. Dry-Run Mode

Must support a mode that performs every step — Drive read, file
validation, metadata preparation — except the actual Facebook API
publish call, and prints exactly what would have been posted and to
which Page. Use this before the first real post and after any code
change.

------------------------------------------------------------------------

# 14. Persistent Database

SQLite, committed to the repository, same approach as the YouTube
spec. One table (or one row-per-Page-per-file design) tracking: Page
ID, Drive file ID, Facebook video ID once posted, timestamp, status,
retry count.

------------------------------------------------------------------------

# 15. Database Commit Safety

Same rule as the YouTube spec: commit the database update immediately
after a confirmed successful post, before any other step, so a crash
later in the run cannot cause a duplicate post on the next run.

------------------------------------------------------------------------

# 16. Recovery After Ambiguous Upload Failure

If the run is interrupted after the Facebook API call was sent but
before the response was confirmed, the next run must check Facebook
directly (list recent videos on that Page) before assuming the post
did not go through, exactly as the YouTube spec requires for its own
ambiguous-failure case. Never assume; verify.

------------------------------------------------------------------------

# 17. Repository Layout

One repository for the whole Page Group (Section 4) — not one per
Page.

``` text
config.yaml          (lists every Page in this group + its settings)
drive_client.py
facebook_client.py
database.py
main.py
requirements.txt
.github/workflows/post.yml
posted_videos.db
```

Never commit: the App Secret, any Page Access Token, the service
account key, or downloaded videos.

Same public-vs-private repository trade-off as the YouTube spec
applies (free unlimited Actions minutes on public vs. a shared
2,000 min/month pool on private) — decide deliberately, don't default
silently.

------------------------------------------------------------------------

# 18. GitHub Actions

One workflow file. It should loop over every Page configured to post
in the current run window, not require a separate workflow file per
Page. Triggered the same way as the YouTube workflow — an inbound
webhook/dispatch call from cron-job.org, not a GitHub-native cron
schedule (for the same reliability reasons already established in the
YouTube spec).

------------------------------------------------------------------------

# 19. Automation Trigger

Identical to the YouTube spec: cron-job.org pings a GitHub repository-
dispatch endpoint on the configured schedule. Each Page in
`config.yaml` carries its own schedule/frequency, evaluated inside the
single workflow run.

------------------------------------------------------------------------

# 20. Upload Frequency

Per-Page configurable daily cap, enforced by the code independent of
whatever Facebook's own platform limits are:

``` text
Page "my_page_1"
Daily limit = 2

Post #1 → allowed
Post #2 → allowed
Post #3 → blocked by guard
```

Facebook's Reels API itself is documented as limited to 30
API-published posts per rolling 24-hour period, per Page. At a
configured 2/day/Page this leaves large headroom, but confirm this
number is still current at build time — Meta revises platform limits
without much notice.

------------------------------------------------------------------------

# 21. Drive Queue Behavior

Same as the YouTube spec: do not require the user to manually move or
rename files after posting. Do not delete source files. An optional
archive-folder feature can come later; keep the first version simple.

------------------------------------------------------------------------

# 22. File Validation

Before upload, confirm: the file is a supported video format, has
non-zero size, and is not still mid-sync (Google Drive sometimes
reports a placeholder before a large file finishes uploading — check
file size stability across a short delay before trusting it).

Also check against the Reels format this file will be routed to
(Section 9): .mp4, 9:16 aspect ratio, 1080×1920 recommended (540×960
minimum), 24–60 fps, 3–90 seconds. A file within these bounds goes
through the Reels path; a file outside them (most likely: longer than
90 seconds) automatically falls back to the classic video endpoint
instead of failing outright. Confirm exact current limits against
Meta's documentation at build time.

The classic endpoint's own limits (file size, duration, format) are
separate and considerably more permissive than the Reels table above
— do not reject a long video for failing the Reels aspect-ratio or
resolution numbers; those numbers only decide routing, they are not a
universal requirement. Check the classic endpoint's own limits only
for files routed to it.

------------------------------------------------------------------------

# 23. Authentication Architecture

## Google Drive

Create a dedicated Google Cloud Service Account for this project.
Share each Page's folder with it (Viewer role). Do not authenticate to
Drive using any Facebook-related credential, and do not depend on any
other project's service account.

## Facebook

Requires the Meta App's own App ID and App Secret, stored as GitHub
Secrets, in addition to the per-Page tokens below.

Use the personal Facebook Login for Business flow, once, for the
whole Page Group:

1.  The user logs into his own personal Facebook account when
    Antigravity opens the permission screen.
2.  He grants the requested permissions (`pages_show_list`,
    `pages_manage_posts`, `pages_read_engagement`, and `publish_video`
    if the current API version still requires it separately), from an
    account with the `CREATE_CONTENT` task on each Page.
3.  Exchange the resulting short-lived User Access Token for a
    long-lived User Access Token (Facebook's token-extension endpoint,
    using the App ID and App Secret) before doing anything else. This
    step is not optional: a Page Access Token derived from a
    short-lived User token is itself short-lived (hours, not months),
    and the automation will silently start failing within hours of
    setup if this step is skipped.
4.  Only from the long-lived User token, call the accounts-listing
    endpoint to receive a Page Access Token for every Page the user
    administers — covering all Pages in this group in one grant, not
    one per Page. A Page token derived this way is effectively
    non-expiring under normal conditions (the user's password
    unchanged, the permission not revoked).
5.  Store every Page's token as its own separate GitHub Secret, named
    to match that Page's `name` field in `config.yaml` (for example,
    `name: my_page_1` → secret `FB_TOKEN_MY_PAGE_1`) — keep them
    addressable per Page for the isolation described in Section 4.

Do not build a Business Manager System User flow. Confirm the exact
current endpoint names on Meta's live documentation at build time —
the mechanism above (short-lived → long-lived exchange → Page token)
is the stable part; exact endpoint paths are the part most likely to
have shifted.

------------------------------------------------------------------------

# 24. First-Setup Onboarding

``` text
1.  Inspect project environment.
2.  Create repository structure.
3.  Implement the configuration system (multi-Page, one Page Group).
4.  Create the Google Cloud project and dedicated service account;
    implement the Drive client.
5.  Implement SQLite state.
6.  Implement the Facebook client and OAuth/login flow.
7.  Implement the upload pipeline.
8.  Implement duplicate protection.
9.  Implement retry logic.
10. Implement the GitHub Actions workflow.
11. Register the Meta App; prepare the App Review submission
    (use-case text, screen recording if required — if you cannot
    produce a screen recording yourself, say so clearly and ask the
    user to record one short screen capture rather than silently
    skipping this part of the submission).
12. Pause for the user's one-time Facebook login + consent.
13. Submit for App Review; wait for approval.
14. Once approved, configure each of the 6 Pages: share its Drive
    folder with the service account, add it to config.yaml.
15. Run automated validation.
16. Run dry-run for all 6 Pages.
17. Fix all errors.
18. Perform one real post, on one Page.
19. Verify the post on Facebook directly.
20. Verify database state.
21. Verify repeat execution does NOT re-post the same file.
22. Only after all tests pass, enable the remaining Pages.
```

Steps 12 and 13 involve a real wait for a human (the user, for login;
Meta, for review) that can span days. Track onboarding progress so
work already done is not repeated or duplicated if the process is
picked back up later.

If App Review is rejected, read Meta's stated reason and fix the
specific issue yourself (a clearer use-case description, a better
screen recording, correcting a permission request) and resubmit —
only pause and ask the user if the rejection reason is something only
he can address, such as a business-verification document issue.

------------------------------------------------------------------------

# 25. Human Actions

The complete list of things only the user can do — everything else is
Antigravity's job:

-   logging into his own personal Facebook account
-   approving the permission/consent screen
-   completing 2FA or CAPTCHA if Facebook requests it
-   providing real business identity details, only if Meta's
    verification step asks for them
-   logging into his personal Google account once, so Antigravity can
    then share each Page's Drive folder with the service account
    itself

If Antigravity encounters a step that seems to require the user but
isn't on this list, it must stop and ask rather than either guessing
or asking the user to do something Antigravity could have done itself.

------------------------------------------------------------------------

# 26. Acceptance Test

### Test A — Dry run

Dry-run for all 6 Pages produces a correct, human-readable plan with
no live Facebook call made.

### Test B — First real post

One real post succeeds on one Page. Verify it exists on that Page
directly (not just a success response from the API).

### Test C — Duplicate protection

Run the automation again immediately. Expected: `Already posted →
SKIP`. No second post.

### Test D — Failure recovery

Simulate a retryable failure and verify retry behavior.

### Test E — Isolation

Simulate a failure on one Page (invalid file, expired token) and
confirm the other 5 Pages in the group still post successfully in the
same run.

### Test F — Secret safety

Repository contains no App Secret, no Page Access Token, no service
account key.

### Test G — Disclosure check

Confirm what actually happened with AI-content labeling on the test
post per Section 9's decision tree, and record which of the three
outcomes applied. Do not mark this test passed on the basis of the
upload succeeding alone.

### Test H — Long-form routing

Post one file over 90 seconds (a real 5–7 minute video, matching what
the user actually produces) and confirm it correctly routes to the
classic video endpoint, not the Reels endpoint, and posts
successfully. Confirm a short file in the same Page's folder still
routes to Reels in the same run. This is not an edge case — both
lengths are regular content and both paths must be verified working,
not just the short one.

### Test I — Token durability

Inspect the derived Page Access Token (Facebook's token-debug tooling)
and confirm it shows as long-lived/non-expiring, not the short
lifetime of an un-exchanged token. Do not consider Section 23's
token-exchange step done on the basis of the post succeeding once —
a short-lived token would also succeed once, then fail hours later.

------------------------------------------------------------------------

# 27. Adding More Pages / Scaling

Adding a Page administered by the **same** personal Facebook identity:
add it to `config.yaml`, share its Drive folder with the existing
service account. No new login, no new App Review.

Adding a Page administered by a **different** personal identity:
treat as a new Page Group (Section 4) — new repository, new one-time
login/consent event (the same Meta App can likely be reused; confirm
at build time whether Meta requires anything additional for a second
identity granting access to the same app).

------------------------------------------------------------------------

# 28. IP / Network Requirement

No fixed IP required. Standard GitHub-hosted runners receive a new
public IP on every run. Facebook's Graph API does not require IP
allowlisting for this use case.

------------------------------------------------------------------------

# 29. Notifications

Same approach as the YouTube spec: notify the user (channel to be
decided — email, or reuse whatever notification method the YouTube
automation already uses) on failures that exhaust retries, and on
App-Review status changes if that can be detected programmatically.

------------------------------------------------------------------------

# 30. Logging

Log every run's decisions per Page: what was selected, what was
posted, what was skipped and why, every error with enough detail to
diagnose without re-running. Never log tokens or secrets.

------------------------------------------------------------------------

# 31. Health Check

A simple way to confirm, on demand, that: the Facebook token(s) are
still valid, the Drive service account still has access to every
configured folder, and the last run per Page completed without error.

If a Page's token is found invalid, notify the user immediately
(Section 29) rather than retrying silently — re-authorization needs
his own login (Section 25) and Antigravity cannot do this step for
him.

------------------------------------------------------------------------

# 32. Configuration Example

``` yaml
page_group: "personal_fb_id_1"
ai_disclosure_status: "pending_determination"  # set once per Section 9's decision tree, during onboarding

pages:
  - page_id: "PAGE_ID_1"
    name: "my_page_1"
    drive_folder_id: "..."
    daily_limit: 2
    description_footer: ""
    default_hashtags: []

  - page_id: "PAGE_ID_2"
    name: "my_page_2"
    drive_folder_id: "..."
    daily_limit: 2
    description_footer: ""
    default_hashtags: []

  # ... remaining 4 pages, same shape
```

------------------------------------------------------------------------

# 33. Code Quality Requirements

Same bar as the YouTube spec: clear function boundaries, no dead code,
no hard-coded credentials or IDs outside `config.yaml`, meaningful
error messages, comments explaining *why* for anything non-obvious
(especially the Section 9 disclosure decision tree and the Section 4
grouping logic, since both are easy for a future reader to
misunderstand).

------------------------------------------------------------------------

# 34. Testing Requirements

Automated tests for: duplicate-protection logic, retry/backoff logic,
config parsing, and the per-Page isolation guarantee (Test E). Manual
verification for the actual Facebook posting and App Review outcome,
since those cannot be meaningfully mocked end-to-end.

------------------------------------------------------------------------

# 35. Security Requirements

All credentials in GitHub Secrets. No token, App Secret, or service
account key ever written to a log, committed to source, or printed in
plaintext in any output the user might paste elsewhere.

------------------------------------------------------------------------

# 36. Dashboard --- Phase 2

Not required for version 1. If built later: per-Page post history,
success/failure counts, and current App/token health, matching
whatever pattern the YouTube dashboard (if built) already uses.

------------------------------------------------------------------------

# 37. Operational Philosophy

Isolate what can genuinely fail independently (each Page's posting)
without over-isolating what is already genuinely shared (one
identity, one login, one app). When a Facebook platform detail is
ambiguous or has changed since this spec was written, check
Facebook's current developer documentation rather than trusting this
document's specifics about version numbers, exact permission names, or
exact endpoint shapes — the architecture and rules in this spec are
the stable part; the API details are the part most likely to have
moved.

------------------------------------------------------------------------

# 38. What NOT to Build

-   No Business Manager, no System User.
-   No separate Meta App per Page within the same Page Group.
-   No manual step handed back to the user that Antigravity could
    perform itself while already authenticated in that browser
    session.
-   No assumption that the AI-disclosure question is solved — Section
    9 must be resolved or explicitly reported as unresolved, not
    skipped.
-   No dependency on any other project's repository, account, or
    credentials. This project is self-contained.

------------------------------------------------------------------------

# 39. Final Implementation Checklist

``` text
[ ] Dedicated Google Cloud project and service account created for this project
[ ] Meta App created and linked as current Facebook flow requires
[ ] App Review submitted and approved
[ ] One login/consent event covers all 6 Pages
[ ] Each Page has its own Drive folder, shared with the service account
[ ] Each Page has its own Page Access Token, stored as its own Secret
[ ] Dry-run works for all 6 Pages
[ ] First real post verified directly on Facebook
[ ] Second run skips the already-posted file
[ ] One Page's simulated failure does not affect the other 5
[ ] Section 9's disclosure decision tree resolved and recorded, not skipped
[ ] A real 5-7 minute video verified routing to the classic endpoint, not Reels
[ ] Page Access Token inspected and confirmed long-lived, not short-lived
[ ] Repository contains no App Secret, Page token, or service account key
```

------------------------------------------------------------------------

# 40. Antigravity Execution Instructions

You are the implementation agent. Read this entire specification
first. This is a self-contained project — do not look for or assume
access to any other repository or account.

Perform every technical step yourself. Pause only for the human
actions listed in Section 25, state clearly what you need and why
when you pause, and resume immediately once it is provided. If you
encounter a decision this spec does not clearly answer, stop and ask
rather than guessing — especially anything touching Section 9's
disclosure question, Section 23's token-lifetime assumption, or
Section 24's current App Review requirements, since all three are
explicitly flagged in this spec as things that may have changed since
it was written.

Inspect the existing environment before creating or modifying
anything. Do not destroy useful existing work.

------------------------------------------------------------------------

# 41. Definition of Done

All 6 Pages are posting automatically, on schedule, from their own
Drive folders, with no duplicate posts, no PC or browser required at
run time, every credential safely stored, and Section 9's disclosure
question explicitly resolved or explicitly reported — not silently
skipped.
