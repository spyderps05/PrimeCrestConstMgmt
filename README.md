<div align="center">

# PrimeCrest Construction Management

### by Spyder Solutions

**Estimating, project control and site management for Pakistan's construction industry.**

<img src="docs/screenshots/hero-overview.png" alt="PrimeCrest Construction Management: BOQ, takeoff, scheduling and cost control" width="900" />

[Website](https://primecrest.pk) · [Documentation](https://docs.primecrest.pk) · [Issues](https://github.com/spyderps05/PrimeCrestConstMgmt/issues) · [support@primecrest.pk](mailto:support@primecrest.pk)

</div>

---

## What it is

PrimeCrest Construction Management is a self-hosted platform that takes a construction
project from the first estimate to final account in one place: bills of quantities,
quantity takeoff from drawings, rate analysis, procurement, scheduling, site diaries,
interim payment certificates and cost reporting.

It is set up for how construction works in Pakistan:

- **PKR first.** Rupee amounts with lakh / crore grouping, multi-currency where a
  contract or import is priced in USD.
- **Sales tax on services.** Federal (FBR / ICT) and provincial sales tax on construction
  services: Punjab (PRA), Sindh (SRB), Khyber Pakhtunkhwa (KPRA) and Balochistan (BRA),
  plus withholding tax on contractor payments.
- **PEC contractor categories.** Record a firm's Pakistan Engineering Council category
  (C-A through C-6) and specialisations on contractors and subcontractors, and check
  them against a tender's eligibility limit.
- **Urdu and English interface.** Full right-to-left Urdu UI alongside English, switchable
  per user.
- **Local demo projects.** Sample projects in Lahore, Karachi and Islamabad, priced in PKR,
  so you can explore every module before entering your own data.

## Who it is for

| Role | What PrimeCrest gives you |
|------|---------------------------|
| **Owner / Director** | Portfolio dashboard across all projects: budget vs. actual, cash flow, margin, overdue payments and risk, in PKR. |
| **Project Manager** | Schedule (Gantt, critical path), change orders, RFIs, risk register, meetings and progress reporting from one project workspace. |
| **Site Engineer** | Daily site diary, labour and plant returns, punch lists, inspections, photos and drawing markups, usable on a tablet. |
| **QS / Estimator** | BOQ editor, rate analysis from labour / material / plant resources, takeoff from PDF and CAD drawings, measurement sheets, IPC / running bills and variations. |
| **Procurement** | Material requisitions, supplier quotes and comparison statements, purchase orders, subcontract packages and delivery tracking. |
| **Accounts** | Invoices and payment certificates with sales tax and withholding, retention, advance recovery, bank guarantees and cost reports by project and cost code. |

## Key capabilities

- **Estimating and BOQ** - hierarchical bills of quantities, unit-rate build-ups,
  overheads, profit and contingency, versioning and comparison between revisions,
  export to Excel and PDF.
- **Takeoff** - measure quantities from PDF drawings, DWG / DXF and BIM models, and link
  each quantity back to the drawing it came from.
- **Cost database** - reusable resources and rates, regional price lists and assemblies;
  maintain your own PKR rate library.
- **Planning** - schedules generated from the BOQ, dependencies, baselines and earned
  value (SPI / CPI).
- **Procurement and subcontracts** - requisition to purchase order to goods received,
  tender packages and bid comparison.
- **Site management** - diaries, labour, plant, quality inspections, safety and
  punch lists.
- **Finance** - running bills / IPCs, sales tax and withholding, retention, guarantees,
  cash-flow forecasts.
- **Validation** - every estimate is checked for missing quantities, zero rates and
  inconsistent units before it is issued.
- **AI assistance (optional)** - connect your own LLM provider to suggest rates or draft
  an estimate from a description or photo. Every suggestion waits for a person to
  confirm it.

## Quick start

### Docker (quickest)

Requires Docker with Compose v2.

```bash
git clone https://github.com/spyderps05/PrimeCrestConstMgmt.git
cd PrimeCrestConstMgmt
echo "POSTGRES_PASSWORD=$(openssl rand -base64 24)" >  .env
echo "JWT_SECRET=$(openssl rand -hex 32)"           >> .env
make quickstart
```

Then open **http://localhost:8080**. On Windows PowerShell, see
[docs/getting-started.md](docs/getting-started.md#path-c-docker) for the equivalent commands.

### Local development

Requires Python 3.12+ and Node.js 22+ (and Docker for PostgreSQL, Redis and MinIO).

```bash
git clone https://github.com/spyderps05/PrimeCrestConstMgmt.git
cd PrimeCrestConstMgmt
make setup            # install backend and frontend dependencies

# Terminal 1 - starts infrastructure, then the API on http://localhost:8000
make dev-backend

# Terminal 2 - frontend on http://localhost:5173
make dev-frontend
```

Open **http://localhost:5173**. See [DEVELOPING.md](DEVELOPING.md) for the codebase guide and
[docs/INSTALL_TROUBLESHOOTING.md](docs/INSTALL_TROUBLESHOOTING.md) if something does not start.

### Single command

Once the backend package is installed, the `primecrest` command runs the API and the built web app together:

```bash
primecrest serve
```

### Demo login

Demo accounts and sample projects are created on first start:

| Account | Email | Password | Role |
|---------|-------|----------|------|
| Admin | `demo@primecrest.pk` | `DemoPass1234!` | Full access |
| Estimator | `estimator@primecrest.pk` | `DemoPass1234!` | Estimator |
| Manager | `manager@primecrest.pk` | `DemoPass1234!` | Manager |

To set your own passwords, define `DEMO_USER_PASSWORD`, `DEMO_ESTIMATOR_PASSWORD` and
`DEMO_MANAGER_PASSWORD` before the first start.

> **Security.** On any internet-facing deployment, set strong values for these
> variables or disable the demo accounts with `DISABLE_DEMO_ACCOUNTS=1`. See
> [SECURITY.md](SECURITY.md) for the self-hosting checklist.

## Screenshots

| | |
|---|---|
| <img src="docs/screenshots/gallery/portfolio-dashboard.jpg" alt="Portfolio dashboard" width="420" /><br/><sub>Portfolio dashboard</sub> | <img src="docs/screenshots/gallery/projects.jpg" alt="Projects" width="420" /><br/><sub>Projects</sub> |
| <img src="docs/screenshots/gallery/boq-editor.jpg" alt="BOQ editor" width="420" /><br/><sub>BOQ editor</sub> | <img src="docs/screenshots/gallery/cost-database.jpg" alt="Cost database" width="420" /><br/><sub>Cost database and rates</sub> |
| <img src="docs/screenshots/gallery/pdf-takeoff.jpg" alt="PDF takeoff" width="420" /><br/><sub>PDF takeoff</sub> | <img src="docs/screenshots/gallery/finance.jpg" alt="Finance" width="420" /><br/><sub>Finance and earned value</sub> |
| <img src="docs/screenshots/gallery/validation.jpg" alt="Validation" width="420" /><br/><sub>Estimate validation</sub> | <img src="docs/screenshots/gallery/analytics.jpg" alt="Analytics" width="420" /><br/><sub>Cross-project analytics</sub> |

## Tech stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy, Alembic |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, AG Grid |
| Database | PostgreSQL 16+ |
| Cache / storage | Redis, MinIO (S3-compatible) |
| CAD / BIM | cad2data converters (RVT, IFC, DWG to structured quantities) |
| i18n | i18next, Urdu (RTL) and English plus additional languages |

Architecture notes: [docs/architecture/README.md](docs/architecture/README.md). Module
catalogue: [MODULES.md](MODULES.md).

## Support

- Issues and feature requests: [GitHub Issues](https://github.com/spyderps05/PrimeCrestConstMgmt/issues)
- Email: [support@primecrest.pk](mailto:support@primecrest.pk)
- Security reports: see [SECURITY.md](SECURITY.md)

## AI disclaimer

AI suggestions are preliminary. A qualified quantity surveyor or estimator must verify
all quantities, rates and costs before any contractual or tender use.

## Licensing & attribution

PrimeCrest Construction Management is developed by Spyder Solutions. The codebase is
derived from **[OpenConstructionERP](https://github.com/datadrivenconstruction/openconstructionerp)**
by **Artem Boiko / DataDrivenConstruction**, and is distributed under the
**GNU Affero General Public License v3.0** - see [LICENSE](LICENSE), [NOTICE](NOTICE) and
[COPYRIGHT](COPYRIGHT). Upstream copyright notices in source files are retained.

Under AGPL-3.0 you may use, modify and redistribute this software. If you run a modified
version as a network service, AGPL section 13 requires you to offer the corresponding
source code to its users under the same licence.

© 2026 Spyder Solutions. PrimeCrest is based on OpenConstructionERP © Artem Boiko /
DataDrivenConstruction, licensed under AGPL-3.0.
