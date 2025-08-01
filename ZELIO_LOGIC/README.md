## Control of a Mobile Water Heater for Winter Construction Work Using Zelio Logic

#### Task Description

During the finishing stage of house construction in winter, heaters are used to warm up the interior premises. For increased fire safety, a mobile system based on a water boiler is used. Coordination of system components is implemented with a Zelio Logic relay (Zelio Soft).

#### List of Actuators and Sensors

- Boiler air heater fan (three speeds)
- Circulation pump
- 3-phase solid-state relay for the boiler (heater)
- Boiler water temperature sensor
- Room temperature sensor
- Air temperature sensor after the heater

#### Functional Requirements

1. **PID room temperature control** — maintaining the set room air temperature using a PID regulator (implemented on Zelio Logic).
2. **Noise reduction of the fan** — the fan runs at minimum speed when the boiler temperature is normal, increasing speed only in case of coolant overheating.
3. **Maximum power limitation** — if the electrical network cannot supply nominal power, PWM regulation of the solid-state relay is implemented with a specified duty cycle.
4. **Safety** — emergency states (overheating, circulation failure) cause heating to stop and trigger a fault indication.

#### Zelio Logic I/O Structure

| Variable    | Type | Description                           |
| ----------- | ---- | ------------------------------------- |
| FAN_L       | DO   | Fan — low speed                       |
| FAN_M       | DO   | Fan — medium speed                    |
| FAN_H       | DO   | Fan — high speed                      |
| PUMP        | DO   | Circulation pump                      |
| HEATER_SSR  | DO   | Boiler solid-state relay (PWM)        |
| ALARM       | DO   | Overheat any T_BOILER/T_ROOM/T_OUTLET |
| T_BOILER    | AI   | Boiler temperature sensor             |
| T_ROOM      | AI   | Room temperature sensor               |
| T_FLOW      | AI   | Air Flow temperature sensor           |
| POWER_LIMIT | INT  | Maximum Power (limit)                 |

#### Operating Algorithm

1. The PID regulator forms the control action based on the room temperature.
2. The PWM regulator (as a macro) controls the heater's duty cycle according to the specified power limit.
3. Fan speed is selected depending on the boiler temperature:
   - Within normal range — minimum speed (FAN_L)
   - If the threshold is exceeded — medium/high speed (FAN_M/FAN_H)
4. Protection: in case of emergency (overheating by any of the three temperature sensors), the heater is switched off and a fault is indicated.

#### Project Files

- [BOILER_01.zm2](BOILER_01.zm2) — Zelio Soft project file for the boiler control system.
- [README.md](README.md) — Functional description.

All files are available directly in this repository and can be downloaded or opened using the standard GitHub interface.