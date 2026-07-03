# SmartCam AI - QA Report

| ID | Page | Severity | Description | Expected | Actual | Likely Cause | Files | Suggested Fix |
|----|------|----------|-------------|----------|--------|--------------|-------|---------------|
| QA-001 | Logs (`/logs`) | Medium | Filter chips (Info, Warn, Error) do nothing when clicked | Logs table filters rows | No action occurs | Missing JS event listeners | `logs.html` | Add Vanilla JS to toggle `.hidden` on rows based on data attributes. |
| QA-002 | Notifications (`/notifications`) | Low | "Mark all as read" button is non-functional | Clears notification badges | Button flashes but no state change | UI mockup state | `notifications.html` | Implement a `POST /api/notifications/read` endpoint and JS handler. |
| QA-003 | Dashboard (`/dashboard`) | Low | "Export PDF" quick action button leads to `#` | Triggers PDF download | Nothing happens | Placeholder href | `dashboard.html` | Change `href="#"` to `href="{{ url_for('api_bp.download_report', format='pdf', timeframe='daily') }}"`. |
| QA-004 | Inspection (`/inspection`) | High | Extremely large images (>15MB) cause UI freeze before timeout | Graceful rejection message | Browser tab freezes | Missing frontend file size validation | `inspection.js`, `inspection.html` | Add `if (file.size > 5 * 1024 * 1024)` check before `fetch()` payload. |
