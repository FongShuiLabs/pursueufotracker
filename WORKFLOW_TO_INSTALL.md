# One-time install: war.gov auto-poller workflow

The push from local was rejected because the stored Personal Access Token doesn't have the `workflow` scope. Two ways to fix it:

## Option A — install via GitHub web UI (5 minutes, no scope changes)

1. Open https://github.com/FongShuiLabs/pursueufotracker
2. Click **Add file** → **Create new file**
3. Filename: `.github/workflows/poll-wargov.yml`
4. Paste the entire contents of [poll-wargov-workflow.yml.txt](poll-wargov-workflow.yml.txt) into the editor
5. Commit message: `chore: add war.gov auto-poller workflow`
6. Commit directly to `main`
7. Then go to **Settings → Actions → General → Workflow permissions** and select **Read and write permissions**
8. Manual fire: **Actions** tab → **Poll war.gov for new PURSUE drops** → **Run workflow**

## Option B — fix your PAT and re-push

1. https://github.com/settings/tokens → edit the PAT used by your local git → check the **workflow** scope → save
2. Update your stored credential:
   ```powershell
   git -C 'C:\Users\Anthony\Desktop\ufo-disclosure-site' credential reject https://github.com
   ```
   Next git operation prompts for the new PAT. Or use `git config credential.helper manager-core` and re-auth.
3. Then I (or you) can push the workflow file normally.

Option A is faster.

## After install: what runs

- Every 30 min during US weekday business hours (13:00-22:00 UTC)
- Hourly off-hours, 7 days a week
- Plus manual `workflow_dispatch` from the Actions tab

On change: commits the new state with `[NEW DROP]` in the message + opens a labeled GitHub issue. On no-change: commits the updated `last_polled_at` timestamp so the homepage liveness stamp ticks. Either way, the commit triggers Cloudflare auto-deploy.

## After install: delete this file and `poll-wargov-workflow.yml.txt`

Once the workflow is live in `.github/workflows/`, both this doc and `poll-wargov-workflow.yml.txt` can be removed:

```powershell
git rm WORKFLOW_TO_INSTALL.md poll-wargov-workflow.yml.txt
git commit -m "Workflow installed via web UI - cleanup"
git push
```
