# Care-Haven — Person 3 Implementation Report

## Scope

This report documents the Person 3 implementation only. No existing README, data scripts, backend code, RAG code, recommendation code, database code, Docker configuration, or shared configuration was modified.

## Files Added

```text
ai/__init__.py
ai/vision/__init__.py
ai/vision/preprocessing.py
ai/vision/quality.py
ai/vision/similarity.py
ai/vision/yolo.py

streamlit/__init__.py
streamlit/app.py
streamlit/config.py
streamlit/api_client/__init__.py
streamlit/api_client/client.py
streamlit/api_client/auth.py
streamlit/api_client/cases.py
streamlit/api_client/donations.py
streamlit/api_client/ai.py
streamlit/api_client/recommendations.py
streamlit/api_client/chat.py
streamlit/components/__init__.py
streamlit/components/navbar.py
streamlit/components/sidebar.py
streamlit/components/case_card.py
streamlit/components/priority_badge.py
streamlit/components/status_badge.py
streamlit/components/charts.py
streamlit/pages/__init__.py
streamlit/pages/login.py
streamlit/pages/dashboard.py
streamlit/pages/cases.py
streamlit/pages/case_details.py
streamlit/pages/submit_case.py
streamlit/pages/donations.py
streamlit/pages/recommendations.py
streamlit/pages/ai_assistant.py
streamlit/pages/image_analysis.py
streamlit/pages/review_queue.py
streamlit/pages/map.py

tests/vision/test_yolo.py
tests/vision/test_similarity.py
requirements/person3.txt
data/sample_images/.gitkeep
```

## Vision Module

The `ai.vision` package is independent of Streamlit, HTTP, authentication, database access, and backend services.

### Preprocessing

`ai/vision/preprocessing.py` provides:

- Safe image loading from paths, bytes, file-like objects, or Pillow images.
- Validation of supported JPEG, PNG, and WEBP files.
- Controlled `ImageLoadError` exceptions for missing, invalid, or corrupted images.
- RGB conversion without changing the original image.
- Optional resize and normalized NumPy-array output.
- Metadata extraction: width, height, format, channel count, and available file size.

### Quality Assessment

`ai/vision/quality.py` provides configurable checks for:

- Minimum image resolution.
- Extreme darkness and brightness.
- Low visible detail / heavy blur, measured using a NumPy Laplacian-variance approximation.
- Invalid or unreadable files.

The returned result has this stable shape:

```python
{
    "is_acceptable": True,
    "quality_score": 0.75,
    "issues": [],
}
```

Thresholds are held in the `QualityConfig` dataclass, allowing future tuning without changing the calling code.

### YOLO Detection

`ai/vision/yolo.py` provides a model-neutral wrapper, `YoloDetector`.

- Model path defaults to `YOLO_MODEL_PATH` or `yolo11n.pt`.
- Confidence and IoU defaults can be set through `YOLO_CONFIDENCE_THRESHOLD` and `YOLO_IOU_THRESHOLD`.
- Ultralytics is imported only when real inference is requested, so normal unit tests do not download or load a model.
- A model may be injected for deterministic testing or future model replacement.
- Ultralytics result objects are converted to a portable result payload:

```python
{
    "detections": [
        {
            "class_name": "person",
            "confidence": 0.91,
            "bbox": [1.0, 2.0, 20.0, 22.0],
        }
    ],
    "num_detections": 1,
}
```

- `visualize_detections` draws labels and bounding boxes on a copy of the image, leaving the source unmodified.

### Similarity

`ai/vision/similarity.py` uses a deterministic perceptual comparison:

- Both images are converted to grayscale and resized to a configurable small resolution.
- Similarity is calculated as normalized mean pixel closeness, giving a score from `0.0` through `1.0`.
- The decision threshold is separate from the calculated score through `SimilarityConfig.threshold`.

```python
{
    "similarity_score": 0.87,
    "is_similar": True,
}
```

This intentionally lightweight approach avoids model downloads and can be replaced later while preserving the public result structure.

## Streamlit Frontend

### Application and Configuration

- `streamlit/app.py` configures the page, initializes authentication session state, routes pages, and keeps page logic outside the entry point.
- `streamlit/config.py` reads settings from environment variables:
  - `CAREHAVEN_API_BASE_URL`
  - `CAREHAVEN_API_TIMEOUT`
  - `CAREHAVEN_APP_TITLE`
  - `CAREHAVEN_MAX_UPLOAD_MB`

