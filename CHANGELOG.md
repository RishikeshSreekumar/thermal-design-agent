# Changelog
 
All significant development changes to the Thermal Design Agent project are documented in this file.
 
The repository was originally developed under the internal name **Thermal AI Engineer**.
 
---
 
# Version 2.0.0
 
**Status:** FROZEN  
**Release Date:** 25 August 2026
 
V2.0.0 is the first complete release of the current Thermal Design Agent architecture.
 
An initial V2 engineering regression baseline was completed on 12 August 2026. The release was subsequently reopened before final freeze to integrate natural-convection orientation modelling, optional thermal radiation, and their complete product, intelligence, and reporting integration.
 
Final feature development, regression, live-provider validation, product smoke testing, documentation reconciliation, and release cleanup were completed before the final freeze on **25 August 2026**.
 
---
 
## Major V2 Capabilities
 
Added or completed:
 
- Forced-convection plate-fin heat-sink optimization
- Natural-convection plate-fin heat-sink optimization
- Fixed approach-air-velocity mode
- Fan-coupled airflow mode
- Pressure-drop calculation
- Pumping-power calculation
- Thermal-temperature constraints
- Pressure-drop constraints
- Pumping-power constraints
- Manufacturability screening
- Material compatibility
- Solid-volume and mass calculation
- Material-cost calculation
- Material-cost budget filtering
- Currency-safe commercial modelling
- Minimum-thermal-resistance optimization
- Weighted multi-objective optimization
- Pareto-front optimization
- Explicit engineer selection from Pareto alternatives
- Engineering intelligence
- Deterministic engineering review
- Optional grounded AI review synthesis
- Grounded engineering recommendations
- Engineering report generation
- CadQuery geometry generation
- STEP export
- Streamlit product integration
- Azure OpenAI provider
- Google Gemini provider
- Offline Mock Provider
 
---
 
## Engineering Authority and AI Safety
 
V2 establishes the following engineering-authority model:
 
- Deterministic physics owns engineering calculations
- Deterministic engineering rules own feasibility
- Deterministic assessments own engineering-review status
- AI output must remain grounded in deterministic evidence
- AI may not override deterministic engineering-review status
- AI may not fabricate engineering evidence
- AI may not silently remove represented engineering constraints
- AI/provider failure must not invalidate valid deterministic engineering
 
AI is used for:
 
- Natural-language requirement extraction
- Clarification interaction
- Grounded engineering-review narrative
- Grounded engineering recommendations
- Engineering communication
 
---
 
## Requirement Engine
 
Expanded the engineering requirement schema to support:
 
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
 
Added deterministic requirement review and clarification.
 
Engineering constraints represented by the requirement schema must not be silently discarded by LLM extraction.
 
Explicit material restrictions that exclude the currently supported Aluminium 6063-T5 design path are rejected rather than silently ignored.
 
Natural-convection requirement handling includes:
 
- Established vertical default when orientation is not specified
- Explicit clarification when a horizontal heat sink is specified without fin-facing direction
- No invented surface emissivity when radiation is requested without an emissivity value
 
Azure OpenAI, Gemini, and Mock Provider extraction paths support the current schema.
 
---
 
## Forced-Convection Engineering
 
Preserved and expanded the plate-fin forced-convection engineering path.
 
Current capability includes:
 
- Fixed approach-air-velocity mode
- Fan-coupled optimization mode
- Flow-area calculation
- Channel-velocity calculation
- Hydraulic-diameter calculation
- Reynolds-number calculation
- Flow-regime-aware heat-transfer correlation selection
- Pressure-drop calculation
- Pumping-power calculation
- Dedicated thermal-solver integration
- Manufacturability-aware candidate exploration
- Candidate validation
- Thermal-temperature constraints
- Pressure-drop constraints
- Pumping-power constraints
- Mass calculation
- Material-cost calculation
- Material-cost budget filtering
- Minimum-thermal-resistance selection
- Weighted optimization
- Pareto optimization
- Engineering intelligence
- Engineering review
- Engineering recommendations
- Engineering reporting
- CAD generation
- STEP generation
- Streamlit integration
 
