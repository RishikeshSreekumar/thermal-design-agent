Thermal Design Agent - Engineering Project State
 
Current Release: V2.0.0
Status: FROZEN
Release Date: 25 August 2026
 
The authoritative detailed project state is maintained in:
 
"../PROJECT_STATE.md"
 
---
 
V2 Capability Summary
 
Thermal Design Agent V2.0.0 provides an end-to-end plate-fin heat-sink engineering workflow covering:
 
- Natural-language requirement extraction
- Requirement review and interactive clarification
- Validated engineering requirements
- Forced-convection optimization
- Natural-convection optimization
- Natural-convection orientation modelling
- Optional natural-convection thermal radiation
- Pressure-drop calculation
- Pumping-power calculation
- Manufacturability screening
- Material compatibility
- Candidate validation and selection
- Material mass calculation
- Material-cost calculation and budget filtering
- Minimum-thermal-resistance optimization
- Weighted multi-objective optimization
- Pareto-front optimization
- Explicit engineer selection from Pareto designs
- Engineering intelligence
- Deterministic engineering review
- Optional grounded AI review narrative
- Grounded engineering recommendations
- Engineering HTML report
- Geometry planning
- CadQuery CAD generation
- STEP export
- Streamlit product integration
 
---
 
Engineering Authority
 
Deterministic engineering calculations and deterministic engineering-review status are authoritative.
 
AI may assist with:
 
- Requirement understanding
- Engineering-review narrative
- Grounded recommendations
- Engineering communication
 
AI may not modify:
 
- Deterministic engineering calculations
- Feasibility
- Engineering-review status
- Deterministic engineering evidence
- Explicit engineering constraints
 
---
 
Forced-Convection Scope
 
V2 forced-convection capability includes:
 
- Fixed approach-air-velocity mode
- Fan-coupled mode
- Flow and hydraulic calculations
- Pressure drop
- Pumping power
- Forced-convection heat transfer
- Thermal resistance
- Base-temperature estimation
- Manufacturability screening
- Material compatibility
- Thermal, hydraulic, mass, and commercial constraints
- Minimum-thermal-resistance optimization
- Weighted multi-objective optimization
- Pareto optimization
- Engineering intelligence
- Engineering review
- Engineering recommendations
- Report generation
- CAD and STEP generation
 
Thermal radiation is not included in the current forced-convection model.
 
---
 
Natural-Convection Scope
 
V2 natural-convection capability includes:
 
- Plate-fin heat sinks
- Vertical orientation
- Horizontal orientation with fins facing upward
- Horizontal orientation with fins facing downward
- Clarification when horizontal fin-facing direction is ambiguous
- Existing Churchill-Chu-based vertical natural-convection path
- Tari-Mehrtash reduced-order horizontal plate-fin correlations
- Iterative temperature/convection solution
- Optional thermal-radiation coupling
- Explicit surface emissivity
- Radiative surroundings constrained to ambient-air temperature
- Separate convective, radiative, and effective heat-transfer coefficients
- Natural-convection optimization
- Minimum-thermal-resistance selection
- Weighted optimization using compatible objectives
- Pareto optimization using compatible objectives
- Engineering intelligence
- Engineering review
- Engineering recommendations
- Engineering report
- CAD and STEP generation
- Streamlit integration
 
Known natural-convection limitations:
 
- Intermediate inclined orientations are not modeled
- Horizontal correlation applicability requires experimental and/or CFD validation for final designs, particularly where geometry extends beyond the published validation range
- Radiation uses a gray, diffuse large-surroundings approximation
- Detailed inter-fin surface-to-surface radiation and view factors are not modeled
- Radiative surroundings temperature cannot currently differ from ambient-air temperature
 
---
 
Commercial / Currency Scope
 
Default Havells demonstration currency:
 
- INR
 
Foreign supplier profiles may use another explicit ISO-style currency such as USD.
 
Rules:
 
- Every material-cost profile preserves its own currency
- Every material-cost result preserves that currency
- Every budget carries a currency
- Cost and budget may be compared only when currencies match
- No silent or automatic exchange-rate conversion is performed
- Demonstration prices remain illustrative until approved procurement values are supplied
 
---
 
Application Architecture
 
The canonical backend orchestration boundary is:
 
"EngineeringOrchestrator"
 
The orchestrated result preserves traceability across:
 
- Engineering requirements
- Optimization result
- Selected design
- Engineering intelligence
- Engineering review
- Engineering recommendations
- Engineering report
- Geometry
- STEP output
 
