# API Contracts

This document standardizes response and request contracts for key endpoints used by the frontend.

## Base paths

All API routes are mounted at **`/api/v1/...`** and duplicated at **`/api/...`** (same handlers) for verification tools that omit `/v1`.

## Identifier types

- `candidate_id` / `id`: string UUID (verification samples may show integers; the live API uses UUIDs).
- `file_id`: storage object key (same as `candidates.file_name` after upload).

## Health

`GET /health`

```json
{
  "status": "ok",
  "timestamp": "2026-04-05T10:30:00Z"
}
```

## Candidate Status API

`GET /api/v1/candidates/{candidate_id}/status` (also `/api/candidates/...`)

Response:

```json
{
  "candidate_id": "fed439df-9687-4199-bc6e-edcb8da52bcc",
  "status": "completed",
  "score": 78.5,
  "processed_at": "2026-04-05T10:35:00Z"
}
```

Notes:
- `status` values: `pending`, `processing`, `completed`, `failed`
- `score` can be `null` until scoring is complete
- `processed_at` is UTC ISO-8601 (`YYYY-MM-DDTHH:MM:SSZ`) or `null`
- On error, an additional `error` string may be present

## Create / list / get candidate

`POST /api/v1/candidates` — flat body `name`, `email`, `file_id` or `storage_url`. Response:

```json
{
  "id": "uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "file_id": "object-key-in-bucket.pdf",
  "status": "pending",
  "created_at": "2026-04-05T10:30:00Z"
}
```

`GET /api/v1/candidates` — returns a **JSON array** of candidates (no `success` wrapper).

`GET /api/v1/candidates/{candidate_id}` — flat object including `file_id`, `status`, timestamps.

## Candidate Feedback API

`GET /api/v1/candidates/{candidate_id}/feedback`

Response:

```json
{
  "candidate_id": "fed439df-9687-4199-bc6e-edcb8da52bcc",
  "score": 78.5,
  "strengths": ["Strong Python experience"],
  "improvements": ["Add more quantifiable impact metrics"],
  "skill_match": {
    "python": 90,
    "sql": 75,
    "aws": 45
  },
  "recommendations": "Consider highlighting project outcomes with measurable KPIs."
}
```

Fallback behavior:
- `skill_match` is derived in order from:
  1. `score.breakdown.skill_match`
  2. `score.breakdown.matched_skills` / `missing_skills`
  3. Score components (`skill`, `experience`, `education`)
- `recommendations` fallback:
  1. `feedback.feedback_text`
  2. Generated text from `improvements`
  3. `"No additional recommendations available yet."`

## Bias Analyze API

Endpoint: `POST /api/v1/bias/analyze`

Request:

```json
{
  "candidates": [
    {
      "id": "c1",
      "score": 82.0,
      "protected_attributes": {
        "group": "male"
      },
      "attributes": {
        "department": "engineering"
      }
    }
  ]
}
```

Response envelope:

```json
{
  "success": true,
  "data": {
    "bias_detected": false,
    "recommendations": []
  }
}
```

Notes:
- `data` comes from ML service output and may include additional fields.
- Backend persists normalized bias metrics for reporting endpoints.

## Bias Metrics API

`GET /api/v1/bias/metrics` — overall snapshot (no `group`, or `group_type=overall`):

```json
{
  "overall": {
    "demographic_parity_ratio": 0.85,
    "equal_opportunity_diff": 0.12,
    "average_score_by_group": {
      "male": 86.5,
      "female": 73.6
    }
  },
  "last_calculated": "2026-04-09T17:19:17Z"
}
```

`GET /api/v1/bias/metrics?group=gender` (any non-`overall` dimension label) — grouped breakdown:

```json
{
  "group_type": "gender",
  "groups": {
    "male": { "count": 45, "avg_score": 73.2 },
    "female": { "count": 38, "avg_score": 74.5 }
  },
  "disparity_ratio": 0.96
}
```

Query params: `group_type` and/or `group` (alias). Use **`overall`** for the compact `overall` + `last_calculated` response.

## Submit user feedback

`POST /api/v1/feedback` — JSON body:

```json
{
  "candidate_id": "uuid-or-string",
  "rating": 4,
  "comment": "Good match for senior role"
}
```

Response:

```json
{
  "feedback_id": "uuid",
  "status": "recorded",
  "timestamp": "2026-04-05T10:40:00Z"
}
```

