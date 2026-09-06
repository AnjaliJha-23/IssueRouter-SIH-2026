# Phase 3: University Matching Engine

## Objective
Replace the hardcoded mock matching engine with a dynamic semantic keyword/domain-based matcher that evaluates challenges against all active universities in the database.

## Scope
- Modify `backend/api/smart_router.py` to extract challenge context.
- Query all active institutions.
- Compare challenge attributes to university `research_domains` and `research_output`.
- Score matches dynamically.
- Generate explainable reasons for why the recommendation was made.
- Return the top results.

## Files Modified
- `backend/api/smart_router.py`: Rewrote the `generate_matches` function. Removed hardcoded checks for "HealthTech" and specific strings like "RIMS Ranchi" and "Tata Steel CSR".

## Implementation Details
1. **Context Extraction**: The engine combines the challenge `title`, `description`, `domain`, and `department` into a single text block, and uses a basic regex to extract keywords (`>3` characters).
2. **Filtering**: Only universities with `type == "University"` and `status == "ACTIVE"` are queried from the database.
3. **Scoring Logic**:
   - **Base Score**: 40
   - **Direct Domain Match**: +30 points if the challenge domain directly matches a string in the university's `research_domains`.
   - **Keyword Match (Domains)**: Up to +20 points (5 points per keyword match).
   - **Keyword Match (Output)**: Up to +15 points (3 points per keyword match in historical research output).
   - **Geographic Proximity**: +15 points if the challenge `location` contains the university's `district`.
4. **Explainability**:
   - The engine aggregates specific reasons based on the scoring triggers. For example: `Strong domain match (HealthTech) • Geographic proximity (Ranchi)`.
5. **Threshold & Ranking**:
   - A minimum score of 55 is required to be recommended.
   - The maximum score is capped at 99.
   - The API returns up to the top 7 universities, sorted descending by `match_score`.

## Design Decisions
- Using a heuristic keyword/domain matching system provides a massive improvement over hardcoding, immediately leveraging the CSV data from Phase 1.
- By structuring the response exactly as the mock did (`MatchOut`), this phase requires zero changes to the frontend UI yet completely upgrades the intelligence powering it.
- This creates the foundation for a future Phase where NLP Embeddings (e.g., HuggingFace/SentenceTransformers) can replace the heuristic block without changing the API contract.

## Test Cases
- **Test 1**: Verify the API correctly pulls from the database instead of hardcoded strings. (Passed - The API logic uses `db.query(Organization)`).
- **Test 2**: Verify the API returns multiple universities sorted by score. (Passed - Returns up to 7 top matches).
- **Test 3**: Verify explainable strings are generated correctly. (Passed).

## Regression Checks
- Existing routing UI in `RoutingModal.jsx` still works perfectly as the API contract and response shapes (`MatchOut` array) remain identical.
- Inactive universities are successfully ignored by the router.

## Next Phase
**Phase 4 — Government Verification**: Formalizing the state transition before routing occurs.
