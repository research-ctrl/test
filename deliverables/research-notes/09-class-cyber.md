# Classification (Bureau Veritas), cyber resilience (IACS UR E26/E27) and machinery automation / shaft monitoring
Verification date: 2026-11-24

**How these findings were checked.** Direct page fetches of `marine-offshore.bureauveritas.com`, `rulesexplorer-docs.bureauveritas.com` and `iacs.org.uk` failed: the hosts are not on this session's network allow-list, and they need to be allowed before any page can be opened directly. Every source below was therefore **seen in web-search results (title, URL and the search engine's extract of the text), not opened in full**. Some statements come from the agent's own professional knowledge and could not be re-checked this session. Those are marked "agent knowledge – not re-verified" and carry UNVERIFIED or CONDITIONAL status. The shared web-search budget ran out before the last two queries (the IACS UR Z21 survey-method detail and the BV survey regime / in-water survey notation). Those topics are covered from knowledge and marked as such. Abbreviations: GT = gross tonnage; CBS = computer-based system; UR = IACS Unified Requirement; UMS = unattended machinery space; RO = recognised organisation; TA = type approval; OT = operational technology.

## A. Claim verification records

### CLS-01
- claim: Dossier §11: "Class and cyber: BV NR467/NR600 applicability". Dossier §1: Lourdes is BV-classed, 770 GT, and earlier and future designs are 390 GT and 490 GT.
- status: CORRECTED
- finding: The dossier leaves out the third rule set that matters, **NR566** (ships under 500 GT). Which BV rule set applies depends on two separate tests: ship **length**, which decides the hull-structure rules, and **GT**, which decides the arrangement, stability and systems rules. The likely mapping is as follows. **770 GT**: NR467 Part A (classification and surveys), Part B (arrangement and stability), Part C (machinery, electrical, automation, fire protection), Part D (service-notation requirements, e.g. ro-ro) and Part F (any additional notations chosen). Hull scantlings come from **NR600**, because the rule length is well under 65 m. **390 GT and 490 GT**: NR566 for arrangement, stability, hull integrity, machinery, electrical and fire safety; NR600 for hull structure; NR467 Part A for classification and surveys. NR600 applies to all three designs because the hull is 51 m long. The change at 500 GT applies to the systems rules, not the structure rules.
- regulation: BV NR467 (Rules for the Classification of Steel Ships); BV NR600 (Hull structure and arrangement for the classification of cargo ships less than 65 m and non-cargo ships less than 90 m); BV NR566 (Hull arrangement, stability and systems for ships less than 500 GT).
- sources: [BV NR600 product page (search result)](https://marine-offshore.bureauveritas.com/hull-structure-and-arrangement-classification-cargo-ships-less-65-m-and-non-cargo-ships-less-90-m); [BV NR566 product page (search result)](https://marine-offshore.bureauveritas.com/nr566-hull-arrangement-stability-and-systems-ships-less-500-gt); [BV NR467 page (search result)](https://marine-offshore.bureauveritas.com/nr467-rules-classification-steel-ships)
- effective: The rule edition in force at the date of the contract for construction applies. This is the IACS PR 29 contract-date principle (agent knowledge – not re-verified). See CLS-02 to CLS-04 for editions.
- applicability: Steel cargo ships. NR600 covers cargo ships < 65 m and non-cargo ships < 90 m, in steel, aluminium or composite. NR566 covers ships < 500 GT, any material, but **excludes hull strength**.
- implication: For 390 and 490 GT, NR566 replaces the NR467 Part B and C requirements. NR566 is generally lighter on systems, though the size of the saving was not verified this session. The **490 GT design has a hidden risk**. If final tonnage measurement comes out at 500 GT or above, the rule basis switches to NR467 Parts B and C, and E26/E27 become mandatory (CYB-01) **after the design has been fixed**. Keep a tonnage margin (agent judgement: design target ≤ 480 GT) and have the tonnage measured early.
- uncertainty: For a 770 GT ship under 65 m, NR600 is likely the only structural route, but whether NR467 Part B structural chapters may be used instead needs BV's written answer. The text of NR566's scope chapter (e.g. any length or service limits) was not read.

### CLS-02
- claim: NEW: BV NR600 title, current edition and scope.
- status: CONFIRMED
- finding: Exact title: "Hull structure and arrangement for the classification of cargo ships less than 65 m and non-cargo ships less than 90 m". It sets hull scantlings and structural arrangement for steel, aluminium and composite hulls. **Current edition: March 2026 (R08).** Earlier editions: October 2024 (R07, in force 1 Oct 2024), January 2024 (R06) and November 2022 (R05). The March 2026 change list includes an updated effective breadth of attached plating for secondary stiffeners (Ch 4 Sec 4). No 2025 edition was found.
- regulation: BV NR600 R08, March 2026.
- sources: [NR600 March 2026 PDF (search result)](https://rulesexplorer-docs.bureauveritas.com/documents/nr600/mar2026/600-NR_2026-03.pdf); [NR600 Main Changes March 2026 (search result)](https://rulesexplorer-docs.bureauveritas.com/documents/nr600/mar2026/600-NR_MainChanges_2026-03.pdf); [NR600 Oct 2024 PDF (search result)](https://rulesexplorer-docs.bureauveritas.com/documents/nr600/oct2024/600-NR_2024-10.pdf)
- effective: R08 is presumed in force from 1 March 2026 (BV editions normally enter into force on the 1st of the edition month). Not read directly.
- applicability: The 51 m hull qualifies for all three GT variants.
- implication: Hull structure has one rule basis for 390, 490 and 770 GT. The main structural cost drivers are the navigation notation (CLS-06), wheel and axle loads on the vehicle deck, the ramp, and beaching loads, not GT.
- uncertainty: How NR600 treats beaching and grounding loads, and the exact navigation coefficients, were not read (domain blocked).

### CLS-03
- claim: NEW: BV NR566 title, edition and scope.
- status: CONFIRMED (title and scope); CONDITIONAL (edition)
- finding: Exact title: "Hull arrangement, stability and systems for ships less than 500 GT". It covers general arrangement, stability, hull integrity, machinery, electrical systems and fire safety, but **not hull strength**, which comes from NR600 or NR467. The BV rules listing (as reported in search results) shows a **November 2024** edition. A third-party copy is the older July 2022 edition (R03). BV's crew transfer vessel rules (NR490) cross-refer to NR566 for vessels under 500 GT.
- regulation: BV NR566 (Nov 2024 edition per BV listing).
- sources: [BV NR566 page (search result)](https://marine-offshore.bureauveritas.com/nr566-hull-arrangement-stability-and-systems-ships-less-500-gt); [BV rules index (search result)](https://marine-offshore.bureauveritas.com/rules-classification-rule-notes-and-guidance-notes); [NR490 July 2025 (search result)](https://rulesexplorer-docs.bureauveritas.com/documents/nr490/jul2025/490-NR_2025-07.pdf)
- effective: Nov 2024 edition (presumed in force 1 Nov 2024; not read).
- applicability: Ships < 500 GT.
- implication: This is the rule set for the 390 and 490 GT variants. For the 770 GT ship, NR467 Parts B and C apply instead.
- uncertainty: Confirm with BV whether a 2025 or 2026 NR566 edition exists, and whether NR566 is mandatory or optional for a < 500 GT ro-ro ship on international voyages.

### CLS-04
- claim: NEW: BV NR467 current editions (2025–2026).
- status: CONFIRMED
- finding: NR467 "Rules for the Classification of Steel Ships" has editions dated **July 2025**, **January 2026** (in force 1 January 2026) and **July 2026** (main-changes document published). BV's index lists **Part F (Additional Class Notations) as R20, January 2026**, and Part A as R25, January 2026. Different Parts are reissued in different months. January 2026 changes include: new requirements for emergency internal communication equipment (Ch 2 Sec 3 [3.6.4]); reliability of single essential propulsion components (IACS UI SC 305, Ch 2 Sec 14); and a reference to NI692 (guidelines for machine-learning systems) in the computer-based-systems section (Ch 3 Sec 3). July 2026 changes include: SMART notation groups; shaft-bracket design load (centrifugal force Fc, Ch 12); MSC.1/Circ.1683; IGC amendments (MSC.566(109)); IACS UI SC 304; and container allowable compression force under the LASHING notation.
- regulation: BV NR467, editions Jul 2025 / Jan 2026 / Jul 2026.
- sources: [NR467 Main Changes Jul 2026 (search result)](https://rulesexplorer-docs.bureauveritas.com/documents/nr467/jul2026/467-NR_MainChanges_2026-07.pdf); [NR467 Main Changes Jan 2026 (search result)](https://rulesexplorer-docs.bureauveritas.com/documents/nr467/jan2026/467-NR_MainChanges_2026-01.pdf); [NR467 Main Changes Jul 2025 (search result)](https://rulesexplorer-docs.bureauveritas.com/documents/nr467/jul2025/467-NR_MainChanges_2025-07.pdf)
- effective: 1 Jan 2026 and 1 Jul 2026 editions. The edition in force at the contract date applies.
- applicability: All BV steel ships. For < 500 GT ships, NR566 takes the place of large parts of Parts B and C.
- implication: A 2026 contract will fall under the January 2026 or July 2026 edition, depending on the signing date. The ship specification should state the edition.
- uncertainty: Whether UI SC 305 (single-component reliability) affects a twin-engine, twin-shaft LCT. Probably not, because propulsion is redundant (agent judgement).

### CLS-05
- claim: NEW: BV main class symbol, service notations for an LCT/RoRo, and whether "landing craft" or "beaching" notations exist.
- status: UNVERIFIED
- finding: From agent knowledge (not re-verified): a BV newbuilding built under BV survey is assigned **I ✠HULL ✠MACH**. "I" is the main class symbol; ✠ (Maltese cross) means construction under BV survey. A navigation notation is added (CLS-06), plus a service notation. Candidates are "**ro-ro cargo ship**" (vehicles loaded and unloaded by ramp) or "**general cargo ship**". The service notation decides which NR467 Part D chapter applies: ro-ro spaces, ramp and door indicators, vehicle-deck loads, etc. Search did not establish whether BV has a dedicated "landing craft" service notation or a "beaching" additional notation.
- regulation: BV NR467 Part A Ch 1 Sec 2 (class symbols and notations) – agent knowledge, section number unverified.
- sources: none opened. Searched for BV navigation and service notation text; the results did not return BV rule text.
- effective: n/a
- applicability: All BV ships.
- implication: The service notation drives scope. "Ro-ro cargo ship" pulls in ro-ro-specific structural, fire (ro-ro space) and door/ramp requirements. Using LCT beaching as a design load needs explicit BV agreement (bottom structure, ramp, propeller and rudder protection).
- uncertainty: High. Ask BV in writing which service notation(s) it will assign to a 24 TEU bow-ramp LCT that carries vehicles and containers, and whether beaching is handled by a notation, a design-basis statement or a memo in the class file.

### CLS-06
- claim: NEW: BV navigation notations (unrestricted / summer zone / tropical zone / coastal area / sheltered area), the coastal-area limit, and the effect on scantlings and on an India→Europe delivery voyage.
- status: UNVERIFIED (definition); CONDITIONAL (implication)
- finding: Agent knowledge, not re-verified: BV defines "**coastal area**" as operation within **20 nautical miles from the shore**, with a maximum sailing time of **six hours** from a port of refuge or safe sheltered anchorage. "**Sheltered area**" covers harbours, estuaries, roadsteads, bays and lagoons where the wind does not exceed Beaufort 6. The navigation notation feeds into the design wave loads in NR600 and NR467 through a navigation coefficient, so a restricted notation gives lighter scantlings. A coastal-area ship cannot, as classed, make an ocean delivery voyage from India to Europe (Arabian Sea, Gulf of Aden or Cape route, Mediterranean). That needs one of two things: (a) designing to **unrestricted navigation**, or (b) a BV voyage-specific assessment, possibly with temporary strengthening, weather routing and seasonal limits, together with a flag single-voyage permit. A search for the BV wording returned only a French national rule (fourth category: within 20 miles of land), which is a different instrument.
- regulation: BV NR467 Part A Ch 1 Sec 2 (navigation notations); NR600 navigation coefficients. Exact paragraph numbers unverified.
- sources: [SHOM / French navigation categories (search result – NOT BV, context only)](https://diffusion.shom.fr/downloadable/download/sample/sample_id/91)
- effective: n/a
- applicability: All designs.
- implication: The decision between unrestricted and restricted navigation is one of the largest structural cost levers, and it is independent of GT. If the business case includes European trading, design for unrestricted navigation. "Coastal area" also limits resale and charter value.
- uncertainty: High. Obtain BV's current definitions in writing, and ask whether a coastal-area ship can be given a one-off delivery-voyage approval and under what conditions.

### CLS-07
- claim: NEW: IRS (Indian Register of Shipping) dual class and the IRS "River-Sea Vessel" notation.
- status: UNVERIFIED
- finding: Agent knowledge, not re-verified: IRS is an IACS member and is the main RO for the Indian flag. Indian-flag vessels are often IRS-classed or BV+IRS dual-classed. India's Directorate General of Shipping (DGS) has a River-Sea Vessel (RSV) framework, and IRS issues class notations for river-sea service in Indian coastal waters. This is relevant only if a variant is meant for Indian coastal or inland-to-sea trade, not for Malta-flag foreign-going service. Not researched further because the search budget ran out.
- regulation: DGS RSV notification(s) and IRS rules (unverified references).
- sources: none opened this session.
- effective: unverified
- applicability: Indian-flag coastal and river-sea service only.
- implication: Dual class adds fees and two sets of plan-approval comments. It helps where Indian charterers or the DGS want IRS. For a Malta-flag ship, BV alone is normal.
- uncertainty: Hand off to the India / flag agent. Verify the current RSV rules and IRS notation names.

### CLS-08
- claim: NEW: BV statutory delegation from Malta and other flags (RO status).
- status: UNVERIFIED (this session)
- finding: Agent knowledge, not re-verified: BV is an EU-recognised organisation under Regulation (EC) No 391/2009 and is authorised by Transport Malta and most open registries to carry out statutory surveys and issue convention certificates on the flag's behalf. Examples are Load Line, IOPP/IAPP and, for ≥ 500 GT, Safety Construction / Equipment / Radio, plus ISM/ISPS where delegated. The scope of delegation differs by flag and certificate and is set out in each flag–RO agreement.
- regulation: Reg. (EC) 391/2009; IMO RO Code (MSC.349(92)/MEPC.237(65)); Transport Malta RO authorisations.
- sources: none opened (search budget exhausted).
- effective: n/a
- applicability: All designs.
- implication: With the same RO for class and statutory work, one surveyor team covers both, which cuts cost and visits. Confirm that BV holds the Malta authorisation for every certificate needed (including the Malta NCV Code certificates for < 500 GT).
- uncertainty: Obtain written confirmation from Transport Malta and BV of the delegation scope for each design.

### CLS-09
- claim: Dossier §5/§8: "BV approvals" link to BV Approval Explorer; "a class/type approval from one society does not establish BV acceptance".
- status: CONDITIONAL
- finding: BV Approval Explorer (approvalexplorer.bureauveritas.com) is BV's public database of type-approval certificates. It could not be reached this session (BV domains blocked). Recommended use: search by manufacturer and model; check certificate validity, the applicable rules (NR467 / NR566 / E27), environmental category, conditions and limitations, and whether **IACS UR E27 Rev.1** cyber capability is in the scope. Search confirmed that BV issues E27-based type approvals; one example is a BV type approval for Ascenz Marorka covering NR467, NR659 and UR E27 Rev.1 (CYB-06). The dossier's point is correct: an approval from another IACS society is not automatically BV acceptance. Under IACS procedures BV may accept or recognise it, but this must be confirmed case by case.
- regulation: BV NR320 (type approval scheme) – agent knowledge, unverified; IACS UR E27 Rev.1.
- sources: [BV – Ascenz Marorka cyber type approval (search result)](https://marine-offshore.bureauveritas.com/newsroom/ascenz-marorka-receives-type-approval-cybersecurity-its-digital-solutions-0)
- effective: n/a
- applicability: All CBS and equipment that needs class approval.
- implication: For a ≥ 500 GT ship, add "E27 evidence or BV-accepted exclusion" as a procurement line item for every in-scope CBS (CYB-06).
- uncertainty: Approval Explorer must be checked by the client directly (the domain is blocked here).

### CLS-10
- claim: NEW: BV class survey regime (annual, intermediate, class renewal, bottom / in-water survey, tailshaft).
- status: UNVERIFIED (this session; agent knowledge consistent with IACS URs)
- finding: Standard IACS and BV regime (agent knowledge): **annual survey** within ±3 months of each anniversary date; **intermediate survey** in place of the 2nd or 3rd annual; **class renewal** every **5 years**, which can be done as a continuous survey for machinery. **Bottom survey**: two examinations of the outside of the bottom in each 5-year period, one at class renewal, with **no more than 36 months** between them (IACS UR Z3). An **in-water survey** may replace the intermediate docking where the ship holds BV's in-water-survey notation (believed "INWATERSURVEY"; name unverified). **Propeller shaft survey**: normally every 5 years (UR Z21; see AUT-06). Search confirmed the 60-month tailshaft interval via a class instruction based on Z21.
- regulation: IACS UR Z3, Z7, Z21; BV NR467 Part A Ch 2–3 (section numbers unverified).
- sources: [ICS Class propeller shaft survey instruction based on UR Z21 (search result)](https://surveyors.icsclass.org/wp-content/uploads/2022/07/PO02-TI04-Propeller-shaft-survey-Ver.-01-05-2020.pdf)
- effective: Current
- applicability: All classed ships. For ≥ 500 GT SOLAS ships, statutory surveys are harmonised with class.
- implication: An in-water-survey notation can save one drydocking every 5 years, but a **beaching LCT is likely to need dry inspection anyway**: bottom, ramp-toe and propeller/rudder damage. Ask BV whether beaching affects bottom-survey eligibility.
- uncertainty: Confirm the in-water-survey notation name, its requirements (marking, hull coatings, shaft clearance measurement), and any beaching-related survey conditions.

### CLS-11
- claim: NEW: class fees, plan-approval scope, and how a sub-500 GT design changes class scope.
- status: UNVERIFIED (fees not public)
- finding: No public BV fee scale was found; BV quotes newbuilding class fees per project. The figures below are **budget estimates (agent judgement, low confidence, ±50%)**. New-construction class (plan approval + construction survey + class certificate) for a ~50 m steel LCT built in India: roughly **EUR 80k–200k**. Statutory delegated surveys, E26 work and travel/attendance may be extra. Annual class maintenance: roughly **EUR 5k–15k per year** plus surveyor attendance. Typical plan-approval set: GA, capacity plan, midship section and scantling plans, shell expansion, bulkheads, double bottom, vehicle-deck wheel-load calculations, bow ramp and hinge/locking structure, beaching/bottom reinforcement, rudder and sternframe, stability booklet, machinery arrangement, shafting, TVC and propeller, steering gear, piping diagrams (bilge, ballast, fuel, cooling, fire), electrical load balance, one-line diagram, short-circuit calculation, switchboards, emergency power, fire detection and structural fire protection, and (≥ 500 GT, international) the E26 document set. For < 500 GT: NR566 replaces NR467 Parts B and C, E26/E27 are guidance only, and ISM is not required by SOLAS. Class still requires full hull/machinery/electrical/stability plan approval, construction survey, type-approved equipment where the rules require it, and the IACS UR E22 computer-based-system rules where NR566 invokes them (the E22 point is unverified).
- regulation: BV NR467 / NR566 / NR600; IACS UR E22 (unverified for < 500 GT).
- sources: none (no public fee source located). Searched BV pages; BV domains blocked.
- effective: n/a
- applicability: All designs.
- implication: Going below 500 GT does **not** remove class plan approval. It mainly removes E26/E27 (CYB-02), SOLAS II-1 Part E for UMS (AUT-02) and SOLAS-level systems requirements. The class fee itself is unlikely to change much between 490 and 770 GT (agent judgement).
- uncertainty: Obtain written fee quotations from BV, and from IRS for comparison, for each variant, separating class, statutory and E26 work.

### CYB-01
- claim: Dossier §5: "IACS E26/E27: prior research identifies international cargo ships ≥500 GT contracted from 1 July 2024." Dossier §2: "500 GT … IACS E26/E27 scope".
- status: CONFIRMED (with refinement)
- finding: **UR E26 Rev.1 (Nov 2023)** and **UR E27 Rev.1 (Sep 2023)** are to be applied by all IACS societies to ships **contracted for construction on or after 1 July 2024**. The original April 2022 versions, with their 1 January 2024 date, were withdrawn before entry into force. Mandatory scope (E26 §1.3.1): passenger ships, including passenger high-speed craft, on international voyages (**any size**); **cargo ships of 500 GT and upwards engaged in international voyages**; high-speed craft ≥ 500 GT on international voyages; mobile offshore drilling units ≥ 500 GT; and self-propelled mobile offshore units engaged in construction. The last item is agent knowledge; the ABS summary confirms cargo ships ≥ 500 GT international and MODUs ≥ 500 GT. **The 770 GT Lourdes, contracted in 2026 and trading internationally (delivery voyage included), is in mandatory scope.**
- regulation: IACS UR E26 Rev.1 (Nov 2023) §1.3; IACS UR E27 Rev.1 (Sep 2023).
- sources: [IACS UR E26 Rev.1 PDF (search result)](https://iacs.s3.af-south-1.amazonaws.com/wp-content/uploads/2022/02/04140503/UR-E26-Rev.1-Nov-2023-CR.pdf); [ClassNK-hosted copy of E26 Rev.1 (search result)](https://www.classnk.or.jp/hp/pdf/info_service/iacs_ur_and_ui/ur_e26_rev.1_nov_2023_cr.pdf); [IACS UR E27 Rev.1 PDF (search result)](https://iacs.s3.af-south-1.amazonaws.com/wp-content/uploads/2022/05/29103854/UR-E27-Rev.1-Sep-2023-UL.pdf); [ABS Regulatory News E26/E27 (search result)](https://ww2.eagle.org/content/dam/eagle/regulatory-news/2023/ABS%20Regulatory%20News%20-%20IACS%20UR%20E26%20and%20E27.pdf)
- effective: Contract for construction on or after 1 July 2024.
- applicability: ≥ 500 GT cargo ships on **international voyages**. A ≥ 500 GT ship confined to domestic voyages falls outside mandatory scope, though BV's rules should be checked for its treatment of such ships. Existing ships are not retroactively covered.
- implication: 770 GT: mandatory for class. 490 and 390 GT: not mandatory (CYB-02).
- uncertainty: Low. Read E26 §1.3 in full once the IACS domain is allowed.

### CYB-02
- claim: NEW: E26/E27 treatment of ships below 500 GT.
- status: CONFIRMED
- finding: E26 Rev.1 and E27 Rev.1 list **cargo ships of less than 500 GT** among the types for which the UR "**may be used as non-mandatory guidance**". The same list includes ships of war and troop ships, pleasure yachts not engaged in trade, fishing vessels and site-specific offshore installations (FPSO/FSU). The Polish Register's implementing publication reproduces the same list.
- regulation: IACS UR E26 Rev.1 §1.3; UR E27 Rev.1 (applicability as E26); PRS Publication P125P.
- sources: [PRS P125P (search result)](https://prs.pl/wp-content/uploads/2024/06/P125P_en.pdf); [IACS UR E26 Rev.1 (search result)](https://iacs.s3.af-south-1.amazonaws.com/wp-content/uploads/2022/02/04140503/UR-E26-Rev.1-Nov-2023-CR.pdf)
- effective: As CYB-01.
- applicability: < 500 GT cargo ships, whatever their voyage.
- implication: **390 and 490 GT designs: E26/E27 are not mandatory class requirements.** The owner may still choose voluntary BV CYBER notations (CYB-07). Basic cyber hygiene in line with the IMO guidelines (CYB-08) remains good practice. This is a genuine scope difference, not an exemption.
- uncertainty: Whether the Malta NCV Code or another flag imposes any cyber requirement on < 500 GT ships (hand off to the flag agent).

### CYB-03
- claim: NEW: which computer-based systems (CBS) are in E26 scope.
- status: CONFIRMED (core list); UNVERIFIED (navigation and communication wording)
- finding: E26 Rev.1 §1.3.2 covers OT systems that use data to control or monitor physical processes and whose disruption could put ship, people or environment at risk. Listed categories: **propulsion; steering; anchoring and mooring; electrical power generation and distribution; fire detection and extinguishing; bilge and ballast systems and the loading computer; watertight integrity and flooding detection; lighting (e.g. emergency lighting, low-location lighting, navigation lights); and any required safety system** whose disruption may pose risks (e.g. emergency shutdown, cargo safety, gas detection). The scope also covers **IP-based interfaces** from in-scope systems to other systems, and any system connected to OT temporarily or permanently, e.g. for maintenance. Agent knowledge, not confirmed by search: the list also includes **navigational systems required by statutory regulations** and **internal/external communication systems required by class and statutory rules**. Firewalls and network devices joining in-scope systems are themselves in scope. Class notations such as ABS CR can add more systems.
- regulation: IACS UR E26 Rev.1 §1.3.2.
- sources: [IACS UR E26 Rev.1 (search result)](https://iacs.s3.af-south-1.amazonaws.com/wp-content/uploads/2022/02/04140503/UR-E26-Rev.1-Nov-2023-CR.pdf); [DNV – cyber security for suppliers (search result)](https://www.dnv.com/maritime/insights/topics/maritime-cyber-security/suppliers/); [Pen Test Partners E26/E27 guidance (secondary, search result)](https://www.pentestpartners.com/security-blog/iacs-ur-e26-and-e27-guidance/)
- effective: As CYB-01.
- applicability: CBS on in-scope ships.
- implication: Systems on the 770 GT LCT that are probably CBS (agent judgement): electronic engine and vessel control (Volvo Penta D13 electronic management and controls; confirm with Volvo); electro-hydraulic steering control and autopilot; generator controllers and any power management; an addressable fire-detection panel; bilge level and machinery alarm panel; ballast control if PLC-based; a loading computer if fitted; ramp/door and flooding indication; navigation-light controller; radar, AIS, GNSS, echo sounder, BNWAS and heading sensor; GMDSS and internal communications. Each needs E27 evidence from its supplier **or** a BV-accepted exclusion (CYB-04).
- uncertainty: Confirm the exact navigation and communication wording, and BV's position on MED-approved navigation and radio equipment (e.g. certified to IEC 61162-460 or IEC 63154). Not verified.

### CYB-04
- claim: Dossier §5: "Standalone/analogue systems may reduce scope, not automatically remove applicability." Dossier §11: "E26/E27 impact of standalone systems".
- status: CONDITIONAL (dossier is correct at ship level; refined at system level)
- finding: Three levels apply. (1) **Purely mechanical, hydraulic or analogue systems are not CBS**, so E26 does not reach them. (2) An individual CBS can be **excluded entirely** from E26 requirements, not just reduced in scope. This needs a documented "**risk assessment for exclusion of CBS**" (E26 Rev.1 section 6) that the class society accepts. Class guidance gives the criteria: the CBS is **not an integrated control system** serving several ship functions; it is **isolated, with no IP-network connections**; it has **no accessible physical interface ports** (unused ports blocked or logically disabled); and it is installed in a **physically access-controlled area**. ABS's FAQ says a fully independent CBS with no internet, no physical interfaces (USB/CD) and no external links "is not required to comply" with E26/E27. ClassNK and KR say the exclusion must be justified and approved; a blog warns that air-gapping is not automatic. (3) **The ship stays in E26 scope** as long as any in-scope CBS remains. The yard still produces the vessel-level documents and BV still carries out the commissioning test.
- regulation: IACS UR E26 Rev.1 §6 (risk assessment for exclusion); ClassNK Rules Part X Ch 5; KR cyber resilience guide.
- sources: [ClassNK explanation of E26 Rev.1 (search result)](https://www.classnk.com/hp/pdf/activities/cybersecurity/e_003.pdf); [KR cyber resilience approval & survey guide (search result)](https://www.krs.co.kr/TECHNICAL_FILE/Cyber%20Resilience%20Approval%20and%20Survey%20Guide%20for%20Ship%20Automation%20Systems_Rev0.0(0).pdf); [ABS UR E27 FAQ (search result)](https://ww2.eagle.org/en/Products-and-Services/vendor-certification/abs-cybersafety-for-resilience/faq-cyber-resilience-program.html)
- effective: As CYB-01.
- applicability: In-scope ships (770 GT).
- implication: This is the main legitimate way to reduce the burden. Keep each system stand-alone. Avoid Ethernet links between the bridge and machinery. Lock away diagnostic and USB ports. Place controllers in locked, access-controlled spaces. Avoid permanent remote-monitoring or telematics links to OT. Every excluded CBS still needs its own exclusion risk assessment, so the paperwork does not disappear; it gets simpler.
- uncertainty: Ask BV in writing: (a) whether serial (NMEA 0183) or CAN-bus links count as "IP-network connections" for exclusion; (b) whether a locked-but-present service port meets "no accessible physical interface"; (c) how BV treats MED navigation and radio equipment.

### CYB-05
- claim: NEW: E26 documentation deliverables.
- status: CONFIRMED (secondary sources)
- finding: Design and construction (systems integrator, normally the shipyard): **zones and conduit diagram; vessel asset inventory; cyber security design description; risk assessments for any excluded CBS; descriptions of any compensating countermeasures; ship cyber resilience test procedure**. Commissioning: the test procedure is carried out in front of the class surveyor. Operation (owner): **ship cyber security and resilience programme**, an asset inventory kept up to date, and verification at annual and renewal surveys. Class societies label the deliverables slightly differently. Projects report several rounds of class comments on the zones/conduit diagram and design description.
- regulation: IACS UR E26 Rev.1 (sections on documentation, construction and commissioning, operation).
- sources: [Viasat/Inmarsat E26/E27 whitepaper, June 2024 (search result)](https://www.viasat.com/content/dam/us-site/maritime/perspectives/documents/MBU_IACS_UR_E26_E27_whitepaper_June_2024.pdf); [Marlink – E26/E27 requirements in practice (search result)](https://marlink.com/news/news-resources/ur-e26-and-e27-requirements-in-practice); [Hellenic Shipping News – preparing for E26/E27 (search result)](https://www.hellenicshippingnews.com/preparing-for-iacs-unified-requirements-e26-and-e27-on-cyber-resilience/)
- effective: As CYB-01.
- applicability: In-scope ships.
- implication: The yard (Bennet & Bernard) is contractually the "systems integrator" unless the contract names someone else. Budget design-office time or a consultant (CYB-11).
- uncertainty: Exact BV submission list. BV's checklist under NR659 / NR467 needs to be obtained.

### CYB-06
- claim: Dossier §8: engine certification should include "E27 where applicable". Dossier §9: ask suppliers for "E27".
- status: CONDITIONAL
- finding: UR E27 Rev.1 places the obligations on the **supplier** of each in-scope CBS. The supplier must show the required security capabilities (largely based on IEC 62443-3-3) and supply documentation per the UR's check sheet: CBS asset inventory, topology, description of security capabilities, test procedure for the security capabilities, security configuration guidelines, secure-development-lifecycle evidence, maintenance and verification plans, information supporting the owner's incident response and recovery, and management-of-change. The detailed list is agent knowledge, consistent with the E27 check sheet referenced by ABS. ABS says E27 does not require a certified testing organisation, and ABS does not require source code. E27 Rev.1 type approvals exist: BV-issued (Ascenz Marorka; an OTESAT-MARITEL product per search), CRS-issued and DNV-issued. DEIF (generator controllers) markets "full IACS UR E27 certification" (vendor claim). For the 770 GT LCT, electronic engine controls, genset controllers and switchboard PMS are "electrical power generation"/"propulsion" CBS, so the dossier's "E27 where applicable" is correct. For 390 and 490 GT, E27 is not mandatory.
- regulation: IACS UR E27 Rev.1 (Sep 2023).
- sources: [IACS UR E27 Rev.1 (search result)](https://iacs.s3.af-south-1.amazonaws.com/wp-content/uploads/2022/05/29103854/UR-E27-Rev.1-Sep-2023-UL.pdf); [ABS UR E27 FAQ (search result)](https://ww2.eagle.org/en/Products-and-Services/vendor-certification/abs-cybersafety-for-resilience/faq-cyber-resilience-program.html); [BV – Ascenz Marorka TA (search result)](https://marine-offshore.bureauveritas.com/newsroom/ascenz-marorka-receives-type-approval-cybersecurity-its-digital-solutions-0); [DEIF cybersecurity page (vendor, search result)](https://www.deif.com/deif-cybersecurity/cybersecurity-you-can-document/)
- effective: As CYB-01.
- applicability: CBS on in-scope ships (770 GT).
- implication: Add to every RFQ for the 770 GT design: "State UR E27 Rev.1 compliance for each CBS (certificate or documentation package), or confirm the unit meets the E26 §6 exclusion criteria." Small-engine and genset vendors (Volvo Penta, AGG/Cummins controller OEM) may not have E27 packages, which would push the system to exclusion or replacement.
- uncertainty: Whether Volvo Penta, AGG, or their controller OEMs (e.g. ComAp, DSE, DEIF) hold E27 evidence for the offered models. Not verified. Ask each.

### CYB-07
- claim: NEW: BV implementation (NR659; CYBER MANAGED / CYBER RESILIENT / CYBER SECURE).
- status: CONFIRMED
- finding: BV **NR659 "Rules on Cyber Security for the Classification of Marine Units"**, edition **R04, July 2024**, contains three notations. **CYBER MANAGED** is risk- and management-based, aimed mainly at existing ships and the owner's SMS. **CYBER RESILIENT** implements UR E26: an **additional service feature CYBER RESILIENT "is assigned, as applicable, to ships contracted for construction on or after 1 July 2024"**, and an **additional class notation CYBER RESILIENT** may be assigned voluntarily to new and existing ships. **CYBER SECURE** is the newbuild notation that goes beyond E26; ships with CYBER SECURE also meet CYBER RESILIENT. NR659 sits within the General Conditions in NR467 Part A. Some older BV material (2023 brochure, owner guide) still says E26 applies to contracts "after 1 January 2024", which is outdated (CYB-01). No 2025 or 2026 NR659 edition was found.
- regulation: BV NR659 R04 (Jul 2024).
- sources: [BV NR659 July 2024 PDF (search result)](https://rulesexplorer-docs.bureauveritas.com/documents/nr659/jul2024/659-NR_2024-07.pdf); [BV NR659 page (search result)](https://marine-offshore.bureauveritas.com/nr659-rules-cyber-security-classification-marine-units); [BV Cyber in marine – newbuilds (search result)](https://marine-offshore.bureauveritas.com/cyber-security-newbuilds); [VARD delivers vessels with cyber notation (search result)](https://www.ajot.com/news/vard-delivers-two-of-the-worlds-first-vessels-with-cyber-notation-following-new-regulations)
- effective: NR659 R04, July 2024. CYBER RESILIENT service feature applies to contracts on or after 1 July 2024.
- applicability: 770 GT: CYBER RESILIENT (E26) is expected in the class record. 390 and 490 GT: optional.
- implication: Do not buy CYBER SECURE for an LCT unless a charterer asks for it; it adds requirements beyond E26. For 390 and 490 GT, adding no cyber notation is legitimate.
- uncertainty: Confirm the current NR659 edition and the exact form in which BV records E26 compliance for a 2026 contract.

### CYB-08
- claim: NEW: IMO Res. MSC.428(98) and MSC-FAL.1/Circ.3 (cyber in the safety management system for ISM ships).
- status: CORRECTED (Rev.2 is no longer the latest guideline)
- finding: **MSC.428(98)** (adopted June 2017; agent knowledge) encourages Administrations to ensure cyber risks are addressed in the ISM safety management system no later than the **first annual verification of the company's Document of Compliance after 1 January 2021**. The verification date is agent knowledge; the resolution text is reproduced in MPA Singapore SC 15/2020 per search. The guidelines have been revised several times. **MSC-FAL.1/Circ.3/Rev.2** (7 June 2022) superseded MSC.1/Circ.1526. **Rev.3** was approved by MSC 108 (May 2024) and FAL 49 (10–14 March 2025), published 4 April 2025, and adds a "Govern" function to Identify / Protect / Detect / Respond / Recover. A **Rev.4** PDF is hosted on the IMO site; one search extract attributes its approval to **MSC 111 (13–22 May 2026)**, another could not confirm this. These are guidelines, not mandatory rules. They apply in practice through ISM (cargo ships ≥ 500 GT under SOLAS IX).
- regulation: IMO Res. MSC.428(98); MSC-FAL.1/Circ.3/Rev.2, Rev.3, Rev.4; SOLAS IX / ISM Code.
- sources: [IMO MSC-FAL.1/Circ.3/Rev.2 (search result)](https://wwwcdn.imo.org/localresources/en/OurWork/Facilitation/FAL%20related%20nonmandatory%20documents/MSC-FAL.1-Circ.3-Rev.2.pdf); [IMO MSC-FAL.1/Circ.3/Rev.3 (search result)](https://wwwcdn.imo.org/localresources/en/OurWork/Facilitation/FAL%20related%20nonmandatory%20documents/MSC-FAL.1-Circ.3-Rev.3.pdf); [IMO MSC-FAL.1/Circ.3/Rev.4 (search result)](https://wwwcdn.imo.org/localresources/en/OurWork/Facilitation/FAL%20related%20nonmandatory%20documents/MSC-FAL.1-Circ.3-Rev.4.pdf); [IMO maritime cyber risk page (search result)](https://www.imo.org/en/OurWork/Security/Pages/Cyber-security.aspx); [MPA SC 15 of 2020 (search result)](https://www.mpa.gov.sg/docs/mpalibraries/circulars-and-notices/shipping-circulars/-sc_no_15_of_2020)
- effective: MSC.428(98) from the first DOC annual verification after 1 Jan 2021. Rev.3 from 2025. Rev.4 from 2026 (conditional).
- applicability: ISM ships. 770 GT: yes. 390 and 490 GT: only if the flag applies ISM or an equivalent SMS.
- implication: The 770 GT operator's SMS must include cyber risk management, which ties in with the E26 "ship cyber security and resilience programme". For < 500 GT, follow the guidelines voluntarily.
- uncertainty: Confirm Rev.4's approval date and changes from the MSC 111 report.

### CYB-09
- claim: NEW: future IMO mandatory cyber instrument (2025–2031).
- status: CONDITIONAL
- finding: At **MSC 110 (18–27 June 2025)** the working group concluded that a **non-mandatory** cybersecurity Code should be developed and invited proposals for a new output to MSC 111. An EU-coordinated proposal for a goal-based, non-mandatory "Maritime Cyber Code" was filed for FAL 50. An industry paper set out a phased plan with a **mandatory instrument only from about 2031**. What MSC 111 (May 2026) decided was **not verified**.
- regulation: MSC 110 report; MSC 110/7 series; MSC 111 papers.
- sources: [IMO MSC 110 meeting summary (search result)](https://www.imo.org/en/mediacentre/meetingsummaries/pages/msc-110th-session.aspx); [IRS MSC 110 report (search result)](https://www.irclass.org/media/7943/msc-110-report.pdf); [LISCR MSC 110 summary (search result)](https://www.liscr.com/marketing/liscr/media/liscr/online%20library/maritime/msc-110-meeting-summary.pdf)
- effective: No mandatory IMO cyber construction rule is in force or adopted (as far as verified).
- applicability: Future.
- implication: No IMO-driven cyber construction requirement is expected for 2026–2028 deliveries. Class (E26) remains the only mandatory newbuild cyber rule, and only for ≥ 500 GT international ships.
- uncertainty: Check the MSC 111 outcome.

### CYB-10
- claim: NEW: any revision of E26/E27 after Rev.1, or IACS unified interpretations (2025–2026).
- status: UNVERIFIED
- finding: Searches for "E26 Rev.2", "E27 Rev.2" and 2025–2026 IACS cyber interpretations returned nothing. All 2024–2026 class and secondary sources still cite Rev.1. IACS was not reachable to check its UR index directly.
- regulation: IACS UR E26 / E27.
- sources: searches only (no confirming source).
- effective: n/a
- applicability: n/a
- implication: Use Rev.1 as the design basis. Ask BV to confirm no later revision or IACS UI applies to the contract date.
- uncertainty: Medium. Check the IACS UR-E index directly.

### CYB-11
- claim: NEW: cost and time of E26 for the 770 GT LCT, and legitimate ways to reduce the burden.
- status: UNVERIFIED (no published cost data; budget estimate only)
- finding: No published per-ship E26 cost was found. **Budget estimate (agent judgement, low confidence)** for a small, simple ship with few CBS: vessel-level documents (zones and conduits, asset inventory, design description, exclusion risk assessments, test procedure) by yard or consultant, about **EUR 15k–50k**; class review and commissioning-test attendance, about **EUR 5k–20k**; supplier E27 packages and any network hardware (firewall, managed switch), **EUR 0–30k**, often built into equipment price. Time: **3–6 months of document cycles**, which can run in parallel with design if started at basic design. Ways to reduce the burden legitimately: (1) choose mechanical, hydraulic or hard-wired controls where the rules allow; (2) keep CBS stand-alone and meet the four exclusion criteria (CYB-04); (3) no permanent remote access to OT; if telematics are needed, put them on a separated IT zone through a single firewall; (4) no IP link between bridge and engine room; (5) buy CBS that already have E27 evidence; (6) one security zone per function, with as few conduits as possible; (7) freeze the equipment list early, because late changes trigger re-review.
- regulation: IACS UR E26 Rev.1 / E27 Rev.1.
- sources: none for costs. A search for published E26 compliance costs found none.
- effective: n/a
- applicability: 770 GT.
- implication: Cost is small relative to ship price but must be planned. The schedule risk comes from late E27 evidence from suppliers.
- uncertainty: Get a BV quotation and at least one consultant quotation.

### CYB-12
- claim: NEW: digital versus analogue equipment, and the trade-off with an integrated bridge or INS.
- status: CONDITIONAL
- finding: E26 does not prohibit integrated systems, and it does not require analogue ones. It scales the work with connectivity. An integrated bridge / INS (one Ethernet network for radar, chart system, conning, autopilot) becomes a single, larger security zone with conduits, firewalls and E27 evidence for every node. Stand-alone units (separate radar, AIS, GNSS, echo sounder linked by serial NMEA, plus a stand-alone autopilot) may each qualify for exclusion, or form small zones. Under 3,000 GT, SOLAS V does not require ECDIS or an INS for these ships (SOLAS V carriage is not my topic; see the navigation agent). So a conventional stand-alone bridge is both compliant and lower in E26 burden. The trade-off is reduced integration, alarm management and situational awareness, and possibly charterer expectations. Integrated alarm and monitoring in the engine room (often needed for UMS) is the same kind of decision (AUT-09).
- regulation: IACS UR E26 Rev.1 §1.3.2 and §6; SOLAS V/19 (thresholds; see navigation agent).
- sources: [ClassNK E26 explanation (search result)](https://www.classnk.com/hp/pdf/activities/cybersecurity/e_003.pdf); [Pen Test Partners on network scope creep (secondary, search result)](https://www.pentestpartners.com/security-blog/iacs-ur-e26-and-e27-guidance/)
- effective: n/a
- applicability: 770 GT mainly. For 390 and 490 GT, a free design choice.
- implication: Recommended for a small LCT: a stand-alone, MED-approved bridge, no ECDIS unless required by the flag or a charterer, and no INS.
- uncertainty: BV's position on whether serial-linked navigation equipment counts as "isolated" (CYB-04 question).

### AUT-01
- claim: Dossier §5: "UMS and shaft monitoring changes need BV assessment."
- status: CONFIRMED (generic). Notation requirements: CONDITIONAL.
- finding: BV's automation notations are **AUT-UMS**, **AUT-CCS**, **AUT-PORT** and **AUT-IMS**. Without any of them, automation must still meet NR467 Part C Ch 3. Part F is R20, January 2026. Agent knowledge, not re-verified: **AUT-UMS** = machinery spaces may be periodically unattended at sea and in port; **AUT-CCS** = machinery operated from a continuously manned centralised control station; **AUT-PORT** = unattended only in port. A BV article associates AUT-IMS with integrated or "smart" machinery monitoring; its exact definition is unverified. Typical AUT-UMS content (agent knowledge): a full machinery alarm and monitoring system with alarm extension to the bridge and engineers' cabins and an engineer-call/dead-man system; fire detection in machinery spaces; bilge high-level alarms; bridge control of propulsion; automatic start of standby pumps; automatic standby generator start and blackout recovery; safety shutdowns. "Assessment by BV" is in practice plan approval against Part F.
- regulation: BV NR467 Part F (automation chapter; section number unverified); NR467 Part C Ch 3.
- sources: [BV NR467 page – Part F R20 Jan 2026 (search result)](https://marine-offshore.bureauveritas.com/nr467-rules-classification-steel-ships); [NR266 copy listing AUT-UMS/CCS/PORT/IMS (unofficial Scribd, search result)](https://www.scribd.com/document/486144449/266-NR-2019-06-pdf); [BV smart assets article (search result)](https://marine-offshore.bureauveritas.com/magazine/new-approach-classification-smart-assets)
- effective: NR467 Part F R20 (Jan 2026).
- applicability: Optional notations, all sizes.
- implication: See AUT-04.
- uncertainty: Obtain BV's Part F automation chapter and NR566's equivalent for < 500 GT.

### AUT-02
- claim: NEW: SOLAS II-1 Part E (periodically unattended machinery spaces) applicability.
- status: UNVERIFIED (this session; agent knowledge)
- finding: SOLAS II-1 Part E, Regulations 46–54, sets extra requirements for periodically unattended machinery spaces: general (46), fire precautions (47), protection against flooding (48), bridge control of propulsion (49), communication (50), alarm system (51), safety systems (52), special requirements for machinery, boiler and electrical installations (53), and passenger ships (54). It applies to SOLAS cargo ships (≥ 500 GT, international) that choose UMS. For < 500 GT ships, UMS is governed by class (AUT-UMS, NR566) and any flag code. BV AUT-UMS is the class route to meeting Part E.
- regulation: SOLAS Ch II-1 Part E, Regs 46–54.
- sources: none opened (search budget exhausted).
- effective: Long-standing (SOLAS 1974 as amended).
- applicability: 770 GT if UMS is chosen. 390 and 490 GT: class and flag only.
- implication: Choosing UMS on the 770 GT ship carries both statutory and class obligations.
- uncertainty: Re-open SOLAS II-1 Part E text.

### AUT-03
- claim: NEW: effect of UMS on safe manning and engineer watchkeeping.
- status: CONDITIONAL
- finding: Agent knowledge, not re-verified: 882 kW total propulsion is **above the 750 kW STCW threshold**. Under STCW Reg. III/3, the chief and second engineer of ships with **750–3,000 kW** propulsion need III/3 certificates. Engineering watch officers or designated duty engineers need III/1. The flag's minimum safe manning document sets the number of engineers. With an attended engine room, a continuous voyage needs a watch rota, normally three watches. With UMS, the engineers can work days with one designated duty engineer on call at night, which may let the flag accept fewer engineering officers. That is the flag's decision, not automatic.
- regulation: STCW Regs III/1, III/3; IMO Res. A.1047(27) (safe manning principles); flag minimum safe manning rules.
- sources: none opened this session (hand off to the manning/flag agent).
- effective: Current.
- applicability: All designs with 882 kW. Below 750 kW, national engineer certification rules would apply instead (not relevant at 882 kW).
- implication: UMS pays back only if the flag (Transport Malta) actually reduces the engineer count or watch rota, or if long voyages make 3-watch engine manning impractical.
- uncertainty: Ask Transport Malta for indicative safe manning with and without UMS for each design.

### AUT-04
- claim: NEW: should a 52 m LCT with 2 × 441 kW go UMS?
- status: CONDITIONAL (recommendation; costs are budget estimates)
- finding: **Budget estimate (agent judgement, low confidence)**: the incremental cost of AUT-UMS over a basic Part C Ch 3 alarm system on a small twin-engine ship is about **EUR 40k–120k**. This covers alarm and monitoring system expansion, cabin and bridge alarm extensions, engineer-call/dead-man system, extra sensors, automatic standby generator start and blackout recovery, and extra class approval and commissioning tests. It adds a little to annual survey time (alarm function tests). It also **adds E26 scope** (AUT-09). Arguments for: India→Europe delivery and long voyages; possible reduction in engineering crew; resale and charter appeal in Europe. Arguments against: short shuttle LCT voyages where the engine room is attended anyway; simple high-speed engines with factory alarm panels; an extra networked CBS. Recommendation: design **"UMS-ready"** (cable routes, sensor provisions, alarm-system capacity) and decide once Transport Malta has given indicative manning for both options.
- regulation: BV NR467 Part F (AUT-UMS); SOLAS II-1 Part E (770 GT).
- sources: none for costs (agent judgement).
- effective: n/a
- applicability: All designs. For < 500 GT, the class route is via NR566 / Part F.
- implication: The decision is set by manning economics, not by technical need.
- uncertainty: Get a BV view and alarm-system vendor quotes for both options.

### AUT-05
- claim: Dossier §5: "shaft monitoring changes need BV assessment"; NEW: BV MON-SHAFT notation.
- status: CONDITIONAL
- finding: **MON-SHAFT** is a BV additional notation for propeller-shaft condition monitoring. It is common on BV ro-ro and general cargo fleets alongside AUT-UMS. A Thordon Bearings note on BV requirements (about a decade old) says MON-SHAFT lets a **modified tailshaft survey replace withdrawal at 5 years, with a full withdrawal survey still required every 10 years**, and that BV **extended MON-SHAFT to water-lubricated systems**. Condition monitoring typically involves regular lube-oil analysis (or water-quality monitoring for water-lubricated systems), bearing temperature monitoring, bearing wear-down records and seal checks. Current BV text was not read.
- regulation: BV NR467 Part F (monitoring notations; section unverified); IACS UR Z21.
- sources: [Thordon – meeting BV MON-SHAFT requirements (search result)](https://thordonbearings.com/docs/default-source/marine/class-society/thordons_comments_to_meet_bv_mon-shaft_requirements_for_extended_shjaft_withdrawal.pdf?sfvrsn=4b6059cf_12); [Cruise Industry News 2016 – BV/LR/CCS revised shaft monitoring rules (search result)](https://cruiseindustrynews.com/cruise-news/2016/01/new-class-rules-favors-seawater-lubricated-propeller-shafts/); [DNV TMON water-lubricated notations (comparator, search result)](https://dnv.com/news/new-dnv-gl-notations-for-water-lubricated-tail-shafts-offers-unlimited-intervals-between-shaft-withdrawals-54331)
- effective: Current BV rules (edition not read).
- applicability: Optional, all sizes.
- implication: The value is lower for small twin shafts, because withdrawal at drydock is relatively cheap. **Budget estimate (agent judgement)**: about EUR 5k–15k per shaftline for sensors and set-up, plus about EUR 0.5k–1k per year for sampling and analysis. Choose it only if the lubrication concept supports it (AUT-06).
- uncertainty: Obtain BV's current MON-SHAFT requirements and intervals, especially for water-lubricated open-loop systems on a beaching ship.

### AUT-06
- claim: NEW: oil versus water-lubricated stern tubes, IACS UR Z21 and tailshaft survey intervals.
- status: CONDITIONAL
- finding: Under UR Z21, as applied by class, the interval between propeller-shaft surveys is **not to exceed 60 months (5 years)**. For oil-lubricated systems, **lube-oil analysis is required at intervals not exceeding 6 months**. An approved condition-monitoring scheme may give an equivalent level of safety and allow alternative survey methods without full withdrawal. Agent knowledge, unverified this session because the search budget ran out: Z21 defines survey methods with and without shaft withdrawal, and open-loop water-lubricated shafts face stricter withdrawal conditions unless they are corrosion-resistant or monitored. **For a beaching LCT**, sea-water-lubricated rubber bearings take in sand and silt when the ship grounds in shallow water, which speeds up wear. Oil-lubricated stern tubes depend on seal integrity, and seals are at risk from debris and lines. This is an engineering decision to take with the stern-gear supplier and BV.
- regulation: IACS UR Z21 (current revision not opened); BV NR467 Part A (tailshaft survey).
- sources: [ICS Class instruction based on UR Z21 (search result)](https://surveyors.icsclass.org/wp-content/uploads/2022/07/PO02-TI04-Propeller-shaft-survey-Ver.-01-05-2020.pdf); [PRS publication on shaft surveys (search result)](https://prs.pl/wp-content/uploads/2024/04/p111p_en.pdf)
- effective: Current.
- applicability: All designs.
- implication: The lubrication choice sets the 5-year drydock scope and the MON-SHAFT eligibility.
- uncertainty: Read the current Z21 revision and BV text. Confirm the intervals for each lubrication type.

### AUT-07
- claim: Dossier §8/§9: engine offers include "TVA"; class requires "torsional vibration analysis".
- status: CONDITIONAL
- finding: The torsional vibration calculation (TVC) for the propulsion line (engine, flexible coupling, gearbox, shafting, propeller), and for gensets as required, must be **submitted to BV for approval**. Permissible torsional stresses follow IACS UR M68 ("Dimensions of propulsion shafts and their permissible torsional vibration stresses"; agent knowledge) as implemented in NR467 Part C Ch 1 (shafting and shaft-vibration sections; section numbers unverified). A TVC prepared by the engine maker, as quoted in the dossier, is normal, but it must use the **final** propeller, gearbox and coupling data and be BV-approved. Shaft-alignment calculations may also be required depending on shaft size and arrangement; BV's threshold was not verified.
- regulation: IACS UR M68 (agent knowledge); BV NR467 Part C Ch 1.
- sources: none opened (search budget exhausted).
- effective: Current.
- applicability: All designs.
- implication: Freeze propeller and gearbox early. A late change means TVC rework and BV re-approval.
- uncertainty: Confirm UR M68 revision, the BV section, and whether alignment calculations are required for this shaft size.

### AUT-08
- claim: NEW: how notations change through-life cost.
- status: CONDITIONAL (budget-level reasoning)
- finding: Each optional notation adds approval and commissioning cost at build and annual survey items through life, and saves costs elsewhere. **AUT-UMS** adds alarm function tests at surveys and may save engineering crew (AUT-03). **MON-SHAFT** adds 6-monthly sampling and records and may avoid shaft withdrawals (AUT-05). An **in-water-survey notation** may avoid one drydocking per 5 years, though this is doubtful for a beaching LCT (CLS-10). **CYBER RESILIENT** (mandatory for 770 GT) adds owner programme upkeep and survey checks (CYB-05). **CYBER SECURE** adds cost with little benefit for an LCT (CYB-07).
- regulation: As referenced.
- sources: as in the cross-referenced records.
- effective: n/a
- applicability: All designs.
- implication: Choose notations against the operating profile, not by default.
- uncertainty: Build a 10-year cost model once BV quotations are in hand.

### AUT-09
- claim: NEW: interaction between UMS and E26 scope.
- status: CONDITIONAL (agent judgement based on CYB-03 and CYB-04)
- finding: An AUT-UMS alarm and monitoring system is normally networked: it gathers signals from engines, gensets, tanks and pumps and extends alarms to the bridge and cabins. That makes it an in-scope "machinery alarm/monitoring" CBS for propulsion and power, and it usually **cannot meet the isolation criteria for exclusion**. On the 770 GT ship, UMS therefore usually means at least one formal E26 security zone with E27 evidence from the alarm-system supplier. On 390 and 490 GT ships this does not arise.
- regulation: IACS UR E26 Rev.1 §1.3.2, §6.
- sources: [IACS UR E26 Rev.1 (search result)](https://iacs.s3.af-south-1.amazonaws.com/wp-content/uploads/2022/02/04140503/UR-E26-Rev.1-Nov-2023-CR.pdf); [ClassNK E26 explanation (search result)](https://www.classnk.com/hp/pdf/activities/cybersecurity/e_003.pdf)
- effective: As CYB-01.
- applicability: 770 GT.
- implication: Include the E26 cost in the UMS business case for the 770 GT design. Specify an alarm-system vendor with E27 Rev.1 evidence.
- uncertainty: BV confirmation.

## B. Missing topics (not in dossier but material)
- **NR566 (< 500 GT arrangement, stability and systems)** is not mentioned, though it governs the 390 and 490 GT variants. CLS-01, CLS-03.
- **Rule edition fixed by contract date.** NR467 Jan/Jul 2026 and NR600 Mar 2026 editions, and the contract-date principle. CLS-02, CLS-04.
- **Navigation notation (unrestricted vs coastal area)** as a major structural cost lever, and its conflict with an India→Europe delivery voyage. CLS-06.
- **Service notation choice** (ro-ro cargo ship vs general cargo ship) and treatment of beaching. CLS-05.
- **Tonnage-margin risk at 500 GT.** A design that measures ≥ 500 GT switches to NR467 Parts B/C and mandatory E26. CLS-01.
- **E26 "international voyages" condition and the CBS exclusion route (E26 §6)**, including its four criteria. CYB-01, CYB-04.
- **E26 deliverables and who owns them** (yard as systems integrator). CYB-05.
- **BV NR659 notations** and the CYBER RESILIENT service feature. CYB-07.
- **IMO cyber guidelines, now Rev.3 / Rev.4**, and MSC.428(98) through ISM. CYB-08.
- **IMO direction: a non-mandatory cyber code first.** CYB-09.
- **SOLAS II-1 Part E and the STCW 750 kW engineer threshold** in the UMS decision. AUT-02, AUT-03.
- **UMS increases E26 scope.** AUT-09.
- **Stern-tube lubrication choice for a beaching ship.** AUT-06.
- **TVC must be BV-approved with final data.** AUT-07.
- **Survey regime, and in-water survey eligibility for a beaching LCT.** CLS-10.

## C. Incorrect or outdated claims in the dossier
- "Class and cyber: BV NR467/NR600 applicability" → incomplete. NR566 governs arrangement, stability and systems below 500 GT. NR600 governs hull structure for all three variants (length < 65 m). CLS-01.
- "500 GT … IACS E26/E27 scope" (§2 threshold table) → needs a qualifier. Mandatory only for cargo ships **≥ 500 GT engaged in international voyages**, contracted on or after 1 July 2024. Passenger ships are in scope at any size. CYB-01.
- "Standalone/analogue systems may reduce scope, not automatically remove applicability" → correct at ship level. At system level, a CBS meeting all four isolation criteria can be **fully excluded** through a class-accepted risk assessment, and non-computer systems are not CBS at all. CYB-04.
- Implied reliance on older cyber material → BV publications that cite E26 for contracts "after 1 January 2024" are outdated (the original UR was withdrawn). MSC-FAL.1/Circ.3/Rev.2 has been superseded by Rev.3 (2025) and, conditionally, Rev.4 (2026). CYB-07, CYB-08.
- "E27 where applicable" for engines (§8) → correct only for the 770 GT design. Not mandatory for 390 and 490 GT. CYB-06.

## D. Conflicting information found
- **E26/E27 effective date.** DNV news (2022), a BV brochure (2023) and some ABS pages say 1 January 2024. IACS UR E26 Rev.1 / E27 Rev.1, BV NR659 R04 (Jul 2024) and ABS Regulatory News say contracts on or after **1 July 2024**. Trust **1 July 2024**: the January 2024 date belonged to the withdrawn 2022 originals.
- **Exclusion of isolated systems.** ABS FAQ: a fully independent CBS "is not required to comply". ClassNK and KR: exclusion requires a risk assessment approved by the Society. A blog: air-gapping does not automatically exempt. Trust the **ClassNK/KR position (documented, class-accepted exclusion)**, because it matches the E26 §6 structure. Confirm BV's practice.
- **Current IMO cyber guideline revision.** The IMO cyber page still cites Rev.2. EU Council (2026) and IMO material cite Rev.3. A Rev.4 PDF exists; one search extract says MSC 111 approved it, another could not confirm. Treat **Rev.3 as confirmed** and Rev.4 as likely current pending the MSC 111 report.
- **NR566 edition.** The BV listing shows Nov 2024; a third-party copy is Jul 2022 (R03). Trust BV.
- **NR659 edition.** BV shows R04 Jul 2024; a standards retailer lists "NR659:2023" as current. Trust BV.
- **NR467 "current edition".** The BV index shows Part A R25 / Part F R20 dated Jan 2026, while a Jul 2026 main-changes document also exists. Both are consistent: Parts are reissued separately, and the edition in force at contract date governs.
- **Meaning of AUT-IMS.** A BV marketing article links it to "smart machinery"; rule wording not read. Unresolved.

## E. Matters requiring written flag-state / class confirmation
To Bureau Veritas:
1. Which rule set applies to each variant (390 / 490 / 770 GT, 51 m hull)? Specifically: NR600 for hull structure; NR566 or NR467 Parts B and C for systems; which NR467 edition, given the planned contract date.
2. Which service notation(s) will BV assign to a 24 TEU bow-ramp LCT carrying vehicles and containers ("ro-ro cargo ship" or "general cargo ship")? How is **beaching** handled (notation, design load case, survey conditions)?
3. Current definitions of the **coastal area** and **sheltered area** notations. Can a restricted-notation ship get a one-off **India→Europe delivery-voyage** approval, and under what conditions?
4. For the 770 GT design: confirm E26 Rev.1 / E27 Rev.1 apply (contract date, international voyages), and how BV records compliance (CYBER RESILIENT service feature under NR659).
5. E26 §6 exclusions: do serial NMEA 0183 or CAN-bus (J1939) links count as "IP-network connections"? Does a locked or covered service port satisfy "no accessible physical interface"? Is MED navigation and radio equipment certified to IEC 61162-460 / IEC 63154 accepted in place of E27 documents?
6. The full E26 submission list and template set BV expects from the yard, and BV's typical review turnaround.
7. Is any E26 Rev.2 or IACS UI applicable to a 2026 contract?
8. For the 390 and 490 GT designs: confirm E26/E27 are **not** required, and which E22 (CBS) requirements still apply under NR566.
9. AUT-UMS (and the NR566 equivalent for < 500 GT): the full requirement list and incremental plan-approval and survey scope. Does an AUT-UMS alarm system make the E26 zone mandatory?
10. Current MON-SHAFT requirements and intervals for oil-lubricated and water-lubricated stern tubes on a beaching ship. UR Z21 survey method options for each.
11. Is a shaft-alignment calculation required for this shaft size? TVC submission requirements (gearbox/coupling data).
12. Name and requirements of the in-water-survey notation, and whether beaching rules it out.
13. Itemised fee quotation for each variant (class new construction, statutory delegation, E26 review and test, annual fees).
14. Does BV hold Transport Malta RO authorisation for every certificate each variant needs, including Malta NCV Code certificates for < 500 GT?

To Transport Malta (flag):
15. Indicative minimum safe manning for each variant **with and without** UMS, for 882 kW propulsion.
16. Does Malta impose any cyber requirement (beyond ISM / MSC.428(98)) on 770 GT ships, or on < 500 GT NCV Code ships?
17. Will Malta issue a single-voyage permit for delivery from India if the ship holds a restricted class navigation notation?

## F. Register entries (sources, vendors, products, prices)
| Category | Name | Item / model | Certificate / approval (exact, only if verified; else "not verified") | Price (currency, date, basis, label) | Link | Notes |
|---|---|---|---|---|---|---|
| Class rules | Bureau Veritas | NR600, March 2026 (R08): hull structure, cargo ships < 65 m | n/a (rule) | n/a | [PDF](https://rulesexplorer-docs.bureauveritas.com/documents/nr600/mar2026/600-NR_2026-03.pdf) | Seen in search; domain blocked for fetch |
| Class rules | Bureau Veritas | NR566, Nov 2024: arrangement, stability, systems < 500 GT | n/a | n/a | [Page](https://marine-offshore.bureauveritas.com/nr566-hull-arrangement-stability-and-systems-ships-less-500-gt) | Edition per BV listing (search) |
| Class rules | Bureau Veritas | NR467 Jan 2026 / Jul 2026 editions | n/a | n/a | [Jul 2026 main changes](https://rulesexplorer-docs.bureauveritas.com/documents/nr467/jul2026/467-NR_MainChanges_2026-07.pdf) | Part F R20 Jan 2026 |
| Class rules | Bureau Veritas | NR659 R04, Jul 2024: cyber notations | n/a | n/a | [PDF](https://rulesexplorer-docs.bureauveritas.com/documents/nr659/jul2024/659-NR_2024-07.pdf) | CYBER MANAGED / RESILIENT / SECURE |
| IACS | IACS | UR E26 Rev.1 (Nov 2023) | n/a | n/a | [PDF](https://iacs.s3.af-south-1.amazonaws.com/wp-content/uploads/2022/02/04140503/UR-E26-Rev.1-Nov-2023-CR.pdf) | Contracts ≥ 1 Jul 2024 |
| IACS | IACS | UR E27 Rev.1 (Sep 2023) | n/a | n/a | [PDF](https://iacs.s3.af-south-1.amazonaws.com/wp-content/uploads/2022/05/29103854/UR-E27-Rev.1-Sep-2023-UL.pdf) | Supplier obligations |
| IMO | IMO | MSC-FAL.1/Circ.3/Rev.3 and Rev.4 | n/a | n/a | [Rev.3](https://wwwcdn.imo.org/localresources/en/OurWork/Facilitation/FAL%20related%20nonmandatory%20documents/MSC-FAL.1-Circ.3-Rev.3.pdf) | Rev.4 approval date conditional |
| Class guidance | ClassNK | E26 Rev.1 explanation (exclusion criteria) | n/a | n/a | [PDF](https://www.classnk.com/hp/pdf/activities/cybersecurity/e_003.pdf) | Secondary class guidance |
| Class guidance | KR | Cyber resilience approval & survey guide | n/a | n/a | [PDF](https://www.krs.co.kr/TECHNICAL_FILE/Cyber%20Resilience%20Approval%20and%20Survey%20Guide%20for%20Ship%20Automation%20Systems_Rev0.0(0).pdf) | Exclusion criteria |
| Class guidance | ABS | UR E27 FAQ | n/a | n/a | [Page](https://ww2.eagle.org/en/Products-and-Services/vendor-certification/abs-cybersafety-for-resilience/faq-cyber-resilience-program.html) | Isolated CBS statement |
| E27 example | Ascenz Marorka | Digital solutions (not LCT-relevant) | BV type approval to NR467, NR659, UR E27 Rev.1. Certificate number not verified | n/a | [BV news](https://marine-offshore.bureauveritas.com/newsroom/ascenz-marorka-receives-type-approval-cybersecurity-its-digital-solutions-0) | Shows BV issues E27 TAs |
| Vendor (gensets controls) | DEIF | Generator / power-management controllers | Vendor claims "full IACS UR E27 certification". Not verified | not obtained | [DEIF](https://www.deif.com/deif-cybersecurity/cybersecurity-you-can-document/) | Marketing claim; ask for certificate |
| Vendor (stern gear) | Thordon Bearings | Water-lubricated shaft bearings; BV MON-SHAFT note | not verified | not obtained | [PDF](https://thordonbearings.com/docs/default-source/marine/class-society/thordons_comments_to_meet_bv_mon-shaft_requirements_for_extended_shjaft_withdrawal.pdf?sfvrsn=4b6059cf_12) | Old document; MON-SHAFT 5/10-yr logic |
| Database | Bureau Veritas | Approval Explorer | n/a | free | [Site](https://approvalexplorer.bureauveritas.com/) | Not reachable this session |
| Budget | Class new construction (BV) | ~50 m LCT, India-built | n/a | EUR 80k–200k, 2026. **Budget estimate (agent judgement), low confidence** | — | No public BV fee scale found (CLS-11) |
| Budget | E26 compliance, 770 GT | Docs + class review/test + network hardware | n/a | EUR 20k–100k in total, 2026. **Budget estimate (agent judgement)** | — | CYB-11 |
| Budget | AUT-UMS increment | Alarm, monitoring, extensions, standby automation | n/a | EUR 40k–120k, 2026. **Budget estimate (agent judgement)** | — | AUT-04 |
| Budget | MON-SHAFT | Sensors and set-up per shaftline; annual sampling | n/a | EUR 5k–15k per shaft; EUR 0.5k–1k per year. **Budget estimate (agent judgement)** | — | AUT-05 |

## G. Card-ready summary (plain English, for a founder; ≤ 350 words)
- **Which BV rulebook applies.** All three designs use BV **NR600** for hull structure (hull under 65 m) (CLS-01/02). Machinery, electrical, stability and fire follow **NR566** under 500 GT and the stricter **NR467** at 770 GT (CLS-03/04). The edition in force on the contract date applies.
- **Biggest structural cost lever: the navigation notation, not GT.** "Coastal area" (believed to be within 20 nm of shore) gives lighter steel. An ocean delivery from India to Europe then needs a special BV/flag approval, or the ship has to be built to "unrestricted" from the start (CLS-06).
- **Cyber (IACS E26/E27).** Mandatory for cargo ships of **500 GT and over on international voyages contracted from 1 July 2024**: yes for 770 GT, guidance only for 390 and 490 GT (CYB-01/02). It means paperwork plus a commissioning test (network map, equipment list, design description) and supplier cyber evidence for computer-controlled systems (CYB-05/06). It does **not** mean buying an integrated bridge.
- **How to keep cyber small.** Use stand-alone equipment with no IP network, locked service ports and no remote access. Such systems can be excluded with a BV-accepted risk assessment (CYB-04/12). Budget estimate: EUR 20k–100k and 3–6 months, run in parallel with design (CYB-11).
- **Watch the 500 GT line.** If the "490 GT" design measures 500 GT or more, the rulebook and cyber requirement both change. Keep a margin (CLS-01).
- **UMS (unattended engine room).** Roughly EUR 40k–120k extra (estimate), and it adds cyber scope at 770 GT. Worth it only if Malta's safe manning actually cuts engineers or watches; 882 kW is above the 750 kW engineer-certificate threshold (AUT-03/04/09). Design "UMS-ready" and decide later.
- **MON-SHAFT.** Lets the 5-year shaft withdrawal be skipped; a full survey is still due every 10 years under older BV guidance. The gain is small for small twin shafts. Choose stern-tube lubrication with beaching sand in mind (AUT-05/06).
- **Before deciding:** get BV's written answers to the questions in Section E, an itemised fee quote, and Malta's indicative safe manning with and without UMS. BV fees are not public; EUR 80k–200k is a rough estimate (CLS-11).
