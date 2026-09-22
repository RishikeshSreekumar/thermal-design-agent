# Thermal Design Agent
 
**Engineering Design & Analysis**
 
Thermal Design Agent is an AI-assisted thermal-engineering application that converts natural-language engineering requirements into optimized, reviewable, reportable, and CAD-ready plate-fin heat-sink designs.
 
The repository and some internal modules retain the historical project name:
 
`Thermal AI Engineer`
 
---
 
## Release Status
 
**Current Version:** V2.0.0  
**Status:** FROZEN  
**Release Date:** 25 August 2026
 
Thermal Design Agent V2.0.0 is the current stable project baseline.
 
Feature development and final functional regression for the V2.0.0 release are complete.
 
Validated release gates include:
 
- Complete offline deterministic regression
- Live Azure OpenAI integration
- Natural-convection orientation and radiation workflows
- Grounded engineering review and recommendations
- End-to-end engineering orchestration
- Streamlit product smoke testing
- Engineering report generation
- CAD / STEP generation
 
No known functional V2.0.0 release blocker remains.
 
Further capability development should proceed in a subsequent V2.x or V3 development line rather than modifying the frozen V2.0.0 feature scope.
 
---
 
## Engineering Philosophy
 
Thermal Design Agent is engineering-first software.
 
The core rule is:
 
> Deterministic engineering calculations own engineering truth.
 
AI assists with:
 
- Natural-language requirement extraction
- Requirement interaction and clarification
- Grounded engineering-review narrative
- Grounded engineering recommendations
- Engineering communication
 
AI does not:
 
- Modify deterministic thermal calculations
- Override deterministic feasibility
- Override deterministic engineering-review status
- Fabricate engineering evidence
- Silently change supplied engineering constraints
- Perform silent currency conversion
 
---
 
## Current V2 Design Scope
 
The principal supported topology is:
 
- Plate-fin heat sink
 
V2.0.0 supports:
 
- Forced convection
- Natural convection
 
The same deterministic engineering architecture feeds optimization, engineering intelligence, review, reporting, geometry planning, and CAD generation.
 
---
 
## End-to-End Workflow
 
```text
Natural-Language Requirement
        |
        v
LLM Requirement Extraction
        |
        v
Requirement Review
        |
        v
Interactive Clarification
        |
        v
Validated EngineeringRequirements
        |
        v
ThermalOptimizer
        |
        v
Candidate Evaluation
        |
        v
Candidate Selection
        |
        v
Engineering Intelligence
        |
        v
Deterministic Engineering Review
        |
        +--> Optional Grounded AI Review Narrative
        |
        v
Grounded Engineering Recommendations
        |
        v
Engineering Report
        |
        v
Geometry Planning
        |
        v
CadQuery CAD Generation
        |
        v
STEP Output
```
 
---
 
## Requirement Engine
 
The requirement engine supports extraction and deterministic review of:
 
- Heat load
- Ambient temperature
- Air velocity
- Maximum base temperature
- Maximum pressure drop
- Maximum pumping power
- Base length
- Base width
- Maximum total height
- Convection mode
- Explicit allowed-material restrictions
- Material-cost budget
- Budget currency
- Natural-convection orientation
- Natural-convection radiation enable/disable state
- Surface emissivity
- Radiative surroundings temperature
 
Missing critical engineering information is handled through clarification rather than silently invented.
 
For natural convection:
 
- Missing orientation defaults to the established vertical baseline
- Explicitly ambiguous horizontal orientation requires clarification
- Surface emissivity is not invented when radiation is requested
 
---
 
## Supported LLM Providers
 
The provider layer supports:
 
- Azure OpenAI
- Google Gemini
- Mock Provider
 
Typical usage:
 
- Office environment: Azure OpenAI
- Personal development environment: Gemini
- Offline regression: Mock Provider
 
Provider selection does not change deterministic engineering calculations.
 
---
 
## Forced-Convection Capability
 
Current forced-convection capability includes:
 
- Plate-fin design-space exploration
- Fixed approach-air-velocity mode
- Fan-coupled airflow mode
- Flow-area calculation
- Channel-velocity calculation
- Hydraulic-diameter calculation
- Reynolds-number calculation
- Flow-regime-aware heat-transfer correlation selection
- Pressure-drop calculation
- Pumping-power calculation
- Thermal-resistance calculation
- Estimated base-temperature calculation
- Manufacturability screening
- Thermal-temperature constraints
- Pressure-drop constraints
- Pumping-power constraints
- Mass calculation
- Material-cost calculation
- Material-cost budget filtering
- Candidate validation
- Minimum-thermal-resistance optimization
- Weighted multi-objective optimization
- Pareto-front optimization
- Engineering intelligence
- Engineering review
- Engineering recommendations
- Engineering report
- CAD generation
- STEP export
- Streamlit integration
 
