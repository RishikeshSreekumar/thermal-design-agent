Thermal Design Agent - PROJECT_STATE
 
Project Status: V2.0.0 FROZEN
Current Version: 2.0.0
Release Date: 25 August 2026
Current Milestone: V2.0.0 Complete and Frozen
Immediate Next Step: Preserve V2.0.0 as the stable baseline and perform any additional safety audit without adding new V2 features
 
---
 
# 1. Project Vision
 
Develop serious internal thermal-engineering software capable of converting natural-language engineering requirements into optimized, manufacturable, explainable, reviewable, and CAD-ready thermal designs.
 
The application is intended to augment engineers rather than replace deterministic engineering physics.
 
Core principle:
 
«Deterministic engineering calculations own engineering truth.
 
AI assists with requirement understanding, engineering communication, grounded review narrative, and grounded recommendations.»
 
AI must never silently change engineering calculations, feasibility, constraints, or deterministic engineering-review status.
 
---
 
# 2. Product Identity
 
User-facing application name:
 
Thermal Design Agent
 
Preferred subtitle:
 
Engineering Design & Analysis
 
The repository, packages, historical documentation, and some internal source-code references may continue to use Thermal AI Engineer.
 
No destructive global internal rename is required for V2.
 
Havells logo:
 
"assets/havells_logo.png"
 
---
 
# 3. V2 End-to-End Architecture
 
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
OptimizationResult
        |
        v
EngineeringIntelligencePipeline
        |
        +--> Engineering Evidence
        +--> Engineering Insights
        +--> Engineering Assessments
        |
        v
EngineeringReviewService
        |
        +--> Deterministic Review
        +--> Optional Grounded AI Enrichment
        |
        v
EngineeringRecommendationService
        |
        v
EngineeringReportBuilder
        |
        v
EngineeringReportHTMLRenderer
        |
        v
GeometryPlanner
        |
        v
CADGenerator
        |
        v
STEP Output
 
The canonical backend orchestration boundary is:
 
"EngineeringOrchestrator"
 
Requirement extraction, requirement review, and clarification remain outside the orchestrator because they are interactive.
 
The current Streamlit product also directly coordinates existing public backend services for configured weighted-optimization and Pareto workflows. This preserves working product capability but means complete orchestration parity is not yet centralized in EngineeringOrchestrator.
 
This is accepted non-blocking architectural technical debt for V2.0.0.
 
 
---
 
# 4. Engineering Authority Model
 
Deterministic Layer
 
The deterministic layer owns:
 
- Engineering requirements
- Geometry
- Fluid properties
- Flow calculations
- Hydraulic calculations
- Reynolds number
- Heat-transfer correlations
- Convection calculations
- Pressure drop
- Pumping power
- Thermal resistance
- Estimated base temperature
- Manufacturability
- Optimization
- Candidate selection
- Engineering assessments
- Engineering-review status
- Geometry planning
- CAD geometry
 
AI Layer
 
AI may assist with:
 
- Natural-language requirement extraction
- Clarification interaction
- Engineering-review narrative
- Grounded trade-offs
- Grounded recommendations
- Engineering communication
 
AI may not:
 
- Alter deterministic calculations
- Invent engineering evidence
- Override deterministic review status
- Silently remove supplied engineering constraints
- Convert unsupported assumptions into engineering facts
 
---
 
# 5. Supported V2 Design Scope
 
Topology
 
V2 principal supported topology:
 
- Plate-fin heat sink
 
Forced Convection
 
Supported capability includes:
 
- Fixed approach-air-velocity mode
- Fan-coupled mode
- Flow geometry
- Hydraulic calculations
- Reynolds number
- Pressure-loss calculation
- Pumping-power calculation
- Forced-convection heat transfer
- Thermal-resistance calculation
- Base-temperature estimation
- Manufacturability screening
- Material/process consideration
- Optimization
- Candidate selection
- Engineering intelligence
- Engineering review
- Engineering recommendations
- Engineering report
- CAD generation
- STEP export
- Streamlit integration
 
Natural Convection
 
Supported capability includes:
 