Requirement extraction, review, and interactive clarification remain outside the orchestrator because they require user interaction.
 
Current V2 architectural technical debt:
 
- EngineeringOrchestrator does not yet expose every advanced optimization-selection configuration used by the Streamlit product
- Configured weighted and Pareto Streamlit workflows therefore coordinate the same public deterministic backend services directly
- Complete orchestration parity is deferred until after V2.0.0 freeze
 
This does not alter deterministic engineering calculations or selection results.
 
---
 
LLM Providers
 
Supported providers:
 
- Azure OpenAI
- Google Gemini
- Mock Provider
 
Typical usage:
 
- Office environment: Azure OpenAI
- Personal development environment: Gemini
- Offline regression: Mock Provider
 
Provider selection does not alter deterministic engineering calculations.
 
---
 
V2 Physical / Model Limitations
 
The following limitations are intentionally retained:
 
- Plate-fin heat sink remains the principal supported topology
- Intermediate inclined natural-convection orientations are not modeled
- Horizontal natural-convection correlations require final experimental and/or CFD validation
- Detailed inter-fin radiation/view-factor modelling is not included
- Independent radiative-surroundings temperature modelling is not included
- Forced-convection radiation is not included
- Pin-fin natural convection is not included
- Generic manufacturing capability limits require supplier review
- Broad multi-material candidate optimization is not implemented
- CFD coupling is not included
- OpenFOAM integration is not included
- Experimental thermal-model calibration is not included
- Additional heat-sink topologies are not included
- Fan-speed scaling is not implemented
- Current fan-coupled optimization supports one fan
 
Known non-blocking Streamlit cosmetic issues remain deferred:
 
- Sidebar collapse/expand arrow visibility
- Unnecessary horizontal scrolling in some layouts
 
These cosmetic issues are not V2.0.0 release blockers.
 
---
 
Regression State
 
The original V2 regression baseline was completed on 12 August 2026.
 
The release was subsequently reopened before final freeze to integrate:
 
- Vertical / horizontal natural-convection orientation support
- Horizontal fins-up and fins-down correlations
- Natural-convection thermal radiation
- Convective / radiative / effective HTC traceability
- Requirement extraction and clarification for orientation/radiation
- Streamlit configuration and output presentation
- Engineering-intelligence traceability
- Engineering-report traceability
 
Focused regressions for this extension have passed.
 
Release-cleanup work has also corrected stale regression fixtures identified during the snapshot-16 audit.
 
A complete final V2.0.0 regression sweep must pass before the release is marked frozen.
 
---
 
Snapshot State
 
The latest audited flattened snapshot before final release-cleanup edits is:
 
"entire_codebase 16.txt"
 
Snapshot 16 contains the complete natural-convection orientation and radiation implementation.
 
Release-cleanup edits were made after snapshot 16.
 
A fresh flattened snapshot must therefore be generated after final regression and before V2.0.0 is declared frozen.
 
---
 
Post-V2 Opportunities
 
Potential V2.x / V3 development areas include:
 
- Intermediate inclined natural-convection orientations
- Higher-fidelity natural-convection validation
- Detailed inter-fin and surface-to-surface radiation modelling
- Independent radiative-surroundings temperature modelling
- Forced-convection radiation coupling if justified
- Additional heat-sink topologies
- Experimental thermal-model calibration
- CFD/OpenFOAM validation
- Expanded material selection and optimization
- Expanded fan selection
- Variable fan-speed modelling
- Richer supplier and manufacturing databases
- Complete EngineeringOrchestrator parity for all selection workflows
- Backend enforcement of convection-mode-compatible optimization objectives
- Engineering design history
- Engineering database integration
- Enterprise deployment
- User authentication
- Broader engineering-agent workflows
 
These are outside the V2.0.0 release boundary.
 
---
 
Current Release State
 
Thermal Design Agent V2.0.0
 
Status: FROZEN AFTER SUCCESSFUL FINAL V2.0.0 REGRESSION
 
V2.0.0 feature development and final functional validation are complete.
 
The release passed:
 
- Complete offline deterministic regression
- Live Azure OpenAI integration
- Natural-convection orientation and radiation validation
- Engineering review and recommendation workflows
- Streamlit product smoke testing
- CAD / STEP generation
 
No known functional V2.0.0 release blocker remains.
 
V2.0.0 was frozen on 25 August 2026 and now serves as the stable project baseline.
 
Additional internal safety and engineering-validation reviews may continue without adding new capability to the frozen release.
 