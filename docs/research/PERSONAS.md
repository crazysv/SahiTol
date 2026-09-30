# Simulated Personas and Journey Maps

> [!IMPORTANT]
> **Provenance Disclosure**: These personas are synthesized exclusively from published desk research, academic studies, and the SIH26229 problem statement. **No primary interviews or fieldwork were conducted by this project.** Names, demographics, and scenarios are illustrative simulations to guide user experience and software testing; they do not depict real participating individuals.

---

## Persona A: Rajesh Kumar — Independent Collector (Delhi-NCR)

### Profile & Operating Context
- **Role**: Independent itinerant waste collector (*feriwallah* / *kabadiwala*)
- **Location**: Operates across East Delhi and Ghaziabad informal trading corridors
- **Language**: Hindi (Devanagari; functional conversational literacy, limited technical English)
- **Hardware**: Entry-level Android smartphone (Android 11, 2GB RAM, cracked screen, intermittent prepaid 4G data)
- **Primary Materials**: Household scrap, discarded small electronics (chargers, broken mobile phones, CRT TVs, fan motors, power supply units)
- **Financial Reality**: Operates on daily cash liquidity (needs ₹500–₹1,500 daily for household expenses). Cannot wait for weekly bank settlements. Relies on informal scrap dealers for quick turnarounds.

### Key Pain Points
1. **Uncertain Valuation**: Does not know whether a recovered computer motherboard or TV chassis is worth ₹20/kg or ₹150/kg; scrap dealers often quote mixed plastic rates.
2. **Connectivity Blackouts**: Loses internet connection when collecting inside dense residential lanes or metal-roofed godowns.
3. **Complex Formal Interfaces**: Intimidated by apps demanding PAN, GST, or bank account numbers.

### User Journey with SahiTol
```mermaid
sequenceDiagram
    autonumber
    actor Rajesh as Rajesh (Collector)
    participant Phone as SahiTol Android (Offline)
    participant Server as SahiTol Backend (Cloud)
    actor Buyer as Scrap Center (Second Phone)

    Rajesh->>Phone: Selects Hindi language (audio welcome)
    Rajesh->>Phone: Takes photo of recovered circuit board lot
    Phone->>Phone: LiteRT suggests "PCB / Circuit Board" (offline)
    Rajesh->>Phone: Confirms material and enters estimated 3,500g
    Phone->>Phone: Displays indicative range: ₹350 - ₹480 (PRICE_V1)
    Rajesh->>Phone: Reviews nearby collection centres (offline distance list)
    Note over Rajesh,Phone: Transaction stored locally in Room database
    Rajesh->>Buyer: Reaches formal collection centre
    Rajesh->>Phone: Generates offline handover QR (SAHITOL-JCS-1)
    Buyer->>Phone: Scans QR with web console on second phone
    Buyer->>Server: Verifies proposal hash and enters scale weight (3,400g)
    Buyer->>Rajesh: Hands over ₹400 in cash
    Rajesh->>Phone: Records cash payment received
    Phone->>Server: Syncs outbox when network reconnects
```

---

## Persona B: Santosh Shinde — Electronics Repair & Scrap Collector (Pune)

### Profile & Operating Context
- **Role**: Commercial repair aggregator and collector
- **Location**: Industrial periphery of Pune and Pimpri-Chinchwad, Maharashtra
- **Language**: Marathi (fluent Marathi speaker and reader; prefers Marathi voice guidance)
- **Hardware**: Mid-tier Android smartphone (Android 13, 4GB RAM)
- **Primary Materials**: Commercial air conditioner scrap, industrial battery banks, discarded laptop components, power tools
- **Regulatory Awareness**: Knows that batteries are dangerous and subject to scrutiny, but lacks clarity on which nearby recyclers hold valid MPCB authorizations.

### Key Pain Points
1. **Hazardous Regulatory Risk**: Fear of being penalized for transporting scrap lithium-ion and lead-acid batteries together with general scrap.
2. **Linguistic Jargon**: English technical terms (e.g., "Cathode Ray Tube", "Printed Circuit Board") do not match regional Marathi trade vernacular (*e-kachra*, *shisha*, *tamba*).
3. **Stale Dealer Directories**: Has visited facilities listed on old government PDF lists only to find them shut down or refusing small lots.

### User Journey with SahiTol
```mermaid
sequenceDiagram
    autonumber
    actor Santosh as Santosh (Collector)
    participant App as SahiTol Android (Marathi)
    participant DB as PostGIS Recycler Directory

    Santosh->>App: Chooses Marathi (audio prompts active)
    Santosh->>App: Creates lot for discarded UPS batteries
    App->>App: Triggers "BATTERY_RULES" safety alert (audio warning)
    App->>App: Warns against opening, puncturing, or shorting terminals
    Santosh->>App: Searches for MPCB authorized battery facilities
    App->>DB: Filters candidates: Route=BATTERY_RULES, Status=L3/L4 Verified
    App->>Santosh: Recommends nearby authorized battery collection centre
    Santosh->>App: Compares offered rates and schedules delivery
```

---

## Persona C: Anil Verma — Formal Collection Centre / Dismantler Manager (Noida)

### Profile & Operating Context
- **Role**: Operations Manager at an authorized E-Waste Dismantling & Collection Centre
- **Location**: Industrial Area Phase II, Noida / Delhi-NCR border
- **Surface**: Desktop / Tablet browser (Recycler Web Console) and borrowed Android smartphone for warehouse gate scans
- **Regulatory Status**: Holds valid state pollution control board authorization for e-waste dismantling (capacity: 500 MT/year)
- **Primary Need**: Transparent procurement logs, tamper-evident transaction records to demonstrate traceability, and fast verification at the weighbridge.

### Key Pain Points
1. **Quality and Weight Mismatch**: Discrepancies between informal sellers' verbal claims and actual weighed moisture/contamination at the weighbridge.
2. **Double-Selling & Fraud**: Concerns about fraudulent sellers presenting the same lot photos or receipts to multiple buyers.
3. **Paperwork Burden**: Managing manual paper registers for dozens of small cash purchases every week.

### User Journey with SahiTol
```mermaid
sequenceDiagram
    autonumber
    actor Anil as Anil (Facility In-charge)
    participant Web as SahiTol Recycler Web
    participant Server as FastAPI + PostgreSQL
    actor Collector as Informal Collector

    Collector->>Anil: Arrives with 8.5kg mixed electronics lot
    Collector->>Anil: Presents Digital Handover QR on phone
    Anil->>Web: Opens QR scanner on mobile browser (R04)
    Web->>Server: Verifies SAHITOL-JCS-1 canonical proposal hash
    Anil->>Web: Weighs lot on calibrated digital scale: 8,200g
    Anil->>Web: Enters measured weight and confirms ₹950 total terms
    Web->>Server: Commits confirmed handover (CONFIRMED_PENDING_ACK)
    Anil->>Collector: Pays ₹950 cash and records payment assertion (R05)
    Web->>Server: Updates lot status and appends to procurement export (R07)
```
