# Fleet Maintenance Policy & Thresholds

Synthetic operating thresholds used by the AI fleet manager to prioritize work.

## Fuel and Charge Thresholds

Internal-combustion vehicles below 25% fuel should be flagged for refueling
before their next dispatch; below 10% is urgent and the vehicle should not be
assigned a long route. Electric vehicles below 20% state of charge should be
scheduled for charging within two hours; below 10% is urgent. These thresholds
exist to prevent stranded-vehicle incidents that disrupt delivery SLAs.

## Battery Health (EV)

Electric-vehicle state of health (SOH) below 70% indicates meaningful capacity
loss and should be logged for battery diagnostics; below 60% warrants planning
for battery service or vehicle rotation out of long-range routes. SOH is distinct
from state of charge: a fully charged but degraded battery still delivers reduced
range.

## Low-Voltage (12V) Battery

A 12V battery resting voltage below 12.2V suggests a discharged or aging battery
that can cause no-start conditions, even on EVs (which rely on the 12V system for
electronics). Flag any vehicle below 12.2V for a battery load test.

## Maintenance Prioritization

Prioritize in this order: (1) active high-severity safety codes such as ABS/ESC
faults, (2) active engine misfires, (3) urgent fuel/charge levels, (4)
medium-severity emissions/thermostat codes, (5) degraded battery health. Always
group multiple issues on the same vehicle into a single service visit.