Current fan-coupled scope:
 
- One fan
- `speed_fraction = 1.0`
- Demonstration or explicitly supplied fan curve
 
Variable fan-speed modelling is not included in V2.0.0.
 
Thermal radiation is not included in the current forced-convection model.
 
---
 
## Natural-Convection Capability
 
V2.0.0 includes a dedicated natural-convection architecture supporting:
 
### Orientations
 
- Vertical
- Horizontal - fins facing upward
- Horizontal - fins facing downward
 
If a user specifies only that the heat sink is horizontal without identifying fin-facing direction, the application requests clarification.
 
### Convection Models
 
The established vertical path uses the existing Churchill-Chu-based reduced-order natural-convection model.
 
Horizontal plate-fin configurations use orientation-specific Tari-Mehrtash reduced-order correlations for:
 
- Horizontal fins upward
- Horizontal fins downward
 
The vertical baseline is preserved for backward compatibility.
 
### Thermal Radiation
 
Optional natural-convection thermal radiation is supported.
 
The current radiation model includes:
 
- Explicit surface emissivity
- Gray, diffuse surface assumption
- Exchange with large surroundings
- Linearized radiative heat-transfer coefficient
- Iterative coupling with the natural-convection temperature solution
 
The model preserves separately:
 
- Convective heat-transfer coefficient
- Radiative heat-transfer coefficient
- Effective heat-transfer coefficient
 
where:
 
```text
h_effective = h_convective + h_radiative
```
 
For the current reduced-order thermal-resistance architecture:
 
```text
Radiative surroundings temperature = ambient-air temperature
```
 
is required.
 
### Natural-Convection Optimization
 
Natural-convection designs support:
 
- Manufacturability-aware candidate exploration
- Thermal constraints
- Mass calculation
- Material-cost calculation
- Material-cost budget filtering
- Minimum-thermal-resistance selection
- Weighted optimization using compatible objectives
- Pareto optimization using compatible objectives
- Engineering intelligence
- Engineering review
- Engineering recommendations
- Engineering report
- CAD generation
- STEP export
- Streamlit integration
 
Natural-convection workflows do not fabricate forced-airflow performance quantities.
 
---
 
## Optimization
 
The deterministic optimization architecture supports four registered engineering objectives:
 
1. Thermal resistance
2. Pressure drop
3. Pumping power
4. Mass
 
Supported selection modes:
 
### Minimum Thermal Resistance
 
Selects the feasible candidate with the lowest calculated thermal resistance.
 
### Weighted Multi-Objective Optimization
 
Normalizes supported objectives and applies engineer-defined weights.
 
Lower total score represents the preferred candidate under the selected weighting.
 
### Pareto Optimization
 
Returns the non-dominated design set.
 
Pareto optimization does **not** automatically declare one design to be the universal best design.
 
The engineer explicitly selects the final design from the Pareto set.
 
### Natural-Convection Objective Compatibility
 
Natural-convection product workflows use objectives that are physically applicable to the mode, currently including:
 
- Thermal resistance
- Mass
 
Forced-flow quantities such as pressure drop and pumping power are not presented as natural-convection optimization objectives in the Streamlit workflow.
 
---
 
## Material, Mass, Cost and Currency
 
The current principal design/manufacturing path is:
 
- Aluminium 6063-T5
- Extrusion
 
The architecture also contains material and commercial data for supported engineering evaluation.
 
Candidate state may include:
 
- Solid volume
- Mass
- Raw-material cost
- Currency
 
### Currency Rules
 
Default Havells demonstration currency:
 
- INR
 
Foreign supplier profiles may use another explicit currency such as USD.
 
Rules:
 
- Every material-cost profile carries its own currency
- Every calculated material-cost result preserves that currency
- Every budget carries a currency
- Cost and budget are compared only when currencies match
- Different currencies may coexist in the database
- No automatic exchange-rate conversion is performed
- No silent cross-currency ranking is permitted
 
Demonstration material prices remain illustrative until approved procurement values are supplied.
 
---
 
## Manufacturability
 
Manufacturability screening is performed before complete candidate evaluation.
 
The current Aluminium 6063-T5 extrusion capability includes deterministic checks such as:
 
- Minimum fin thickness
- Minimum fin spacing
- Fin-height / fin-thickness ratio
- Fin-height / spacing ratio
- Base-thickness range
- Maximum total height
 
These are generic engineering capability assumptions, not universal supplier guarantees.
 
Supplier validation is required before release for manufacture.
 
---
 
## Engineering Intelligence
 
The deterministic engineering-intelligence layer produces:
 
- Engineering context
- Engineering evidence
- Engineering insights
- Engineering assessments
- Geometry analysis
- Optimization analysis
- Thermal analysis
- Model-limitation analysis
- Manufacturability evaluation
- Thermal-margin evaluation
- Forced-airflow performance evaluation when applicable
 
