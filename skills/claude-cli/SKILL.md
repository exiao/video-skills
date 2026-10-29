---
name: claude-cli
description: Run Claude Code for implementation, animation, design, reviews, or a second perspective, using the user's authorized local setup.
---

# Claude CLI

Run Claude Code in the relevant project directory. Check the installed `claude --help` and `claude auth status` before relying on flags or model names. Use an existing authorized login, respect the host's sandbox and approval policy, and never print or inspect credentials. A failed sandboxed authentication check may reflect credential-store access rather than a logged-out account; report the limitation and use only an approved execution context. Do not route around denied permissions.

Give Claude the task, source and reference paths, editable boundaries, output format, scope, and concrete verification requirements. For animation or design, include the visual and motion brief and ask for playable output and editable source. Select an available model appropriate to the task; the animation workflow prefers Opus for open-ended motion design when available. Preserve the user's specified tools and model.

Use the installed CLI's documented noninteractive or interactive mode. Resume the same session for bounded revisions when available. Inspect actual changes and media yourself, verify the requested result, and report anything that could not be checked. An agent's success message is not evidence that motion, sound, or playback works.

The optional `scripts/auth_preflight.py` performs a read-only authentication visibility check without displaying secrets. Review it before use. Alternate providers or proxies can receive the task context: use them only with appropriate authorization.
