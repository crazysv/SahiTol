# Pictogram & Safety Component Design Briefs for Google Stitch

## Metadata
- **Target Screen**: `C17` (Contextual Safety Library & Material Detail)
- **Target Components**: Inline Material Safety Warning Card (used on `C04`, `C05`, `C06`, and `A04`)
- **Author**: SahiTol Safety & Design Working Group (T035)
- **Status**: Brief Prepared for Owner Stitch Generation
- **Supported Languages**: Hindi (`hi`), Marathi (`mr`), English (`en`)
- **Regulatory Framework**: CPCB E-Waste Management Rules 2022, CPCB Battery Waste Management Rules 2022

---

## 1. Safety Design System & Color Tokens

To ensure immediate comprehension by informal waste collectors with low literacy or noisy ambient scrapyard conditions, all safety pictograms and cards use strict standardized color tokens:

| Token Name | Hex Code | Purpose | Visual Application |
|---|---|---|---|
| `safety-critical-fg` | `#DC2626` (Red-600) | Immediate physical danger | Border, prohibition diagonal slash, hazard badge |
| `safety-critical-bg` | `#FEF2F2` (Red-50) | High alert background | Card container fill |
| `safety-high-fg` | `#EA580C` (Orange-600) | Severe toxic fume/chemical risk | Border, warning triangle, warning text |
| `safety-high-bg` | `#FFF7ED` (Orange-50) | Warning background | Card container fill |
| `safety-isolation-fg` | `#D97706` (Amber-600) | Regulatory isolation / segregation | Battery route border, tape indicators |
| `safety-isolation-bg` | `#FFFBEB` (Amber-50) | Isolation container background | Card container fill |
| `safety-audio-btn` | `#0284C7` (Sky-600) | Audio narration trigger | Speaker button fill, high contrast |
| `safety-text-primary` | `#0F172A` (Slate-900) | Primary readability | Devanagari & Latin body copy |

---

## 2. Pictogram Specifications (9 Core Hazards)

Every pictogram must be designed as an unambiguous visual metaphor without relying on text labels for safety comprehension:

### 1. `icons/safety/no_burn_cables.svg` — Cable Safety
- **Hazard**: Burning plastic insulation emits toxic dioxins and hydrochloric acid fumes.
- **Visual Subject**: A bundle of coiled electrical copper cables with red/blue insulation.
- **Danger Element**: Orange/yellow flame licking up from underneath the cables.
- **Prohibition Element**: Prominent red circular prohibition ring with a 45-degree diagonal slash (`⃠`) overlying the flame and cable.
- **Do / Safe Action**: Small inset badge showing handheld mechanical cable stripper with green checkmark.

### 2. `icons/safety/no_acid_pcb.svg` — Circuit Board Chemical Hazard
- **Hazard**: Informal acid leaching and heating produces lethal hydrogen cyanide and nitrogen dioxide gas.
- **Visual Subject**: Green printed circuit board with soldered microchips.
- **Danger Element**: Chemical flask pouring bubbling green/yellow liquid onto the board, with skull/crossbones vapor cloud.
- **Prohibition Element**: Universal red prohibition slash (`⃠`) across the acid pour.
- **Do / Safe Action**: Board placed unbroken in a clean slotted storage crate.

### 3. `icons/safety/no_break_crt.svg` — CRT Glass Implosion & Lead
- **Hazard**: Vacuum implosion and airborne toxic lead/cadmium phosphor dust.
- **Visual Subject**: Silhouette of curved CRT display tube showing screen and rear electron gun funnel.
- **Danger Element**: Heavy claw hammer striking the front glass with radiating fracture lines and explosive outward shards.
- **Prohibition Element**: Red prohibition slash (`⃠`) across the hammer and shattering glass.
- **Do / Safe Action**: Whole CRT monitor resting face-down on a cushioned transport surface.

### 4. `icons/safety/isolated_battery.svg` — Lead-Acid Battery Upright Storage
- **Hazard**: Corrosive sulfuric acid leaks causing chemical burns and blindness; terminal shorting.
- **Visual Subject**: Heavy rectangular lead-acid battery with two top terminal posts.
- **Mandatory Cues**: 
  - Two bold vertical green arrows (`⬆⬆`) indicating mandatory upright orientation.
  - Strips of insulating black/yellow electrical tape clearly wrapped over both positive and negative terminals.
  - Leak-proof polyethylene containment tray underneath the battery base.

