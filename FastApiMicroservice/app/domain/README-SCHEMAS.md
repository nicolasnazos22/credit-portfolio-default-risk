# Credit Risk Scoring — Schemas

Pydantic schema module for a credit risk scoring service. It defines the input/output contracts for three features:

1. **Individual scoring** of a loan applicant.
2. **Portfolio risk simulation** (Monte Carlo).
3. **Model performance metrics** logging.

Intended to be exposed via FastAPI.

## Requirements

- Python 3.10+
- `pydantic>=2.0`

```bash
pip install "pydantic>=2.0"
```

## Models

### Enum types

| Enum | Values | Description |
|---|---|---|
| `HomeOwnership` | `RENT`, `OWN`, `MORTGAGE`, `OTHER` | Applicant's housing situation |
| `LoanIntent` | `PERSONAL`, `EDUCATION`, `HOMEIMPROVEMENT`, `DEBTCONSOLIDATION`, `MEDICAL`, `VENTURE` | Purpose of the loan |
| `LoanGrade` | `A`–`G` | Loan grade/rating |
| `CbDefaultOnFile` | `Y`, `N` | Whether the credit bureau has a prior default on file |
| `EtiquetaRiesgo` | `BAJA`, `MEDIA`, `ALTA` | Risk category assigned to the result (Low/Medium/High) |

### `CreditRiskRequest`

Input data to evaluate an applicant.

| Field | Type | Range / Constraint |
|---|---|---|
| `person_age` | `int` | 18–100 |
| `person_income` | `int` | 10,000–1,000,000 (annual USD) |
| `person_home_ownership` | `HomeOwnership` | — |
| `person_emp_length` | `float` | 0–60 (years) |
| `loan_intent` | `LoanIntent` | — |
| `loan_grade` | `LoanGrade` | — |
| `loan_amnt` | `int` | 1,000–50,000 |
| `loan_int_rate` | `float` | 5.0–25.0 |
| `loan_percent_income` | `float` | 0.0–1.0 |
| `cb_person_cred_hist_length` | `int` | 0–60 (years) |
| `cb_person_default_on_file` | `CbDefaultOnFile` | — |

**Business validation** (`model_validator`, mode `after`):

- `person_emp_length` cannot exceed `person_age - 16` (employment history can't be longer than age minus 16).
- `cb_person_cred_hist_length` cannot exceed `person_age - 16 - 2` (credit history can't predate age 18).

Both violations raise `ValueError`, which Pydantic turns into a `ValidationError`.

### `CreditRiskResponse`

Result of the evaluation.

| Field | Type | Description |
|---|---|---|
| `probabilidad_default` | `float` (0–1) | Inferred probability of default |
| `default_prediccion` | `0` \| `1` | Binary prediction |
| `etiqueta_riesgo` | `EtiquetaRiesgo` | Low / Medium / High |
| `explicacion` | `dict[str, float]` | SHAP values per feature (interpretability) |

Built via the `armar_respuesta(...)` classmethod, which rounds `probabilidad_default` to 4 decimals.

### `PortfolioRiskSimulationRequest` / `PortfolioRiskSimulationResponse`

Monte Carlo simulation of aggregate portfolio risk.

- **Request**: `cantidad_escenarios` (1,000–10,000, default 10,000) and `requests`, a list of 2 to 1,000 individual probabilities (`Proba = float` between 0 and 1).
- **Response**: `cantidad_simulaciones`, `var_95` (95% VaR) and `cvar_95` (95% CVaR / Expected Shortfall). Built via `armar_respuesta(...)`.

### `Metricas`

Snapshot of model performance for monitoring/logging.

| Field | Type | Description |
|---|---|---|
| `timestamp` | `datetime` | When the metrics were recorded |
| `recall_default` | `float` (0–1) | Sensitivity on the default class |
| `precision_default` | `float` (0–1) | Precision on default detection |
| `pr_auc` | `float` (0–1) | Area under the precision-recall curve |

## Design note: `armar_respuesta`

`CreditRiskResponse` and `PortfolioRiskSimulationResponse` use a named constructor (`armar_respuesta`) instead of building the model with raw `cls(...)` kwargs, so rounding/casting happens in one place instead of at every call site. If this ever grows to include actual decision logic (e.g. deriving `etiqueta_riesgo` from `probabilidad_default`), move that part into the service layer and keep the schema to fields + validation.

## Usage example

```python
from datetime import datetime

request = CreditRiskRequest(
    person_age=30,
    person_income=45000,
    person_home_ownership=HomeOwnership.RENT,
    person_emp_length=5,
    loan_intent=LoanIntent.PERSONAL,
    loan_grade=LoanGrade.B,
    loan_amnt=10000,
    loan_int_rate=12.5,
    loan_percent_income=0.22,
    cb_person_cred_hist_length=8,
    cb_person_default_on_file=CbDefaultOnFile.N,
)

response = CreditRiskResponse.armar_respuesta(
    probabilidad_default=0.1834,
    etiqueta=EtiquetaRiesgo.MEDIA,
    prediccion_default=0,
    explicacion={"loan_int_rate": 0.04, "person_income": -0.02},
)
```