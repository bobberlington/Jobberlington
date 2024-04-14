base_chance = 0.01
expected_rolls = 1/base_chance
meter = True
if meter:
    chance_increase = (base_chance * 2) * base_chance
else:
    chance_increase = 0
max_rolls = 100
#Handle at 1037 runs
meter_cutoff = False
meter_cutoff_num = 90
ev = 0

total_chance = 1
for i in range(max_rolls):
    # Chance you got the drop chance off.
    if i > meter_cutoff_num and meter_cutoff:
        meter = False
    if meter:
        chance_success = (base_chance + (i * chance_increase))
    else:
        chance_success = base_chance
    ev += chance_success * total_chance
    # This is the chance that you didn't get the drop yet including all previous runs
    total_chance *= (1 - chance_success)


    print(f"Chance of getting it this time: {chance_success}")
    print(f"Chance I never got it yet: {total_chance}")
    print(f"EV: {ev}")

if meter or meter_cutoff:
    ev += 1
print("FINAL")
print(f"EV: {ev}")