### 5. `icons/safety/tape_terminals.svg` — Lithium-Ion Battery Fire Hazard
- **Hazard**: Violent thermal runaway fires reaching 800°C; cannot be extinguished with water.
- **Visual Subject**: 18650 cylindrical cells and rectangular smartphone pouch lithium batteries.
- **Danger Element**: Yellow fire warning triangle with lightning bolt spark.
- **Mandatory Cues**:
  - Clear visual of electrical adhesive tape wrapped over metal contact pads and solder tags.
  - Red prohibition slash over metal pliers/wire cutters puncturing the pouch battery.

### 6. `icons/safety/isolated_container.svg` — Unknown Battery Segregation
- **Hazard**: Unidentified battery chemistries causing cross-contact sparks and spontaneous ignition.
- **Visual Subject**: Sturdy plastic bin with sand or vermiculite lining.
- **Mandatory Cues**:
  - Assorted small batteries placed separately inside so their terminals cannot touch.
  - Red prohibition slash over loose batteries dumped mixed inside a steel drum or scrap sack.

### 7. `icons/safety/stop_handling_hazard.svg` — Emergency Stop Handling
- **Hazard**: Leaking, hissing, smoking, or overheating e-waste components.
- **Visual Subject**: Raised bold open palm (universal "STOP" gesture) centered in an octagonal red badge.
- **Danger Element**: Toxic droplet falling from cracked casing with wavy rising heat/smoke lines.
- **Mandatory Cues**:
  - Distance indicator showing people walking away to an arrow labeled "10m".
  - Prohibition slash over bare human hands touching liquid puddles.

### 8. `icons/safety/no_burn_plastics.svg` — Flame-Retardant Plastics
- **Hazard**: Brominated flame retardants emitting carcinogenic polybrominated dioxins.
- **Visual Subject**: Molded black and grey computer monitor casing plastics (marked ABS / HIPS).
- **Danger Element**: Open campfire and burning barrel with dense black smoke.
- **Prohibition Element**: Universal red prohibition slash (`⃠`) over the fire.
- **Do / Safe Action**: Clean stacked casings delivered to an industrial recycling facility.

### 9. `icons/safety/no_dismantle_mixed.svg` — Mixed Electronic Assemblies
- **Hazard**: Concealed high-voltage charges in capacitors and hidden lithium cells.
- **Visual Subject**: Sealed metal electronic enclosure or home appliance.
- **Danger Element**: Crowbar and chisel prying open the seams.
- **Prohibition Element**: Universal red prohibition slash (`⃠`) across the pry tools.
- **Do / Safe Action**: Closed unit placed in cardboard container with a "Review Required" tag.

---

## 3. Screen Layout Specification for `C17` (Safety Library)

### Header & Context Area
- Title: "सुरक्षा मार्गदर्शिका (Safety Library)" / "सुरक्षा मार्गदर्शक (Safety Library)" / "Safety Library"
- Subtitle: "सामग्री अनुसार सुरक्षा नियम (Material Hazard & Handling Rules)"
- Language Toggle: Quick-switch pill chips for `हिंदी` | `मराठी` | `English`.

### Search & Filter Strip
- Chips: `सभी (All)` | `केबल (Cables)` | `सर्किट बोर्ड (PCB)` | `बैटरी (Battery)` | `सीआरटी (CRT)` | `प्लास्टिक (Plastics)`.

### Safety Card Anatomy
1. **Hazard Badge**: Top-left colored pill indicating `अति संवेदनशील (Critical Hazard)` or `उच्च जोखिम (High Warning)`.
2. **Pictogram Display**: Centered or left-aligned high-contrast SVG container ($96 \times 96\text{ dp}$).
3. **Card Title**: Large bold typography in Devanagari ($\ge 18\text{ sp}$).
4. **Hazard Description**: 2-line plain-language summary of what harms the collector.
5. **Safe Handling Action**: Green-tinted container highlighting the correct action.
6. **Prohibited Action**: Red-tinted container highlighting what must NEVER be done.
7. **Audio Playback Bar**: Full-width button with speaker icon: "सुनें (Listen) • 0:18" allowing one-tap offline playback.
8. **Statutory Source Attribution**: Small footnote: "स्रोत: सीपीसीबी ई-कचरा नियम 2022 (CPCB E-Waste Rules 2022)".

---

## 4. Interaction & Accessibility Invariants

1. **Audio First**: Every safety card must have a dedicated audio button with a minimum touch target of $48 \times 48\text{ dp}$. Tapping the button plays the pre-generated offline MP3 clip corresponding to the active language.
2. **Non-Instructional Invariant**: The cards never provide DIY disassembly steps, chemical extraction recipes (e.g., acid leaching tutorials), or false safety claims (e.g., claiming cloth masks make toxic acid fumes safe).
3. **Offline Guarantee**: All vector pictograms and audio clips must be stored locally in APK assets (`assets/safety/`) and remain 100% accessible in airplane mode.