Current fan-coupled restrictions:
 
- One fan
- `speed_fraction = 1.0`
 
Thermal radiation is not included in the current forced-convection model.
 
---
 
## Natural-Convection Engineering
 
Added a dedicated natural-convection architecture including:
 
- Reusable convection-state model
- Natural-convection physics
- Dedicated natural-convection solver
- Plate-fin natural-convection solver
- Iterative temperature/convection coupling
- Thermal-solver integration
- Optimizer integration
- Candidate validation
- Engineering-intelligence integration
- Engineering-review integration
- Engineering-recommendation integration
- Engineering-report integration
- Streamlit integration
- Geometry-planning integration
- STEP generation
 
### Supported Orientations
 
V2.0.0 supports:
 
- Vertical
- Horizontal - fins upward
- Horizontal - fins downward
 
Intermediate inclined orientations are not modeled.
 
### Vertical Natural Convection
 
The established vertical natural-convection path is preserved using the existing Churchill-Chu-based reduced-order model.
 
Legacy vertical numerical behaviour was regression-protected while adding the new orientation capability.
 
### Horizontal Natural Convection
 
Added orientation-specific Tari-Mehrtash reduced-order plate-fin correlations for:
 
- Horizontal fins upward
- Horizontal fins downward
 
Correlation applicability must be validated for final designs where geometry extends beyond the published validation range.
 
### Thermal Radiation
 
Added optional thermal-radiation coupling for natural convection.
 
The current model includes:
 
- Explicit surface emissivity
- Gray, diffuse surface assumption
- Exchange with large surroundings
- Linearized radiative heat-transfer coefficient
- Iterative coupling with natural convection
- Separate convective HTC
- Separate radiative HTC
- Effective HTC
 
The thermal state preserves:
 
```text
h_effective = h_convective + h_radiative
```
 
The current reduced-order model constrains:
 
```text
Radiative surroundings temperature = ambient-air temperature
```
 
Detailed inter-fin surface-to-surface radiation and view factors are not included.
 
---
 
## Optimization and Candidate Evaluation
 
Added or completed:
 
- Candidate-state validation
- Optimization-selection infrastructure
- Minimum-thermal-resistance selection
- Weighted-objective optimization
- Pareto-front optimization
- Candidate-objective normalization
- Solid-volume calculation
- Mass calculation
- Material-cost calculation
- Material compatibility handling
- Thermal-temperature requirement checks
- Pressure-drop requirement checks
- Pumping-power requirement checks
- Material-cost budget checks
- Optimization-selection metadata
- Traceability from validated requirements through selected designs
 
Four registered optimization objectives are currently available:
 
1. Thermal resistance
2. Pressure drop
3. Pumping power
4. Mass
 
Material cost is maintained as deterministic commercial state and a budget constraint rather than a registered optimization objective.
 
Pareto optimization does not automatically declare one design universally best.
 
The engineer explicitly selects the final design from the Pareto set.
 
Natural-convection Streamlit workflows expose only physically applicable objectives such as thermal resistance and mass.
 
---
 
## Material Cost and Currency
 
Added deterministic material-cost state and budget handling.
 
Current Havells demonstration material-cost profiles use:
 
- INR
 
The architecture permits other explicitly defined currencies such as USD for foreign supplier profiles.
 
Currency rules:
 
- Every cost profile preserves its own currency
- Every calculated cost result preserves that currency
- Every budget has an explicit currency
- Cost and budget may be compared only when currencies match
- Different currencies may coexist in the material-cost database
- No silent currency conversion is performed
- No implicit exchange-rate model is used
 
Demonstration prices remain illustrative until approved procurement data is supplied.
 
---
 
## Manufacturability
 
Added deterministic manufacturability assessment before full thermal candidate evaluation.
 
The current Aluminium 6063-T5 extrusion capability includes checks such as:
 
- Minimum fin thickness
- Minimum fin spacing
- Maximum fin-height / fin-thickness ratio
- Fin-height / spacing ratio
- Base-thickness limits
- Maximum total height
 
