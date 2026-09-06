# Phase 2: University Directory UI

## Objective
Provide the Government with a complete institutional registry. The government officer should be able to view, search, and manage participating universities, acting as a foundation for intelligent routing.

## Scope
- Add "Universities" to the main left navigation bar.
- Build the `Universities` dashboard page to display the imported dataset.
- Implement responsive data table, detail drawer, and forms to add or edit universities.
- Connect the UI to the `api/universities/` endpoints.

## Files Created
- `frontend/src/pages/Universities.jsx`: The core React component for the directory. Includes search/filter bars, an interactive table, a side-drawer for viewing university details, and modals for creating and editing universities.
- `docs/government-routing/04-phase-02-university-directory.md`: This documentation file.

## Files Modified
- `frontend/src/components/layout/Sidebar.jsx`: Added the `Universities` navigation link with the `GraduationCap` icon.
- `frontend/src/App.jsx`: Registered the `/universities` route to render the `Universities` component.

## UI Changes
- **Sidebar**: Now features a dedicated `Universities` menu item beneath `Progress`.
- **Universities Page**:
  - **Header Stats**: Displays Total Universities, Active Universities, Currently Receiving Challenges (stubbed), and Active Projects (stubbed).
  - **Filters**: Provides a unified search bar for Name, Location, and Domain. Includes dropdown filters for Status, District, and Domain (dynamically populated from data).
  - **Table**: Compact display showing University Name, Location, Status, and Research Domains.
  - **Drawer**: Clicking a row opens a right-side drawer revealing full research domains, output text, and action buttons.
  - **Forms**: Intuitive add and edit modals utilizing the same UI language as the rest of the application. Status toggling is done with a single click.

## API Integration
- Utilized the `GET /api/universities/` endpoint created in Phase 1 to populate the table.
- Bound the Add University form to `POST /api/universities/`.
- Bound the Edit University form to `PUT /api/universities/{id}`.
- Bound the Deactivate/Activate toggle to `PATCH /api/universities/{id}/status`.

## Design Decisions
- Adopted the existing Glassmorphism/Tailwind aesthetic for seamless integration.
- Extracted unique districts and domains dynamically from the fetched dataset for the dropdown filters, avoiding hardcoded lists and ensuring they update when new universities are added.
- Placed the detail view in an off-canvas drawer to prevent losing context of the table.

## Test Cases
- **Test 1**: Verify navigation to `/universities` works and the table loads the seeded data. (Passed).
- **Test 2**: Search for "RIMS" and verify the table filters correctly. (Passed).
- **Test 3**: Select a district from the dropdown and verify filtering. (Passed).
- **Test 4**: Edit a university to change its location and save. (Passed).
- **Test 5**: Deactivate a university. Verify the badge changes to "Inactive" and it remains in the list. (Passed).

## Next Phase
**Phase 3 — University Matching Engine**: Replace the hardcoded matching logic with a semantic/keyword-based matching engine that evaluates challenges against the `research_domains` of the active universities we can now manage.
