## Project Overview

Cross-platform industrial automation project: selected modules using PLC, HMI, Fieldbus, SQL.

This repository highlights several modules of interest, selected from a broader set of implemented solutions—not for coding complexity, but for architectural design, integration, and usability in operator-driven environments.

The project is organized into several sets, each representing a distinct production area with its own technology stack and integration logic:

- `Barcode_Parser_SQL` — Product serialization using barcode-embedded control characters, processed by the parser.
- `HMI_OPC_PLC` — Tool position retrieval from SQL, manual correction and adaptive system learning.
- `M340_FBD_CANopen` — Schneider Modicon M340 FBD code snippets for various operations.

---

## Repository Structure

```plaintext
Modicon_M340-OPC-HMI-SQL/
├── README.md
├── Barcode_Parser_SQL/
│   └── README.md
├── HMI_OPC_PLC/
│   ├── README.md
│   ├── HMI_1.jpg
│   ├── HMI_2.jpg
│   ├── HMI_variables.gif
│   ├── Modbus.gif
│   └── opc_sql_handler.lua
├── M340_FBD_CANopen/
    ├── README.md
    ├── ContactDetection.gif
    ├── FeedPID.gif
    └── PulseJet.gif

```
