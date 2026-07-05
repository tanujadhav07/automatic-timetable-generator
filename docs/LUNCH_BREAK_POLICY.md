# ☕ Lunch Break Policy - 12:00 to 13:00

## Overview

**Every class has a mandatory lunch break from 12:00 to 13:00 every day**, regardless of any other scheduling constraints.

---

## Implementation Details

### Time Configuration

```python
TIMESLOTS = [
    ("10:00 - 11:00", "lecture"),
    ("11:00 - 12:00", "lecture"),
    ("12:00 - 13:00", "lunch"),    ← RESERVED FOR LUNCH
    ("13:00 - 14:00", "lecture"),
    ("14:00 - 15:00", "lecture"),
    ("15:00 - 16:00", "lecture"),
    ("16:00 - 17:00", "lecture"),
]
```

### Enforcement Rules

The lunch break is **guaranteed** under ALL conditions:

✅ **Regular Days**
```
Normal timetable:
10:00-11:00: Lecture
11:00-12:00: Lecture
12:00-13:00: ☕ LUNCH BREAK (locked)
13:00-14:00: Lecture
...
```

✅ **Project Days** (Even full project days have lunch!)
```
Project Day:
10:00-11:00: Project Day
11:00-12:00: Project Day
12:00-13:00: ☕ LUNCH BREAK (overrides project day!)
13:00-14:00: Project Day
...
```

✅ **Lecture-Only Days**
```
Lecture-Only Day:
10:00-11:00: Lecture
11:00-12:00: Lecture
12:00-13:00: ☕ LUNCH BREAK (locked)
13:00-14:00: Lecture
...
```

✅ **Special Days** (T&P, Library, Experiential Learning)
```
Special Day:
10:00-11:00: Special Activity
11:00-12:00: Special Activity
12:00-13:00: ☕ LUNCH BREAK (locked)
13:00-14:00: Special Activity
...
```

---

## Code Implementation

### Priority Check (First Check in Loop)

```python
for slot_time, stype in timeslots:
    # ✅ LUNCH BREAK IS ALWAYS 12:00-13:00 (HIGHEST PRIORITY!)
    if slot_time == "12:00 - 13:00":
        timetable[cls][day][slot_time] = "Lunch Break"
        continue  # Skip all other checks
    
    # Then check project day, lecture-only day, etc.
    if day == project_day:
        timetable[cls][day][slot_time] = "Project Day"
        continue
    
    # ... other scheduling logic
```

### Why This Works

The lunch break check is placed **BEFORE all other scheduling logic**, ensuring:
- 🎯 No activities override lunch
- 🎯 No special days override lunch
- 🎯 No project days override lunch
- 🎯 Consistent across all classes
- 🎯 Consistent across all days

---

## Verification

### Test Coverage (4 Tests)

✅ **test_lunch_break_enforced_all_classes**
- Verifies 12:00-13:00 is "Lunch Break" for ALL classes
- Checks ALL days of the week
- Status: **PASSING**

✅ **test_lunch_break_no_activities_during_12_13**
- Ensures no teaching activities occur during lunch
- Verifies it's not a subject or class
- Status: **PASSING**

✅ **test_lunch_break_consistency**
- Runs timetable generation multiple times
- Confirms lunch is always there
- Status: **PASSING**

✅ **test_lunch_break_position**
- Verifies lunch is in the middle of the day
- Checks morning → lunch → afternoon sequence
- Status: **PASSING**

**Result: 4/4 tests passing ✅**

---

## Example Timetable (Class SE)

### Monday (Project Day - Special Case)
```
10:00-11:00: Project Day
11:00-12:00: Project Day
12:00-13:00: ☕ LUNCH BREAK  ← Even on project day!
13:00-14:00: Project Day
14:00-15:00: Project Day
15:00-16:00: Project Day
16:00-17:00: Project Day
```

### Tuesday (Regular Lecture Day)
```
10:00-11:00: S1 (T1)
11:00-12:00: S2 (T2)
12:00-13:00: ☕ LUNCH BREAK  ← Always locked
13:00-14:00: S3 (T3)
14:00-15:00: S1 (T1)
15:00-16:00: Practical (Lab1)
16:00-17:00: Practical (Lab1)
```

### Wednesday (Lecture-Only Day)
```
10:00-11:00: Library Hour
11:00-12:00: S1 (T1)
12:00-13:00: ☕ LUNCH BREAK  ← Always locked
13:00-14:00: S2 (T2)
14:00-15:00: S3 (T3)
15:00-16:00: Free
16:00-17:00: Free
```

---

## Benefits

| Benefit | Impact |
|---------|--------|
| **Health & Wellness** | Students get proper break time |
| **Compliance** | Meets academic standards |
| **Consistency** | Same break across all classes |
| **Predictability** | Always 12:00-13:00 |
| **Reliability** | Never overridden by other rules |

---

## Configuration

### To Change Lunch Time (if needed in future)

Modify `TIMESLOTS` in algorithm.py:

```python
# Current (RECOMMENDED):
TIMESLOTS = [
    ("10:00 - 11:00", "lecture"),
    ("11:00 - 12:00", "lecture"),
    ("12:00 - 13:00", "lunch"),    ← Change this
    # ...
]

# To move lunch to 13:00-14:00, change to:
TIMESLOTS = [
    ("10:00 - 11:00", "lecture"),
    ("11:00 - 12:00", "lecture"),
    ("12:00 - 13:00", "lecture"),
    ("13:00 - 14:00", "lunch"),    ← New lunch time
    # ...
]
```

### Then Update Priority Check

```python
# Change from:
if slot_time == "12:00 - 13:00":
    timetable[cls][day][slot_time] = "Lunch Break"

# To:
if slot_time == "13:00 - 14:00":  # New lunch time
    timetable[cls][day][slot_time] = "Lunch Break"
```

---

## Guarantees

✅ **100% Coverage**: Every class, every day has 12:00-13:00 lunch  
✅ **No Exceptions**: Not overridden by project day, special days, or activities  
✅ **Consistent**: Same across all classes  
✅ **Predictable**: Always at exactly 12:00-13:00  
✅ **Tested**: 4 comprehensive tests, all passing  

---

## Summary

The lunch break from **12:00 to 13:00** is a **protected, mandatory slot** in every timetable. No scheduling rules, special days, or project days can override it. This ensures consistent student break time across all classes and days of the week.

**Status**: ✅ **Fully Implemented & Tested**

---

## Related Documentation

- [TIMESLOTS Configuration](algorithm.py#L7)
- [Lunch Break Tests](tests/test_lunch_break.py)
- [Timetable Generation](algorithm.py#generate_timetable)
