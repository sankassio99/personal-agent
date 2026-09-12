## Context

The repository already contains a lightweight Google Sheets infrastructure skeleton under the finance assistant package. That structure currently exposes empty placeholder classes without a working authentication or credential model. The requested capability should align with the repository’s Agno-style architecture while staying compatible with the current package layout.

The reference instructions supplied for Google Sheets in the workspace describe an Agno toolkit named `GoogleSheetsTools`, including environment variables (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_PROJECT_ID`) and the expected dependency surface (`agno`, `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`, `openai`). The design should use these constraints as the authoritative integration requirements for the implementation branch.

## Goals / Non-Goals

**Goals:**
- Add a Google Sheets integration path that can be used by an Agno-style agent in this project.
- Model credentials through existing environment variables and the project’s settings object.
- Provide a repository/client abstraction consistent with the existing `infrastructure/google_sheets/` package skeleton.
- Keep the implementation optional and dependency-safe when Google tooling is absent.

**Non-Goals:**
- Building a full OAuth refresh token UI.
- Implementing spreadsheet creation and duplication workflows beyond the repository’s initial placeholders.
- Replacing the current Telegram or Gemini message response stack.

## Decisions

1. Treat the Google Sheets integration as an optional infrastructure capability rather than a hard dependency in the application bootstrap.
   - Rationale: The repository already uses graceful dependency fallbacks (`Agent`, `Gemini`) and should avoid breaking the project when `agno` or Google libraries are not installed.

2. Standardize on environment-backed Google configuration and repository dependency injection.
   - Rationale: Existing configuration style already expects environment variables and settings objects; the Google Sheets client should take the same pattern rather than embedding secrets directly in code.

3. Keep the new capability centered on a small, testable client and repository surface.
   - Rationale: The existing placeholder files in the repo show a `GoogleSheetsClient` and `GoogleSheetsRepository` split; treating them as the boundary reduces implementation complexity while keeping the code open for future extension.

4. Add the dependency contract in the project’s metadata and document the expected OAuth and scope configuration.
   - Rationale: The attached Google Sheets instructions are authoritative for the user-facing integration flow, including `AuthConfig` and `GoogleSheetsTools` guidance.

## Risks / Trade-offs

- [Missing optional dependency handling] → Keep imports inside try/except blocks and degrade gracefully when Google Credential libraries are unavailable.
- [Credential model ambiguity] → Use environment-variable names and settings fallbacks consistently, while documenting the required Google OAuth values.
- [Repo skeleton mismatch] → Keep the implementation in the existing package namespaces to avoid unnecessary refactors in the finance assistant structure.

## Migration Plan

1. Add dependency guidance and environment configuration notes to the project metadata and repository documentation context.
2. Implement a Google Sheets client wrapper that can be configured with service-account or OAuth credentials paths.
3. Add the repository abstraction that reads and writes spreadsheet records in a thin, domain-friendly interface.
4. Expose the integration through the finance assistant’s agent or infrastructure wiring points without forcing a new data model.

## Open Questions

- Should the initial repository support only read operations or also update operations for the spreadsheet-backed finance records?
- Is the Google Sheets instance expected to be a single configured workbook for all expense reporting or can the repository layer support multiple spreadsheets dynamically?