Current manufacturing limits are generic engineering assumptions.
 
Supplier confirmation remains required before release for manufacture.
 
---
 
## Engineering Intelligence
 
Added structured deterministic engineering intelligence including:
 
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
- Forced-airflow performance evaluation
 
Natural-convection designs intentionally suppress forced-airflow insights and forced-airflow assessments.
 
Natural-convection thermal evidence additionally preserves, where applicable:
 
- Orientation
- Radiation enabled/disabled state
- Surface emissivity
- Convective heat-transfer coefficient
- Radiative heat-transfer coefficient
- Effective heat-transfer coefficient
 
---
 
## Engineering Review
 
Added the complete engineering-review architecture:
 
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
 
The deterministic engineering-review status remains authoritative.
 
AI review synthesis may enrich communication fields but cannot modify:
 
- Deterministic status
- Deterministic findings
- Deterministic engineering evidence
- Required actions
- Validation requirements
- Source traceability
 
If AI engineering-review synthesis fails, the application may safely fall back to the deterministic engineering review.
 
---
 
## Engineering Recommendations
 
Added grounded engineering recommendations based on the completed engineering review.
 
AI recommendations remain non-authoritative.
 
Fallback behavior ensures:
 
- AI/provider/parsing failure does not invalidate deterministic engineering
- Engineering intelligence remains available
- Engineering review remains available
- Engineering report generation may continue
- Geometry generation may continue
- STEP generation may continue
- Recommendation results may safely contain no AI-generated recommendations
 
Strict provider-failure propagation remains available for regression testing.
 
---
 
## Engineering Report
 
Added the V2 engineering-report system:
 
- Immutable report models
- Structured engineering sections
- Authoritative engineering-review status
- Engineering traceability
- Havells branding
- Compact engineering tables
- Professional typography
- Engineering review
- Recommendations
- Validation requirements
- Natural-convection orientation presentation
- Radiation configuration presentation
- Convective / radiative / effective HTC presentation
- Self-contained HTML rendering
 
Canonical V2 report format:
 
- HTML
 
PDF report generation is deferred beyond V2.0.0.
 
---
 
## CAD and STEP
 
Preserved deterministic geometry planning and CadQuery-based CAD generation.
 
Integrated:
 
- Geometry planning
- CAD generation
- STEP export
- Streamlit STEP download
- Application workflow traceability
 
Current CAD topology:
 
- Plate-fin heat sink
 
---
 
## Application Architecture
 
Added:
 
- `EngineeringOrchestrator`
- `EngineeringApplicationResult`
 
`EngineeringOrchestrator` is the canonical backend orchestration boundary for the standard application workflow.
 
The application result preserves traceability across approximately:
 
- Engineering requirements
- Optimization result
- Selected candidate
- Engineering intelligence
- Engineering review
- Engineering recommendations
- Engineering report
- Geometry
- STEP output
 
Requirement extraction, requirement review, and interactive clarification remain outside the orchestrator because they require user interaction.
 
### Accepted V2 Architectural Technical Debt
 
The Streamlit application directly coordinates the same public deterministic backend services for some configured weighted and Pareto workflows because `EngineeringOrchestrator` does not yet expose every advanced optimization-selection configuration.
 
This does not change deterministic engineering results.
 
Complete orchestration parity is deferred until after V2.0.0 freeze.
 
---
 
## Streamlit Application
 
Updated the user-facing product identity to:
 
**Thermal Design Agent**
 
Subtitle:
 
**Engineering Design & Analysis**
 
V2 Streamlit capability includes:
 
- Havells branding
- Professional engineering-tool interface
- Natural-language requirement input
- Requirement review
- Interactive clarification
- Analysis configuration
- Forced-convection execution
- Fan-coupled configuration
- Natural-convection execution
- Natural-convection orientation configuration
- Natural-convection thermal-radiation configuration
- Surface-emissivity configuration
- Minimum-thermal-resistance optimization
- Weighted-objective configuration
- Pareto-front exploration
- Explicit engineer selection from Pareto alternatives
- Engineering design results
- Design-space evaluation
- Forced-airflow information when applicable
- Natural-convection HTC decomposition
- Mass
- Material cost
- Engineering review
- Engineering recommendations
- Validation requirements
- STEP download
- HTML engineering-report download
 