- Plate-fin heat sinks
- Vertical orientation
- Horizontal orientation with fins facing upward
- Horizontal orientation with fins facing downward
- Explicit clarification when horizontal orientation is supplied without fin-facing direction
- Natural-convection physics
- Existing Churchill-Chu-based vertical convection path
- Orientation-specific Tari-Mehrtash reduced-order horizontal plate-fin correlations
- Iterative temperature/convection coupling
- Optional thermal-radiation coupling
- Explicit surface emissivity
- Radiative surroundings constrained to ambient-air temperature in the current reduced-order model
- Separate convective, radiative, and effective heat-transfer coefficients
- Natural-convection thermal optimization
- Candidate validation
- Minimum-thermal-resistance selection
- Weighted optimization using natural-convection-compatible objectives
- Pareto optimization using natural-convection-compatible objectives
- Engineering intelligence
- Engineering review
- Engineering recommendations
- Engineering report
- CAD generation
- STEP export
- Streamlit integration
 
Natural-convection mode does not generate forced-airflow insights or forced-airflow assessments.

---
 
# 6. Known V2 Physical Limitations
 
The following limitations are intentionally retained in V2.0.0:
 
- Plate-fin heat sink remains the principal supported topology
- Intermediate inclined natural-convection orientations are not modeled
- Horizontal natural-convection calculations use orientation-specific reduced-order correlations that require final experimental and/or CFD validation, particularly where candidate geometry extends beyond the published validation range
- Natural-convection radiation uses a gray, diffuse surface exchanging with large surroundings
- Detailed inter-fin surface-to-surface radiation and view factors are not modeled
- Radiative surroundings temperature is currently constrained to equal ambient-air temperature
- Radiation is integrated only into the natural-convection model; the current forced-convection model excludes radiation
- Pin-fin natural convection is not included
- Generic manufacturing capability limits require supplier review
- Broad multi-material design optimization is not implemented
- CFD coupling is not included
- OpenFOAM integration is not included
- Experimental thermal-model calibration is not included
- Additional heat-sink topologies are not included
 
These limitations are explicit engineering validation considerations rather than hidden assumptions.
 
---
 
# 7. Requirement Engine
 
Supported LLM providers:
 
- Azure OpenAI
- Google Gemini
- Mock Provider
 
Typical environment usage:
 
- Office laptop: Azure OpenAI
- Personal laptop: Gemini
- Offline regression: Mock Provider
 
Provider choice has no effect on deterministic engineering calculations.
 
The V2 requirement schema preserves:
 
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
- Natural-convection orientation
- Natural-convection radiation enable/disable state
- Surface emissivity
- Radiative surroundings temperature
 
Engineering constraints explicitly represented by the requirement schema must not be silently dropped by the LLM extraction boundary.

For natural convection, an explicitly stated but directionally ambiguous horizontal orientation is clarified rather than silently mapped to another orientation.
 
Surface emissivity is not invented when radiation is requested and the value is missing.
 
V2 currently designs around the supported Aluminium 6063-T5 extrusion path.
 
If an explicit material restriction excludes the currently supported material, the requirement is rejected rather than silently producing an incompatible aluminium design.
 
---
 
# 8. Physics and Thermal Architecture
 
The V2 deterministic engineering foundation includes:
 
- Fluid-property models
- Flow-geometry models
- Hydraulic models
- Forced-convection correlations
- Natural-convection physics for vertical, horizontal fins-up, and horizontal fins-down orientations
- Orientation-specific natural-convection correlations
- Gray-surface thermal-radiation model for natural convection
- Iterative convection/radiation coupling
- Separate convective, radiative, and effective heat-transfer coefficients
- Fin-efficiency calculations
- Heat-transfer surface-area calculations
- Thermal-resistance calculations
- Pressure-drop calculations
- Pumping-power calculations
- Flow-network calculations
- Fan/system coupling
- Dedicated thermal solver
- Natural-convection iterative solver
 
The architecture maintains separation between:
 
- Flow resolution
- Convection resolution
- Thermal calculations
- Optimization
- Manufacturability
- Candidate selection
 
---
 
# 9. Optimization
 
The optimization architecture includes:
 
