# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in PrimeCrest,
please report it responsibly.

**DO NOT** open a public GitHub issue for security vulnerabilities.
Public disclosure before a fix is available puts users at risk.

### How to Report

1. **GitHub Security Advisories** (preferred):
   [Create a new advisory](https://github.com/spyderps05/PrimeCrestConstMgmt/security/advisories/new)

2. **Email:** `support@primecrest.pk`

### What to Include

- Description of the vulnerability
- Affected version (commit hash or release tag) and component
  (backend module, frontend, desktop client, Docker image)
- Steps to reproduce
- Potential impact (CIA classification and realistic scenarios)
- Suggested fix (if any)
- Your preferred credit attribution (or request for anonymity)

### Response Timeline

We follow coordinated disclosure:

| Action                | Target time                                              |
|-----------------------|----------------------------------------------------------|
| Acknowledgement       | 48 hours                                                 |
| Initial assessment    | 5 business days                                          |
| Fix development       | 14 business days (critical: 72 hours)                    |
| Public disclosure     | After a fix is released; at the latest 120 days from report |

For actively exploited vulnerabilities, we shorten all stages and
publish a mitigation advisory as soon as one is available.

### Advisories and CVE identifiers

Every confirmed vulnerability gets a GitHub Security Advisory that names
the affected and the fixed versions, and a CVE identifier that we request
through GitHub, which is a CVE Numbering Authority. We request the
identifier ourselves so the record carries the verified facts: the
component, the fixed release and the severity we assessed with the
reporter. All published advisories are listed at
<https://github.com/spyderps05/PrimeCrestConstMgmt/security/advisories>.

Please keep a report private until we publish the advisory, and leave the
CVE request to us, so that one accurate record exists rather than
duplicates from different sources. Reporters are credited in the
advisory and in the CVE record unless they ask for anonymity.

## Supported Versions

| Version track           | Security updates                                    |
|-------------------------|-----------------------------------------------------|
| Latest release (18.x)   | Yes                                                 |
| Previous minor          | Critical fixes only, for six months after superseded |
| Older releases          | No - upgrade path published in release notes         |

## Scope

**In scope:**

- Backend API (FastAPI services under `backend/app/`)
- Frontend web application (`frontend/`)
- Desktop client (`desktop/`)
- Official Docker images published by Spyder Solutions and
  the hosted instance at `https://primecrest.pk`
- CLI tools distributed with the project
- Build and release automation that produces signed artefacts
  (`.github/workflows/release*.yml`, `signatures/`)

**Out of scope:**

- Vulnerabilities in third-party dependencies - report directly
  to the upstream vendor; we will update once a patched version
  is available.
- Social engineering of the maintainers, contributors, or customers.
- Issues that require an already-compromised user system or the
  user deliberately bypassing security controls.
- Self-XSS, denial-of-service via resource exhaustion on
  community-edition deployments.
- Issues restricted to configurations that contradict the
  self-hosting checklist below (e.g., default `JWT_SECRET`, HTTP
  instead of HTTPS).

## External Code and Pull Requests

Every pull request is reviewed by Spyder Solutions before it is merged, and must pass
the continuous-integration checks. Security fixes reported privately are implemented
and reviewed before disclosure, and the reporter is credited unless they ask for
anonymity.

## Self-Hosting Security Checklist

If you deploy PrimeCrest on your own infrastructure:

- [ ] Change `JWT_SECRET` from the default value
- [ ] Use HTTPS (TLS 1.2+) in production - never expose HTTP
      publicly
- [ ] Set `APP_ENV=production` to disable debug endpoints
      (`/api/docs`, `/api/redoc`)
- [ ] Give PostgreSQL a strong password when you run your own
      server instead of the embedded one
- [ ] Restrict `ALLOWED_ORIGINS` to your actual domain
- [ ] Keep Docker images updated (`docker compose pull`)
- [ ] Back up your database regularly and test restores
- [ ] Review `.env` file permissions - readable only by the app
      user
- [ ] If using AI features, protect your provider API keys
      (OpenAI / Anthropic / Google / Mistral / Groq / DeepSeek) -
      never commit them to git

## Security Features

- JWT authentication with configurable expiration
- Password hashing with bcrypt
- CORS middleware with configurable origins
- SQL-injection prevention via SQLAlchemy ORM
- Input validation via Pydantic v2
- Rate limiting (configurable)
- Role-based access control (RBAC)
- Reproducible builds and signed release artefacts
  (see [Verifying a Release](#verifying-a-release))

## Verifying a Release

Every GitHub release carries `SHA256SUMS`, signed with Sigstore as
`SHA256SUMS.sig` and `SHA256SUMS.pem`. Download those three files next
to your installer, then run:

```
cosign verify-blob \
  --certificate SHA256SUMS.pem \
  --signature SHA256SUMS.sig \
  --certificate-identity-regexp 'https://github.com/spyderps05/PrimeCrestConstMgmt/.*' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  SHA256SUMS
sha256sum -c SHA256SUMS --ignore-missing
```

The first command proves the checksum list is ours, the second that
your download matches it. Both have to pass.

## Regulatory Reporting

Where personal data is affected, Spyder Solutions notifies affected customers without
undue delay and cooperates with the competent authorities in Pakistan, including
obligations under the Prevention of Electronic Crimes Act 2016 where applicable.

## No Bug Bounty

Spyder Solutions currently does not operate a paid
bug-bounty programme. We gratefully acknowledge responsible
researchers in the associated GitHub Security Advisories unless
anonymity is requested.

## Contact

All security communication: `support@primecrest.pk`.
Where GitHub Security Advisories are available, please use that
channel for reports that include sensitive proof-of-concept
material.
