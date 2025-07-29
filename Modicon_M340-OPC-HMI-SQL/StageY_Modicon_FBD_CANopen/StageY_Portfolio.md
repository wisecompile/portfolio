# 📦 Automation Portfolio — Stage Y

## 🔹 Stage Y: Relative Surface Detection via Spindle Current and Tool Wear Monitoring (Modicon M340 + CANopen)

In this stage, certain machining operations must be performed not in absolute coordinates relative to the machine bed, but in **relative depth from the external surface of the workpiece**. To achieve this, the system utilizes a fully automated method relying solely on the capabilities of the **Modicon M340 PLC**, without additional probing sensors.

---

### 🛠️ Process Sequence

1. At the start of the machining cycle, the system uses the **product's serial number** to dynamically retrieve all relevant parameters from the **SQL database**, including:
   - The estimated surface position along the Z-axis,
   - Safety buffer distance,
   - Initial spindle speed and feedrate settings.

   These parameters are transmitted to the **Modicon M340 PLC via OPC server** and mapped into dedicated memory areas within the controller.  
   > 🧠 **No values are stored locally in the PLC** — all machining parameters are loaded in real time, ensuring traceability and full adaptability per product instance.

2. Using the received values, the **Z-axis spindle** performs a two-phase descent:
   - It rapidly moves to the **pre-contact level** (estimated surface minus safety zone),
   - Then enters **slow approach mode**, reducing vertical speed as it enters the safety buffer,  
     while the spindle ramps up to the defined **operating RPM** in preparation for surface detection.

3. When the **cutting tool contacts the workpiece**, a **sudden increase in motor current** is detected.

   This current spike is transmitted via **CANopen** from the drive to the Modicon M340, which uses it to:
   - Establish the **actual surface level** (Z-reference point),
   - Begin subsequent machining operations from this dynamically measured position.

---

### ⚙️ Tool Wear Monitoring and Adaptive Compensation

The system also leverages spindle current data to **estimate cutting tool wear**:

- As the tool wears down, the **spindle drive current increases** under identical cutting conditions.
- The system is configured to:
  - **Automatically compensate** minor wear by adjusting **RPM and feed rate**, within pre-approved safety limits;
  - Trigger a **tool wear alarm** if compensation limits are exceeded.

When wear thresholds are breached:
- The equipment switches to **service mode**;
- The system logs relevant data to the SQL database, including:
  - The measured wear event,
  - The tool's actual operating lifespan,
  - The associated product serial number and matrix ID — enabling both **technical traceability** and **financial analysis**.

---

### 🧩 Functional Block Logic – Tool Contact Detection

**RS_0 Trigger**  
Indicates that the Z-axis has reached the predefined safety threshold `Z_reached.Q`, which is retrieved from the SQL table for the current serial number. This event initiates the reduction of the vertical spindle speed along the Z-axis to the default feed rate.

**GE_INT Comparator**  
Compares the real-time spindle current value (received via CANopen) with a predefined threshold value (typically 10%–20% of the nominal cutting load).

**AND block 35 and TP block 36**  
These are responsible for generating a trigger pulse and committing the following variable assignments:

- `torque_A` — Torque setpoint for the PID controller (explained separately);
- `ATV32_A.TargetVelocity` — Spindle rotational speed for this segment of the toolpath;
- `position_A_1` — Reference zero position for relative motion calculations;
- `position_A_2` and `target_A` — Calculated toolpath segment positions;
- `A_PID_PARAM.out_sup` — Feedrate setpoint output for the PID controller;
- `Vent.Target_Velocity` — CANopen command to increase dust collector fan speed (+20% above nominal, short-time boost mode).


This approach enables **dynamic surface referencing**, **proactive wear detection**, and **closed-loop performance monitoring** — ensuring high machining accuracy and long-term process reliability even when surface conditions vary.

### 🧹 Dust Collection Logic

Each machining operation increments the counter `CTU_1` by 1. Once the counter reaches the threshold `PulseJetFreq`, logical latches `AND_5`, `AND_9`, and `AND_13` are enabled to pass the state of triggers `RS_8`, `RS_4`, and `RS_7`.

At any given time, only **one of the three RS triggers is active**, enabling rotation of the control signal between the three pulse valves. This design ensures more efficient cleaning of bag filter groups while reducing compressed air consumption per pulse.

The remaining logic covers **service modes**:

- **RED BUTTON LONG PRESS** — triggers a forced **PULSE JET** for all filter groups to prepare for dust bin emptying. It also activates a lockout timer to **block further pulses for two hours**, ensuring enough time for container replacement.

- **GREEN BUTTON LONG PRESS** — activates a forced **TURBO mode** of the dust collector fan, used during scheduled maintenance and cleaning procedures.