- Manufacturability-aware candidate exploration
- Forced-convection candidate evaluation
- Natural-convection candidate evaluation
- Candidate-state validation
- Minimum-thermal-resistance selection
- Weighted-objective optimization infrastructure
- Pareto-front optimization infrastructure
- Mass calculation
- Material-cost calculation
- Material compatibility handling
- Requirement-based temperature evaluation
- Requirement-based pressure-drop evaluation
- Requirement-based pumping-power evaluation
- Optimization selection metadata
 
The application preserves traceability from requirements through candidate evaluation and final selected design.
 
---
 
# 10. Engineering Intelligence
 
The engineering-intelligence architecture is complete for V2.
 
Major components include:
 
- "EngineeringAssessmentEngine"
- "EngineeringIntelligencePipeline"
- Engineering context
- Engineering evidence
- Engineering insights
- Engineering assessments
- Airflow analyzer
- Geometry analyzer
- Thermal analyzer
- Optimization analyzer
- Model-limitation analyzer
- Manufacturability evaluator
- Thermal-margin evaluator
- Airflow-performance evaluator
 
Natural-convection mode suppresses forced-airflow engineering content.
 
Engineering intelligence remains deterministic.
 
---
 
# 11. Engineering Review
 
The engineering-review architecture is complete for V2.
 
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
 
The deterministic review status is authoritative.
 
AI may enrich communication fields but cannot modify:
 
- Deterministic engineering-review status
- Deterministic engineering evidence
- Deterministic findings
- Required actions
- Validation requirements
- Engineering traceability
 
If engineering-review AI synthesis fails while fallback is enabled, the valid deterministic engineering review is returned.
 
---
 
# 12. Engineering Recommendations
 
Grounded engineering recommendations are generated from the completed engineering review.
 
AI-generated recommendations are non-authoritative.
 
If recommendation synthesis fails while fallback is enabled:
 
- Deterministic engineering remains valid
- Engineering intelligence remains valid
- Engineering review remains valid
- Report generation may continue
- Geometry generation may continue
- STEP generation may continue
- The recommendation result may contain no AI-generated recommendations
 
Strict provider-failure propagation remains available for regression testing.
 
---
 
# 13. Engineering Report
 
The V2 engineering-report architecture is complete.
 
Capabilities include:
 
- Immutable report models
- Structured engineering-report sections
- Authoritative engineering-review status
- Engineering traceability
- Havells branding
- Professional typography
- Compact engineering tables
- Engineering-review presentation
- Recommendation presentation
- Validation requirements
- Self-contained HTML rendering
 
Canonical V2 report format:
 
HTML
 
PDF generation is intentionally deferred beyond V2.0.0.
 
---
 
# 14. Geometry, CAD and STEP
 
Completed capability includes:
 
- "GeometryPlanner"
- "CADGenerator"
- CadQuery plate-fin geometry generation
- STEP export
- Orchestrator integration
- Streamlit STEP download
 
The selected deterministic thermal geometry is passed into geometry planning and CAD generation.
 
The current CAD topology is a plate-fin heat sink.
 
---
 
# 15. End-to-End Orchestrator
 
The canonical backend application boundary is:
 
"EngineeringOrchestrator"
 
The orchestrated application result preserves approximately:
 
- Validated engineering requirements
- Optimization result
- Selected candidate
- Engineering-intelligence result
- Engineering-review result
- Engineering-recommendation result
- Engineering report
- Geometry
- STEP file
 
"EngineeringApplicationResult" protects traceability between these stages.
 
Both forced- and natural-convection orchestrator paths have regression coverage.
 
Current V2 architectural limitation:
 
- EngineeringOrchestrator does not yet own every advanced optimization-selection configuration used by the Streamlit product
- Configured weighted and Pareto product workflows therefore coordinate the existing public backend services directly
- This does not change deterministic engineering results, but creates duplicated application-level orchestration
 
Complete orchestration parity is deferred as non-blocking architectural cleanup after V2.0.0 freeze.
 
---

# 16. Streamlit Application
 
The V2 Streamlit application is feature complete for the current V2.0.0 release candidate.
 
Current capabilities include:
 
