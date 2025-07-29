# 📦 Automation Portfolio — Stage Zero

## 🔹 Stage Zero: Serialization via Barcode Scanning and SQL Record Creation

In this stage, the operator performs two consecutive barcode scans:

1. **Scans the mold identifier** from the product;
2. **Scans a pre-printed serial number** from a roll of unique codes.

This operation initiates a **serialization procedure**, which:

- Creates a **new SQL record** using the scanned serial number as a **unique identifier**;
- Automatically inserts:
  - The **model number** (determined via the mold ID),
  - The **mold instance ID**,
  - The **current recipe** (retrieved from system context),
  - The **timestamp** (current date/time from the system).

> ⚙️ Within 1–2 seconds, the operator fills a complex SQL record with two scans — no keyboard, no touchscreen, no UI interaction.

---

### 🧠 Operator-Centric Design

- The operator uses **industrial barcode scanners**, operable even while wearing gloves;
- There is **no need to touch a keyboard or screen**;
- This drastically **reduces operator fatigue** and **minimizes qualification requirements**;
- The resulting data is displayed in real time on a **large screen** for immediate verification and traceability.

> ✅ This process enforces discipline through workflow design, not supervision — it becomes impossible to skip serialization without bypassing physical scanning.

---

### 📦 Summary of What’s Stored in SQL:

- **Serial Number** (unique)
- **Model ID** (mapped via Mold ID)
- **Mold Instance**
- **Active Recipe ID**
- **Timestamp (Date/Time)**

---

## 📄 SQL Serialization Logic – Stage Zero

The SQL code below is executed by the parser during the serialization procedure. It is triggered when the mold barcode contains a hidden control character `@M`, which places the scanner into **serialization mode**.

The system ensures that serialization is **executed only once per serial number**, preventing accidental overwrites due to repeated scans.

```sql
-- Triggered when mold barcode contains hidden '@M' symbol
IF :TAG = '@M'
AND NOT EXISTS (
    -- Ensure this serial number hasn't already been recorded
    SELECT serialNum
    FROM serialSKU
    WHERE serialNum = (SELECT serialNum FROM castingBatch)
)
BEGIN
    -- Step 1: Increment mold usage counter
    UPDATE moldNum
    SET counter1 = counter1 + 1
    WHERE moldNum = :MARK3;

    -- Step 2: Create a new serialSKU record with associated data
    INSERT INTO serialSKU (
        serialNum,         -- unique serial number
        castingDateTime,   -- timestamp of the pour
        moldNum,           -- mold instance identifier
        SKU                -- product identifier (model + color)
    )
    VALUES (
        (SELECT serialNum FROM castingBatch),
        :DATETIME,
        :MARK3,
        (SELECT modelNum FROM moldNum WHERE moldNum = :MARK3)
        + (SELECT colorID FROM castColor)
    );

    -- Step 3: Return a message string for Industrial PC screen
    SELECT
        'Serial.', serialNum,
        ' MoldNum.', moldNum,
        CHAR(13),
        'Model.', LEFT(SKU, 3),
        '  Color.',
        (
            SELECT colorName
            FROM colorList
            WHERE colorID = (
                SELECT RIGHT(colorID, 3)
                FROM castColor
            )
        )
    FROM serialSKU
    WHERE serialNum = (SELECT serialNum FROM castingBatch);
END
```

---

### 🔁 Multi-Mode Scanning via Parser-Controlled Logic

Although the same barcode scanner is used for multiple functions, **it is not a special hardware device**. The scanner simply decodes the barcode and transmits its content as plain text to the system.

> The **parser logic on the industrial PC** interprets this content and determines the operational mode based on **embedded control characters** (prefixes).

#### 🔹 Supported Modes

| Prefix | Mode Name               | Description |
|--------|-------------------------|-------------|
| `@M`   | **Serialization mode**  | Links mold and serial number, creates new product record in SQL |
| `@S`   | **Mold service mode**   | Registers maintenance actions like cleaning, reassembly |
| `@D`   | **Defect logging mode** | Marks mold as defective using predefined defect tags |

This architecture allows:

- Using a **single physical scanner** for multiple workflows;
- **Hands-free, keyboard-free operation** (ideal for gloved operators);
- Simplified training and maintenance;
- Quick expansion with new modes (e.g. inspection, operator login) via parser updates.