Natural-convection thermal evidence additionally preserves, where applicable:
 
- Orientation
- Radiation enabled/disabled state
- Surface emissivity
- Convective HTC
- Radiative HTC
- Effective HTC
 
Natural-convection designs do not generate forced-airflow insights or assessments.
 
---
 
## Engineering Review
 
The engineering-review architecture is:
 
```text
EngineeringIntelligenceResult
        |
        v
EngineeringReviewSource
        |
        v
Deterministic EngineeringReview
        |
        +--> Optional Grounded AI Synthesis
        |
        v
EngineeringReviewResult
```
 
The deterministic review owns:
 
- Overall engineering-review status
- Deterministic findings
- Strengths
- Concerns
- Required actions
- Validation requirements
- Engineering traceability
 
AI may improve communication and identify grounded trade-offs.
 
AI may not change deterministic engineering truth.
 
If AI review synthesis fails, the deterministic review remains available.
 
---
 
## Engineering Recommendations
 
Grounded engineering recommendations are generated from the completed engineering review.
 
AI-generated recommendations remain non-authoritative.
 
If recommendation synthesis fails:
 
- Deterministic engineering remains valid
- Engineering intelligence remains valid
- Engineering review remains valid
- Report generation may continue
- Geometry generation may continue
- STEP generation may continue
 
---
 
## Engineering Report
 
V2.0.0 includes structured HTML engineering-report generation.
 
The report includes:
 
- Engineering requirements
- Selected geometry
- Thermal performance
- Forced-airflow performance when applicable
- Natural-convection orientation when applicable
- Radiation configuration when applicable
- Convective / radiative / effective HTC values when applicable
- Engineering review
- Recommendations
- Validation requirements
- Model limitations
- Engineering traceability
- Havells branding
 
Canonical V2 report format:
 
- HTML
 
PDF report generation is outside V2.0.0.
 
---
 
## CAD and STEP Generation
 
The selected deterministic candidate is converted through:
 
```text
Selected Design
      |
      v
GeometryPlanner
      |
      v
CADGenerator
      |
      v
CadQuery Plate-Fin Model
      |
      v
STEP File
```
 
Current CAD topology:
 
- Plate-fin heat sink
 
The generated geometry includes:
 
- Base length
- Base width
- Base thickness
- Fin count
- Fin height
- Fin thickness
- Fin spacing
- Material
 
---
 
## Application Architecture
 
`EngineeringOrchestrator` is the canonical backend orchestration boundary for the standard application workflow.
 
It preserves traceability across:
 
- Validated engineering requirements
- Optimization result
- Selected candidate
- Engineering intelligence
- Engineering review
- Engineering recommendations
- Engineering report
- Geometry
- STEP output
 
Requirement extraction, requirement review, and interactive clarification remain outside the orchestrator because they require user interaction.
 
### Known Architectural Technical Debt
 
The current Streamlit product also directly coordinates the same public deterministic backend services for configured weighted-optimization and Pareto workflows because `EngineeringOrchestrator` does not yet expose every advanced optimization-selection configuration.
 
This is accepted non-blocking V2.0.0 technical debt.
 
Complete orchestration parity is deferred until after V2 freeze.
 
---
 
## Streamlit Product
 
The user-facing application is:
 
**Thermal Design Agent**
 
Subtitle:
 
**Engineering Design & Analysis**
 
Current product capability includes:
 
- Havells branding
- Natural-language requirement input
- Requirement review
- Interactive clarification
- Analysis configuration
- Forced-convection configuration
- Fan-coupled configuration
- Natural-convection orientation selection
- Natural-convection radiation selection
- Surface-emissivity configuration
- Optimization-strategy selection
- Weighted-objective configuration
- Pareto-front exploration
- Explicit engineer selection from Pareto designs
- Engineering design results
- Design-space statistics
- Flow performance where applicable
- Mass and material cost
- Natural-convection HTC decomposition
- Engineering review
- Engineering recommendations
- Validation requirements
- STEP download
- HTML engineering-report download
 
Two known cosmetic issues remain intentionally deferred:
 
- Sidebar collapse/expand arrow visibility
- Unnecessary horizontal scrolling in some layouts
 
They are not V2.0.0 release blockers.
 
---
 
## Installation
 
Create and activate a Python virtual environment, then install project dependencies:
 
```powershell
python -m pip install -r requirements.txt
```
 
CadQuery must be available in the active project environment for CAD and STEP generation.
 
---
 
## LLM Provider Configuration
 
Provider selection uses the environment variable:
 
```text
LLM_PROVIDER
```
 
Supported values:
 
```text
azure
gemini
mock
```
 
