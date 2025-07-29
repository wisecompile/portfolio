# Modicon_M340-OPC-HMI-SQL

## 🧩 Project Overview

Cross-platform industrial automation projects: PLC, HMI, Fieldbus, Python, SQL

This repository documents a complete industrial automation architecture built on **Schneider Modicon M340 PLC**, integrated with **SQL Server**, **OPC middleware**, and **HMI interfaces**. It includes fully traceable serialization, model-specific toolpath logic, tool wear monitoring, and dust collection coordination.

The project is divided into multiple functional stages:

- `Stage 0` — Product serialization using barcode scanners with automated model assignment.
- `Stage X` — Height correction logic based on mold variation and manual learning.
- `Stage Y` — Dynamic tool contact detection, PID-regulated feedrate, and compressed air optimization.

---

## Repository Structure

```plaintext
Modicon_M340-OPC-HMI-SQL/
├── README.md
├── Stage0_Barcode_Parser_SQL/
│   └── Stage0_Portfolio.md
├── StageX_HMI_OPC_PLC/
│   ├── Portfolio.md
│   ├── HMI_1.jpg
│   ├── HMI_2.jpg
│   ├── HMI_variables.jpg
│   ├── Modbus.jpg
│   └── opc_sql_handler.lua
├── StageY_Modicon_FBD_CANopen/
│   ├── StageY_Portfolio.md
│   ├── ToolContactDetection.gif
│   ├── FeedRatePID.gif
│   ├── DustCollectionLogic.gif
│   └── Supporting_Logic/
│       ├── StageY_FeedRate_PID.md
│       └── StageY_DustCollectionLogic.md
└── docs/
    └── Full_Portfolio_PDF.pdf (optional)
```