Known non-blocking cosmetic issues remain deferred:
 
- Sidebar collapse/expand arrow visibility
- Unnecessary horizontal scrolling in some layouts
 
These are not V2.0.0 release blockers.
 
---
 
## Regression History
 
### Initial V2 Regression Baseline - 12 August 2026
 
The initial V2 engineering architecture passed regression covering:
 
- Python compilation
- Convection-state checks
- Forced-convection solver
- Thermal solver
- Natural-convection physics
- Natural-convection solver
- Plate-fin natural-convection solver
- Forced-convection optimizer
- Fan-coupled optimizer
- Natural-convection optimizer
- Optimization-selection integration
- Thermal-temperature requirements
- Airflow-performance requirements
- Material-compatibility requirements
- Engineering-intelligence pipeline
- Natural-convection intelligence
- Engineering-assessment engine
- Engineering-review source
- Engineering-review structure
- Grounded AI engineering-review logic
- Deterministic engineering-review fallback
- Engineering-recommendation payload
- Grounded engineering-recommendation logic
- Engineering-recommendation fallback
- Engineering-report models
- Engineering-report builder
- Engineering-report HTML renderer
- CAD generation
- STEP generation
- Natural-convection orchestrator
- Forced-convection orchestrator
 
A live Azure OpenAI requirement-extraction regression also passed.
 
This was an engineering baseline, not the final V2.0.0 release freeze.
 
### Natural-Convection Orientation and Radiation Extension
 
The V2 release was subsequently reopened before final freeze.
 
Added and regression-tested:
 
- Explicit natural-convection configuration model
- Vertical orientation
- Horizontal fins-up orientation
- Horizontal fins-down orientation
- Ambiguous-horizontal clarification
- Tari-Mehrtash reduced-order horizontal plate-fin correlations
- Gray-surface thermal-radiation model
- Iterative convection/radiation coupling
- Separate convective, radiative, and effective HTC state
- Candidate and result propagation
- Azure OpenAI requirement extraction
- Gemini requirement extraction
- Mock Provider requirement extraction
- Streamlit configuration
- Engineering-intelligence traceability
- Engineering-report traceability
 
The legacy vertical, radiation-disabled numerical path was preserved.
 
Forced-convection and fan-coupled regressions remained unchanged.

### Final Freeze Regression
 
The complete final V2.0.0 regression passed successfully.
 
Validated release gates included:
 
- Complete Python compilation
- All `tests/test_*.py` regression modules
- All root `test_*.py` regression modules
- Forced-convection optimization
- Fan-coupled optimization
- Natural-convection vertical modelling
- Horizontal fins-up modelling
- Horizontal fins-down modelling
- Natural-convection thermal radiation
- Convection/radiation iterative coupling
- Candidate-state validation
- Thermal, hydraulic, material, mass, cost, and budget constraints
- Minimum-thermal-resistance optimization
- Weighted multi-objective optimization
- Pareto-front optimization
- Explicit engineer Pareto selection
- Engineering intelligence
- Deterministic engineering review
- Grounded AI engineering review
- Grounded engineering recommendations
- Azure OpenAI live-provider integration
- Natural-convection orientation/radiation extraction through Azure OpenAI
- End-to-end engineering orchestration
- Engineering-report generation
- Streamlit product smoke testing
- Geometry planning
- CadQuery CAD generation
- STEP export
 
No known functional release blocker remained after final regression.
 
**Thermal Design Agent V2.0.0 was therefore frozen on 25 August 2026.**
 
Further capability development will proceed beyond the frozen V2.0.0 baseline.
 
 
---
 
## Forced-Convection Regression Reference
 
Reference forced-convection regression approximately produces:
 