- Havells branding
- Thermal Design Agent title
- Engineering Design & Analysis subtitle
- Engineering workflow sidebar
- Natural-language requirement input
- Requirement review
- Interactive clarification
- Forced-convection execution
- Natural-convection execution
- Natural-convection orientation configuration
- Natural-convection thermal-radiation configuration
- Convective, radiative, and effective HTC presentation
- Minimum-thermal-resistance optimization
- Weighted multi-objective optimization
- Pareto-front exploration with explicit engineer final selection
- Engineering design result
- Design-space evaluation
- Forced-airflow section
- Engineering review
- Engineering recommendations
- Validation requirements
- STEP download
- HTML engineering-report download
 
The Streamlit application uses the shared deterministic backend services throughout the engineering workflow.
 
Standard orchestrated workflows use `EngineeringOrchestrator`. Configured weighted and Pareto workflows currently coordinate the same public backend services at the Streamlit application layer because the canonical orchestrator does not yet expose the complete advanced selection configuration.
 
This is recorded as non-blocking V2 architectural technical debt.
 
Known non-blocking cosmetic issues intentionally deferred:
 
- Sidebar collapse/expand arrow visibility
- Unnecessary horizontal scrollbar in the main interface
 
These are not V2 release blockers.
 
Do not reopen V2 UI styling work unless explicitly required.
 
---
 
# 17. V2 Release-Hardening Fixes
 
Two release blockers were identified during the V2 pre-freeze audit and resolved.
 
## 17.1 Requirement Constraint Preservation
 
Azure OpenAI, Gemini, and Mock Provider extraction now preserve supported V2 engineering constraints including:
 
- Maximum base temperature
- Maximum pressure drop
- Maximum pumping power
- Allowed materials
 
An explicit supported engineering constraint is no longer silently lost at the natural-language extraction boundary.
 
Explicit material restrictions incompatible with the current Aluminium 6063-T5 design path are rejected rather than silently ignored.
 
## 17.2 Recommendation Failure Resilience
 
Engineering-recommendation AI failure no longer destroys an otherwise valid deterministic application result.
 
When fallback is enabled, recommendation synthesis failure results in an empty recommendation collection while preserving the valid engineering workflow.
 
---
 
# 18. V2 Regression Status
 
The original V2 regression baseline was completed on 12 August 2026.
 
The release was subsequently reopened before final freeze to add:
 
- Natural-convection orientation support
- Horizontal fins-up modelling
- Horizontal fins-down modelling
- Natural-convection thermal radiation
- Convective/radiative/effective HTC traceability
- Requirement-extraction support for the new configuration
- Streamlit configuration and presentation
- Engineering-intelligence integration
- Engineering-report integration
 
The orientation/radiation extension has passed focused regression covering:
 
- Natural-convection requirement specification
- Requirement parsing and validation
- Requirement extraction
- Vertical natural-convection regression preservation
- Horizontal natural-convection correlations
- Horizontal orientation integration
- Thermal-radiation physics
- Iterative convection/radiation coupling
- Natural-convection optimizer integration
- Candidate/result radiation-state propagation
- Engineering intelligence
- Engineering reporting
- Streamlit vertical/no-radiation scenario
- Streamlit vertical/radiation scenario
- Streamlit horizontal fins-up/down scenarios
- Forced-convection regression preservation
- Fan-coupled regression preservation
 
A complete final V2.0.0 regression sweep will be run after release-cleanup work is finished.
 
The release must not be marked frozen until that final regression passes.
 
---
 
# 19. Forced-Convection Regression Reference
 
Final forced-convection regression approximately produced:
 
- Total candidates evaluated: 15,870
- Feasible candidates: 5,496
- Rejected candidates: 10,374
- Selected base thickness: 3.0 mm
- Selected fin height: 8.0 mm
- Selected fin thickness: 0.8 mm
- Selected fin spacing: 1.6 mm
- Selected fin count: 21
- Channel velocity: 7.8125 m/s
- Pressure drop: 86.1899 Pa
- Pumping power: 0.17238 W
- Thermal resistance: 0.680824 °C/W
- Estimated base temperature: 142.336 °C
 
These values are regression references, not hard-coded application outputs.
 
---
 
# 20. Natural-Convection Vertical / Radiation-Off Regression Reference
 
