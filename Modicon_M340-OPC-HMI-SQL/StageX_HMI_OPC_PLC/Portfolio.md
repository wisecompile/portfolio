# 📦 Automation Portfolio — Stage X

## 🔹 Stage X: Automated CNC Height Adjustment and Adaptive Correction Based on Mold Data

In this subsequent process step, a second operator scans the serial number of the product using an industrial barcode scanner. This triggers a request from a second industrial PC, which:

- Queries the SQL Server database for:
  - the geometric parameters of the product,
  - the processing recipe associated with the scanned serial number (including material hardness and machining conditions),
  - and the mold instance used.

- Distributes the data as follows:
  - Sends Z-axis spindle height and correction offsets to the Modicon M340 PLC;
  - Sends cutting speed and feed rate parameters, adjusted based on the expected material hardness, to the PLC via OPC Server;
  - Sends supplementary data to the HMI panel for operator reference.

> By retrieving the product recipe linked to the serial number, the system dynamically determines expected material hardness and automatically adjusts machining parameters such as spindle RPM and feed rate, ensuring optimal processing quality.

Once the data is received, the operator initiates the machining cycle. The M340 PLC:

- Positions the Z-axis spindle based on the model and mold-specific correction;
- Activates the spindle and executes the machining routine, using the adjusted processing parameters.

---

## 🖥️ HMI Interface and Operator Workflow — Stage X

The HMI interface shown in the image represents the initial screen displayed after the operator scans the serial number of the product.

![Initial HMI Screen – StageX_HMI_1](StageX_HMI_1.jpg)

### 🔹 Bidirectional SQL Communication and Parameter Injection

Upon scanning:
- The HMI panel initiates a query to the SQL Server using the scanned serial number.
- The system retrieves:
  - The product model number,
  - The specific mold instance used for this product, which may introduce minor geometric deviations relative to the standard model.

These values are immediately transferred via the OPC server to:
- the HMI panel (for display and operator confirmation), and
- the Modicon M340 PLC, where they populate internal memory variables used for calculating the Z-axis spindle position and machining parameters.

> 🔁 All data exchange is fully bidirectional:
> - At the beginning of the process, parameters are loaded from SQL to the PLC and HMI.
> - If the operator adjusts processing parameters, the changes can be written back to the SQL Server for future reuse.

---

### 📊 Tool Life Tracking in Normalized Units

The numeric bar at the bottom of the screen (e.g., 211) displays the current estimated tool usage, expressed in normalized units.

- Each model has a predefined weighting factor that reflects how aggressively it wears the tool.
- This allows heterogeneous models to be normalized into a standardized cycle count.
- After each completed operation, the system increments this counter based on the model's weighting coefficient.

This approach supports predictive tool replacement without requiring per-model calibration.

---

### 🧭 Manual Correction — *State 1 and State 2*

When launching a new mold series, the default Z-position retrieved from SQL may be slightly off.

- In this case, the operators can enter manual correction mode (as shown in State 2).
- Using a rotary dial, they can fine-tune the spindle’s Z-position up or down relative to the default.
- The right-hand bar graph visually displays the offset in real time.

![Manual Correction – StageX_HMI_2](StageX_HMI_2.jpg)

---

### 💾 Saving Persistent Corrections — “Transfer Changes”

If the correction proves to be consistently required for a specific mold instance:
- The operators press the “Transfer Changes” button.
- The system writes the updated Z-offset value back to the SQL Server, updating the record for this mold instance.

As a result:
- The next product using the same mold instance will automatically use the corrected value,
- Reducing future interaction and training the system over time.

The operators can further refine the value and repeat the process as needed.

> The long-term goal is to eliminate the need for operator input altogether.  
> Once mold-specific offsets are tuned and saved, the process can run hands-free, with all execution triggered via physical buttons — ideal for gloved operators.  
> The HMI is used only during the initial learning phase, after which it becomes purely optional.

---

### 🧠 OPC Communication Flow and System Architecture

The accompanying Variables diagram shows data routing through the OPC server:

- Data from SQL Server is injected into:
  - the HMI panel (for reference), and
  - the Modicon M340 PLC (for immediate use in logic and positioning).
- Updated values (e.g. Z-offsets) are written back to the SQL Server if changes are made by the operator.

![OPC Variable Mapping – StageX_HMI_variables](StageX_HMI_variables.jpg)

The architecture involves:
- A Modicon M340 PLC,
- A dedicated HMI terminal,
- Two SQL interface nodes connected via the OPC server.

![System Architecture – StageX_Modbus](StageX_Modbus.jpg)

---

### 📄 Lua Script: Bidirectional SQL-PLC Integration

A complete Lua script is provided that demonstrates:
- SQL read and write operations,
- Injection of SKU and mold-based parameters into Modbus OPC tags,
- Optional write-back to the SQL table if a Z-offset correction is applied by the operator.

👉 [Download opc_sql_handler.lua](sandbox:/mnt/data/opc_sql_handler.lua)
