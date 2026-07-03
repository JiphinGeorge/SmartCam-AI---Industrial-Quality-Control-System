# QualiVision AI - Developer TODO

## Critical
- [ ] **Fix Large Image Upload Timeout**: Add frontend Javascript validation to reject images over 5MB before passing them to the Flask backend to prevent memory spikes in TensorFlow. (Ref: QA-004)

## High
- [ ] **Wire Dashboard "Export PDF" Button**: Update the `href` in the Dashboard quick actions card to point to the actual `/api/reports/download` endpoint. (Ref: QA-003)

## Medium
- [ ] **Connect Logs Filter UI**: Implement the JavaScript necessary to filter the terminal output on the `logs.html` page based on the selected severity chips. (Ref: QA-001)

## Low
- [ ] **Notifications "Mark Read"**: Add a background API call for the "Mark all as read" button on the Notifications screen. (Ref: QA-002)
- [ ] **Typography**: Adjust the line height on the Settings panel for better readability on 13-inch laptop screens.