Final natural-convection regression approximately produced:
 
- Feasible candidates: 5,496
- Selected base thickness: 3.0 mm
- Selected fin height: 8.0 mm
- Selected fin thickness: 0.8 mm
- Selected fin spacing: 1.6 mm
- Selected fin count: 21
- Convective heat-transfer coefficient: 13.8418 W/m²K
- Radiative heat-transfer coefficient: 0 W/m²K
- Effective heat-transfer coefficient: 13.8418 W/m²K
- Thermal resistance: 3.60029 K/W
- Estimated base temperature: 102.006 °C
 
These values are regression references for the legacy-compatible vertical, radiation-disabled natural-convection path. They are not hard-coded application outputs.
 
Different orientations and radiation configurations intentionally produce different engineering results and may select different optimal geometries.
 
---
 
# 21. Development Working Rules
 
For future development:
 
- Inspect the latest flattened codebase snapshot before giving code changes
- Treat that snapshot as the code source of truth
- Give exact file/find/replace instructions
- Do not modify project files directly unless explicitly requested
- Make incremental architectural changes
- Run focused regressions after changes
- Preserve deterministic engineering authority
- Keep AI outputs grounded in deterministic evidence
- Preserve forced-convection behaviour when extending the application
- Do not casually redesign working architecture
- Avoid unrelated changes
- Maintain Azure OpenAI and Gemini provider portability
- Regenerate the flattened snapshot when accumulated changes become difficult to track
- Update PROJECT_STATE after major milestones
 
The latest audited flattened snapshot before final release cleanup was:
 
`entire_codebase 16.txt`
 
That snapshot includes the natural-convection orientation and radiation extension.
 
Further release-cleanup edits are being made after snapshot 16. A fresh flattened snapshot must therefore be generated after the final regression and before V2.0.0 is declared frozen.
 
---
 
# 22. Post-V2 Opportunities
 
Potential V2.x / V3 development areas include:
 
- Intermediate inclined natural-convection orientations
- Higher-fidelity natural-convection correlation validation
- Detailed surface-to-surface and inter-fin radiation modelling
- Independent radiative-surroundings temperature modelling
- Forced-convection radiation coupling, if justified by future use cases 
- Additional heat-sink topologies
- Experimental thermal-model calibration
- CFD/OpenFOAM validation
- Expanded material selection
- Expanded fan selection
- Fan-speed modelling
- Richer supplier/manufacturing capability databases
- Engineering design history
- Engineering database integration
- Enterprise deployment
- User authentication
- Broader engineering-agent workflows
 
These opportunities are explicitly outside the V2.0.0 release boundary.
 
---
 
# 23. Current Release State
 
**Thermal Design Agent V2.0.0**
 
**Status: FROZEN AFTER SUCCESSFUL FINAL V2.0.0 REGRESSION**
 
V2.0.0 feature development is complete.
 
The final release validation successfully covered:
 
- Complete Python compilation
- All `tests/test_*.py` regression modules
- All root `test_*.py` regression modules
- Forced-convection engineering workflows
- Fan-coupled airflow workflows
- Natural-convection vertical orientation
- Natural-convection horizontal fins-up orientation
- Natural-convection horizontal fins-down orientation
- Natural-convection thermal-radiation coupling
- Requirement extraction and clarification
- Material, mass, cost, and currency handling
- Minimum-thermal-resistance optimization
- Weighted multi-objective optimization
- Pareto-front optimization and engineer selection
- Engineering intelligence
- Deterministic engineering review
- Grounded AI review and recommendations
- Azure OpenAI live integration
- Engineering report generation
- Streamlit product workflows
- Geometry planning
- CAD generation
- STEP export
 
No known functional V2.0.0 release blocker remains.
 
V2.0.0 is therefore frozen as the stable project baseline on **25 August 2026**.
 
No additional engineering capability should be added directly to the frozen V2.0.0 baseline.
 
Further development should proceed as a subsequent V2.x or V3 development line.
 
Additional internal safety, code-quality, and engineering-validation reviews may still be performed against the frozen baseline. Any issue identified by those reviews should be documented and handled as a controlled maintenance change rather than silently modifying the frozen release.