- Total candidates evaluated: 15,870
- Feasible candidates: 5,496
- Rejected candidates: 10,374
- Selected base thickness: 3.0 mm
- Selected fin height: 8.0 mm
- Selected fin thickness: 0.8 mm
- Selected fin spacing: 1.6 mm
- Selected fin count: 21
- Channel velocity: approximately 7.8125 m/s
- Pressure drop: approximately 86.19 Pa
- Pumping power: approximately 0.17238 W
- Thermal resistance: approximately 0.680824 °C/W
- Estimated base temperature: approximately 142.336 °C
 
These values are regression references and are not hard-coded design outputs.
 
---
 
## Natural-Convection Vertical / Radiation-Off Regression Reference
 
Reference natural-convection regression approximately produces:
 
- Feasible candidates: 5,496
- Selected base thickness: 3.0 mm
- Selected fin height: 8.0 mm
- Selected fin thickness: 0.8 mm
- Selected fin spacing: 1.6 mm
- Selected fin count: 21
- Convective heat-transfer coefficient: approximately 13.8418 W/m²K
- Radiative heat-transfer coefficient: 0 W/m²K
- Effective heat-transfer coefficient: approximately 13.8418 W/m²K
- Thermal resistance: approximately 3.60029 K/W
- Estimated base temperature: approximately 102.006 °C
 
These values specifically represent the established vertical, radiation-disabled regression path.
 
Horizontal orientations and/or radiation intentionally change the resulting thermal state and may change the selected optimal geometry.
 
---
 
## Known V2.0.0 Limitations
 
The following limitations are intentionally retained:
 
- Plate-fin heat sink remains the principal supported topology
- Intermediate inclined natural-convection orientations are not modeled
- Horizontal natural-convection correlations require experimental and/or CFD validation for final designs
- Detailed inter-fin surface-to-surface radiation and view factors are not modeled
- Radiative surroundings temperature cannot currently differ from ambient-air temperature
- Forced-convection radiation is not included
- Pin-fin natural convection is not included
- Generic manufacturing capability limits require supplier validation
- Broad multi-material candidate optimization is not implemented
- Fan-speed scaling is not implemented
- Multiple-fan optimization is not implemented
- CFD/OpenFOAM coupling is not implemented
- Experimental thermal-model calibration is not implemented
- Additional heat-sink topologies are not implemented
- PDF report generation is not implemented
- Enterprise authentication is not implemented
- Engineering database integration is not implemented
- Design-history persistence is not implemented
 
---
 
## Release-Cleanup Corrections
 
Final V2 release cleanup corrected stale repository artifacts identified during the `entire_codebase 16.txt` audit:
 
- Updated the material-cost database regression to reflect INR demonstration profiles and explicit mixed-currency support
- Preserved the prohibition on silent currency conversion
- Updated the root validation regression to reflect the current parser/review/strict-validation architecture
- Removed obsolete natural-convection limitation fixtures claiming that radiation and horizontal orientation are unsupported
- Reconciled `PROJECT_STATE.md`
- Reconciled `docs/PROJECT_STATE.md`
- Reconciled `README.md`
- Reconciled this changelog
 
---
 
# Version 1.1.0-dev
 
## Added
 
- Modular LLM provider architecture
- Common LLM provider interface
- Azure OpenAI provider
- Gemini provider
- Offline Mock Provider
- Environment-based provider factory
- Active provider identification
 
## Improved
 
- Azure OpenAI requirement-extraction prompt
- Requirement clarification workflow
- Provider-independent application architecture
- Protection against inferring missing maximum-height values
 
## Validated
 
- Azure OpenAI provider
- Gemini provider
- Mock Provider
- Provider factory
- End-to-end development application workflow
 
## Development Environment Support
 
- Office environment: Azure OpenAI
- Personal development environment: Gemini
- Offline development and regression: Mock Provider
 
---
 
# Version 1.0.0
 
## Initial Functional Prototype
 
- Natural-language engineering requirement extraction
- Structured requirement parsing
- Thermal equation library
- Parametric forced-convection plate-fin heat-sink optimization
- Geometry planning
- CadQuery model generation
- STEP file export
- Streamlit user interface
- Initial Gemini development path
- Migration to Azure OpenAI for office development
- Initial end-to-end application validation