No URLs, credentials, tokens, passwords, or secrets are hard-coded.

### API Client Layer

All frontend HTTP communication is isolated in `streamlit/api_client/`.

`ApiClient` supports authenticated GET, POST, PUT, and DELETE requests, JSON handling, configurable timeouts, and safe error messages for unavailable backend services. The page code does not make raw HTTP requests.

The API facades use the endpoints listed in the repository README:

| Feature | Endpoint(s) |
| --- | --- |
| Authentication | `POST /auth/login`, `GET /auth/me` |
| Cases | `GET /cases`, `POST /cases`, `GET /cases/{case_id}`, `PUT /cases/{case_id}` |
| Donations | `GET /donations`, `POST /donations`, `GET /cases/{case_id}/donations` |
| Recommendations | `GET /recommendations/{donor_id}` |
| Chat | `POST /chat` |
| AI integration facade | `POST /ai/analyze-image`, `POST /ai/check-similarity` |

### Pages

| Page | Implemented functionality |
| --- | --- |
| Login | Collects credentials, calls the login API, and stores only returned session information in Streamlit session state. |
| Dashboard | Displays case totals, active/high-priority counts, status chart, and recent case cards. |
| Cases | Retrieves cases, filters by existing priorities, and supports choosing a case. |
| Case Details | Retrieves and displays the selected case from the API. |
| Submit Case | Validates input, previews and quality-checks selected evidence locally, then submits the documented case payload. |
| Donations | Displays donation history and submits donation payloads. |
| Recommendations | Retrieves and renders backend-generated donor recommendations; no recommendation logic is duplicated. |
| AI Assistant | Sends a question to the backend chat API and renders conversation history. |
| Image Analysis | Performs local quality assessment, optional YOLO detection and annotation, and optional local reference-image similarity comparison. |
| Review Queue | Clearly reports the missing backend review-queue endpoint instead of inventing actions. |
| Map | Displays valid backend-provided case latitude/longitude points and safely skips malformed coordinates. |

### Reusable Components

- Navbar with context, signed-in user display, and session logout.
- Centralized sidebar navigation.
- Reusable case card.
- Consistent visual priority and status badges that retain backend values.
- Case-status chart based exclusively on API responses.

## Tests

### `tests/vision/test_yolo.py`

- Uses a fake injected model, so it does not download a YOLO model.
- Verifies the stable detection payload and bounding-box data.
- Verifies controlled invalid-image handling.
- Verifies annotation output is a new image rather than the source image.

### `tests/vision/test_similarity.py`

- Checks identical-image similarity.
- Checks score type/range for distinct images.
- Checks independent threshold behavior.
- Checks controlled invalid-image handling.

## Dependencies

`requirements/person3.txt` contains only Person 3 dependencies:

```text
streamlit>=1.40
Pillow>=10.0
numpy>=1.24
ultralytics>=8.3
pytest>=8.0
```

Ultralytics is only needed for real YOLO inference; the vision tests use no downloaded models.

## Validation Performed

- `python -m compileall ai streamlit tests/vision`: passed.
- Manual vision similarity smoke test: passed.
- Manual injected-YOLO adapter smoke test: passed.

`pytest tests/vision -v` could not run in the existing virtual environment because `pytest` was not installed. Streamlit startup could not be run because Streamlit was not installed. Both dependencies are recorded in `requirements/person3.txt`.

## Integration Blockers

The following required integration resources were absent at implementation time:

1. `docs/architecture.md` was not present.
2. `docs/api_contract.md` was not present.
3. No backend implementation was present.
4. The README lists `POST /cases`, but it does not document a multipart evidence-image upload field or a storage response. The Submit Case page therefore performs local image validation/preview only and does not invent a file-upload API.
5. The README lists no review-queue retrieval or case approval/rejection endpoint. The Review Queue page shows this limitation rather than making undocumented requests.

## Next Integration Steps

After the backend and dependencies are available:

1. Install the Person 3 requirements.
2. Run `python -m pytest tests/vision -v`.
3. Start the backend and run `streamlit run streamlit/app.py`.
4. Replace endpoint assumptions with the final `docs/api_contract.md` response schemas if they differ.
5. Add documented multipart upload and review-queue endpoints to the frontend API client only after the responsible backend owner publishes their contracts.
