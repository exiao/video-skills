# Higgsfield CLI image-to-video

Read the installed higgsfield-generate (external resource; not included) skill and its media-input reference for current model modes. The CLI is a paid or separately metered route; website Unlimited access does not imply CLI allowance.

Check CLI and account state without printing credentials:

```bash
command -v higgsfield
higgsfield account status
higgsfield model list --video
higgsfield model get <job_type> --json
```

Use the exact schema returned by `model get` to determine whether the input is `start_image`, `image`, or `image_references` and which mode accepts it. For example, the installed Seedance 2.5 skill documents `omni_reference` for a start image; its `t2v` mode accepts no media. Confirm current cost with `higgsfield generate cost` for the selected model and parameters before submission. Then call `higgsfield generate create <job_type> ... --wait`, passing the local image path directly; the CLI uploads it. If the wait ends without a terminal result, use the returned job ID with `higgsfield generate get` or `wait` instead of submitting a duplicate.

Use the result URL and, when possible, retain a local video file. Verify playback and metadata as described in the main skill. If CLI account status or model discovery fails, investigate the exact error; do not assume the website is also unavailable. In particular, `No workspace selected` means set an existing workspace with `higgsfield workspace list` and `higgsfield workspace set <workspace_id>`; it is not evidence of expired authentication.
