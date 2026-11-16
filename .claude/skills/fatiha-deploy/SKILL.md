---
name: fatiha-deploy
description: Publish the Fatiha site to https://fatiha.ample.run after a change is committed and pushed. Use whenever the owner asks to put the site online, update it, "mets en ligne", "publie", or after any change to fatiha/ that they will want to see live. Not for claude.ai artifacts: they break the 3D globe.
---

# Deploy Fatiha to Ample

Direct uploads from this cloud session are blocked by the proxy (403). The working path is
to let Ample fetch each file from GitHub.

1. Commit and push the change on the working branch first. Note the commit SHA
   (`git rev-parse HEAD`).
2. List the files that changed under `fatiha/` (`git diff --name-only <last-deployed-sha> HEAD -- fatiha/`).
3. For each, call `ample_workspace_write` on the site's workspace with
   `source_url = https://raw.githubusercontent.com/<owner>/<repo>/<SHA>/fatiha/<path>` and
   the path relative to `fatiha/`. Use the commit SHA, never the branch name: GitHub's cache
   serves stale branch files for minutes.
   Workspace id is in the last deploy; if lost, `ample_workspace_create` with `from_app`
   on the fatiha app.
4. `ample_deploy` (static, public). Read the result once; never redeploy to poll.
5. Check the live page loads the new files (fetch it, compare a changed string or size).

Tell the owner in French, in one or two sentences, with the link.
Never add outbound links, analytics or third-party embeds while deploying.