### Azure OpenAI
 
Required environment configuration includes:
 
```text
LLM_PROVIDER=azure
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_API_VERSION=...
AZURE_OPENAI_DEPLOYMENT=...
```
 
### Gemini
 
Required configuration includes:
 
```text
LLM_PROVIDER=gemini
GEMINI_API_KEY=...
```
 
An optional Gemini model may be configured with:
 
```text
GEMINI_MODEL=...
```
 
### Offline Mock
 
```text
LLM_PROVIDER=mock
```
 
Secrets must remain in the local environment / `.env` and must not be committed to source control.
 
---
 
## Running the Application
 
From the repository root:
 
```powershell
streamlit run app.py
```
 
---
 
## Regression References
 
These are regression references, not hard-coded application outputs.
 
### Forced Convection
 
Reference case approximately produces:
 
- Total candidates evaluated: 15,870
- Feasible candidates: 5,496
- Rejected candidates: 10,374
- Base thickness: 3.0 mm
- Fin height: 8.0 mm
- Fin thickness: 0.8 mm
- Fin spacing: 1.6 mm
- Fin count: 21
- Channel velocity: 7.8125 m/s
- Pressure drop: 86.1899 Pa
- Pumping power: 0.17238 W
- Thermal resistance: 0.680824 °C/W
- Estimated base temperature: 142.336 °C
 
### Natural Convection - Vertical / Radiation Off
 
Reference case approximately produces:
 
- Feasible candidates: 5,496
- Base thickness: 3.0 mm
- Fin height: 8.0 mm
- Fin thickness: 0.8 mm
- Fin spacing: 1.6 mm
- Fin count: 21
- Convective HTC: 13.8418 W/m²K
- Radiative HTC: 0 W/m²K
- Effective HTC: 13.8418 W/m²K
- Thermal resistance: 3.60029 K/W
- Estimated base temperature: 102.006 °C
 
Horizontal orientation and/or radiation intentionally change these values and may change the selected optimal geometry.
 
---
 
## Known V2.0.0 Limitations
 
The current release intentionally does not include:
 
- Additional heat-sink topologies beyond the principal plate-fin path
- Intermediate inclined natural-convection orientations
- Detailed inter-fin surface-to-surface radiation/view-factor modelling
- Independent radiative-surroundings temperature modelling
- Forced-convection radiation coupling
- Pin-fin natural convection
- Broad multi-material candidate optimization
- Variable fan-speed modelling
- Multiple-fan optimization
- Production supplier-capability databases
- CFD coupling
- OpenFOAM integration
- Experimental thermal-model calibration
- PDF report generation
- Enterprise authentication
- Engineering database integration
- Design-history persistence
 
Horizontal natural-convection predictions use reduced-order literature correlations and require final experimental and/or CFD validation, especially when candidate geometry extends outside the published validation range.
 
Manufacturing limits also require supplier confirmation before design release.
 
---
## Project-State Source of Truth
 
The detailed authoritative project-state document is:
 
```text
PROJECT_STATE.md
```
 
A concise mirror is maintained at:
 
```text
docs/PROJECT_STATE.md
```
 
The latest audited flattened snapshot before final release-cleanup edits is:
 
```text
entire_codebase 16.txt
```
 
A fresh flattened snapshot must be generated after final regression and before V2.0.0 is marked frozen.
 
---
 
## Post-V2 Development Areas
 
Potential V2.x / V3 work includes:
 
- Intermediate inclined natural-convection orientations
- Higher-fidelity horizontal natural-convection validation
- Detailed surface-to-surface radiation modelling
- Independent radiative-surroundings temperature modelling
- Forced-convection radiation coupling where justified
- Additional heat-sink topologies
- Expanded material optimization
- Expanded fan selection
- Fan-speed optimization
- CFD / OpenFOAM validation
- Experimental-model calibration
- Richer manufacturing and supplier databases
- Backend enforcement of convection-mode-compatible objectives
- Complete `EngineeringOrchestrator` parity
- Design history
- Engineering database integration
- Enterprise deployment
- User authentication
- Broader engineering-agent workflows
 
These are outside the V2.0.0 release boundary.
 
---
 
## Current Release State
 
**Thermal Design Agent V2.0.0**
 
**Status: FROZEN AFTER SUCCESSFUL FINAL V2.0.0 REGRESSION**
 
**Freeze Date: 25 August 2026**
 
The V2.0.0 release is feature complete and regression validated.
 
It now serves as the stable baseline for:
 
- Demonstration
- Internal engineering evaluation
- Further validation
- Controlled deployment experiments
- Future V2.x / V3 development
 
Additional safety, code-quality, CFD, experimental, or engineering-validation work may be performed against this baseline.
 
Such validation does not reopen the V2.0.0 feature scope unless a genuine release defect is identified.