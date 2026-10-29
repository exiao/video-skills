# fal API image-to-video

Use a current model page's **API** tab as the source of truth for endpoint ID, accepted fields, size/duration limits, output schema, and price. fal image-to-video models have different input keys and may bill for reference video or retries. Do not substitute a text-to-video endpoint or copy parameters from another model. Start from [fal's model catalog](https://fal.ai/models) and the selected model's API page.

The official JavaScript client is `@fal-ai/client`, using `FAL_KEY` in the environment. Keep the key server-side and out of logs. For a local image, upload it with `fal.storage.upload(file)` or the client's documented binary auto-upload, then place the returned URL in the model's image input field. Verify that the upload and its contents succeeded before submitting the generation.

For a long job, prefer the queue so the request ID survives a process interruption. Adapt field names to the selected model's live schema:

```js
import { fal } from "@fal-ai/client";

const endpoint = "<verified image-to-video endpoint>";
const input = { /* exact fields from this endpoint's API tab */ };
const submitted = await fal.queue.submit(endpoint, { input });
console.log(submitted.request_id);
// Later: fal.queue.status(endpoint, { requestId: submitted.request_id })
// Once complete: fal.queue.result(endpoint, { requestId: submitted.request_id })
```

Use the returned video URL or file object according to that endpoint's output schema. Download the file promptly to a task-owned path and verify playback. On an uncertain network response, check the existing request ID/status before retrying: a blind repeat may incur another charge. See [fal's official queue, upload, and client example](https://fal.ai/models/fal-ai/vidu/image-to-video/api).
