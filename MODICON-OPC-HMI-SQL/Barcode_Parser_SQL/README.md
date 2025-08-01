## Role Assignment via Barcode Scanning and Bidirectional SQL Exchange

Identification barcodes with embedded control characters can be attached to any physical object involved in the production process. These control characters dynamically assign roles to the operator as an agent for data exchange with SQL tables.

- The operator uses **industrial barcode scanners**, operable even while wearing gloves;
- There is **no need to touch a keyboard or screen**;
- This drastically **reduces operator fatigue** and **minimizes qualification requirements**;
- The resulting data is displayed in real time on a **large screen** for immediate verification and traceability.

> ✅ This approach naturally enforces discipline by workflow design rather than supervision—it is impossible to complete the operation without physically scanning the barcode. 
>
> ✅ The operator completes a SQL query in just a few seconds with two scans — no keyboard, no touchscreen, no UI interaction required.



#### Examples of roles: serialization

The operator first scans a serial number from a roll of pre-printed labels. Then, the operator scans the barcode attached to the injection mold. The barcode on the mold contains a set of hidden control characters that, in this context, assign a specific role—namely, the role of a serialization agent (@M)

This operation initiates a **serialization procedure**, which:

- Creates a **new SQL record** using the scanned serial number as a **unique identifier**;

- Automatically inserts:

  - The **model number** (determined via the mold ID),

  - The **mold instance ID** (determined via the mold ID),

  - The **current recipe** (retrieved from system context),

  - The **timestamp** (current date/time from the system).

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

#### Examples of roles: defect registration 

As in the previous example, the operator first scans the product’s serial number. Next, the operator scans one of the defect marking barcodes from a template card; these barcodes contain the hidden control character %D. The parser switches to defect assignment mode and writes the result to the SQL table.

Given the established link between the product’s serial number and the mold number, this procedure ensures that defect information is also recorded in the mold table. As a result, the presence of defects can automatically trigger mold maintenance or servicing routines.

```SQL
-- Triggered when barcode contains hidden '@D' symbol
IF :TAG = '%D' 
BEGIN
    -- If no primary defect is registered for this serial number, set it as primary
    IF (SELECT defectPrimary FROM dbo.repairList WHERE serialNum = (SELECT serialNum FROM dbo.inspectionBatch)) IS NULL
        UPDATE repairList
        SET defectPrimary = :PREFIX
        WHERE serialNum = (SELECT serialNum FROM dbo.inspectionBatch)
    -- Otherwise, set it as secondary defect code
    ELSE IF (SELECT defectPrimary FROM dbo.repairList WHERE serialNum = (SELECT serialNum FROM dbo.inspectionBatch)) IS NOT NULL
        UPDATE repairList
        SET defectSecondary = :PREFIX
        WHERE serialNum = (SELECT serialNum FROM dbo.inspectionBatch)
END
```

#### Examples of roles: mold status update and maintenance logging 

In this procedure, the operator first scans the barcode on the mold, which contains an embedded control sequence @M. When the parser detects this sequence, it effectively “overwrites itself,” clearing the previous mold number and registering the new one. The operator then scans a service barcode from a separate template card; this barcode contains a control sequence (@S) that puts the scanner into service mode.

During this process, each completed operation on the mold is recorded, and the mold is further classified into categories such as "Suitable for all product types", "For less critical products", "To be withdrawn from operation".

```SQL
-- If the tag is '@M', reset mold batch and register new mold number
IF :TAG='@M'
BEGIN
    DELETE FROM moldBatch
    INSERT INTO moldBatch (moldNum)
    VALUES (:MARK3)
END

-- If the tag is '@S', log operation and update mold state based on suffixes
ELSE IF :TAG='@S'
BEGIN
    -- Log operation in moldLog
    INSERT INTO moldLog (DateTime, moldNum, operationNum)
    VALUES (:DATETIME, (SELECT moldNum FROM moldBatch), :PREFIX2)

    -- Different operation codes trigger various status/limit updates
    IF :PREFIX = '1'
    BEGIN
        UPDATE moldNum
        SET statusOK = '0',
            statusExtended = (SELECT serviceDesc FROM serviceList WHERE serviceNum = :PREFIX2)
        WHERE moldNum = (SELECT moldNum FROM moldBatch)
        IF :PREFIX2 = '12'
        BEGIN
            UPDATE moldNum
            SET counter2 = 0
            WHERE moldNum = (SELECT moldNum FROM moldBatch)
        END
    END
    ELSE IF :PREFIX2 = '21'
    BEGIN
        UPDATE moldNum
        SET darkOK = '1', lightOK = '1',
            limitsExtended = (SELECT serviceDesc FROM serviceList WHERE serviceNum = :PREFIX2)
        WHERE moldNum = (SELECT moldNum FROM moldBatch)
    END
    ELSE IF :PREFIX2 = '22'
    BEGIN
        UPDATE moldNum
        SET darkOK = '1', lightOK = '0',
            limitsExtended = (SELECT serviceDesc FROM serviceList WHERE serviceNum = :PREFIX2)
        WHERE moldNum = (SELECT moldNum FROM moldBatch)
    END
    ELSE IF :PREFIX2 = '23'
    BEGIN
        UPDATE moldNum
        SET darkOK = '0', lightOK = '1',
            limitsExtended = (SELECT serviceDesc FROM serviceList WHERE serviceNum = :PREFIX2)
        WHERE moldNum = (SELECT moldNum FROM moldBatch)
    END
    ELSE IF :PREFIX = '3'
    BEGIN
        IF :PREFIX2 = '33'
        BEGIN
            UPDATE moldNum
            SET counter1 = 0, counter2 = counter2 + 1
            WHERE moldNum = (SELECT moldNum FROM moldBatch)
        END
        UPDATE moldNum
        SET statusOK = '1',
            statusExtended = (SELECT serviceDesc FROM serviceList WHERE serviceNum = :PREFIX2)
        WHERE moldNum = (SELECT moldNum FROM moldBatch)
    END

    -- Output updated state for feedback
    SELECT 'MoldNum.' ,moldNum, ':' ,statusExtended, CHAR(13), ' Model.', modelNum, ' :', limitsExtended    
    FROM moldNum
    WHERE moldNum = (SELECT moldNum FROM moldBatch)
END
```

Thus, by assigning roles, all procedures for product movement and tracking of completed operations are carried out. This includes preparation for packaging, printing of transport labels, and printing of retail labels. In these cases, integration with Seagull BarTender Enterprise is used.





