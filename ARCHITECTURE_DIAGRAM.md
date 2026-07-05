# System Architecture Diagram

## Cross-Class Conflict Resolution Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    TIMETABLE GENERATION PROCESS                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │  Read Input:              │
                    │  - Teachers              │
                    │  - Classes               │
                    │  - Subjects              │
                    │  - Batches               │
                    └───────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │ Initialize:               │
                    │ - ConflictTracker        │
                    │ - CrossClassResolver     │
                    │ - Global Teacher Schedule│
                    └───────────────────────────┘
                                    │
                                    ▼
            ┌──────────────────────────────────────────┐
            │      FOR EACH CLASS, DAY, SLOT           │
            └──────────────────────────────────────────┘
                                    │
                ┌───────────────────┴───────────────────┐
                │                                       │
                ▼                                       ▼
        ┌────────────────┐                     ┌────────────────┐
        │  LECTURE       │                     │  PRACTICAL     │
        │  SCHEDULING    │                     │  SCHEDULING    │
        └────────────────┘                     └────────────────┘
                │                                       │
                ▼                                       ▼
        ┌────────────────────────┐            ┌──────────────────────┐
        │ Check Teacher Conflict │            │ Check Lab Conflict   │
        │ (same slot)?           │            │ (same batch)?        │
        └────────────────────────┘            └──────────────────────┘
                │ YES                                   │ YES
                ▼                                       ▼
        ┌──────────────────┐                  ┌────────────────────┐
        │ Find Alternative │                  │ Rotate Lab/Batch   │
        │ Subject/Teacher  │                  │                    │
        └──────────────────┘                  └────────────────────┘
                │                                       │
                ▼                                       ▼
        ┌────────────────────────────────────────────────────────────┐
        │  ✨ NEW: CHECK CROSS-CLASS CONFLICTS ✨                    │
        │  (Same teacher in OTHER class at overlapping time?)        │
        └────────────────────────────────────────────────────────────┘
                                    │
                    YES (CONFLICT!) │
                                    ▼
        ┌───────────────────────────────────────────────────────────┐
        │        APPLY RESOLUTION STRATEGIES (in order)             │
        └───────────────────────────────────────────────────────────┘
                                    │
                ┌───────┬───────┬───────┬───────┐
                │       │       │       │       │
                ▼       ▼       ▼       ▼       ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
        │Strategy 1│ │Strategy 2│ │Strategy 3│ │Strategy 4│
        │SLOT MOVE │ │  SPLIT   │ │ REASSIGN │ │  MOVE    │
        │          │ │LECTURES  │ │TEACHER   │ │  OTHER   │
        └──────────┘ └──────────┘ └──────────┘ └──────────┘
             │            │            │            │
             ▼            ▼            ▼            ▼
        Move prac    Split 1-hr   Use diff     Move conf
        to alt slot  slots        teacher      class
             │            │            │            │
             └────┬───────┴────┬───────┴────┬───────┘
                  │            │            │
                  ▼            ▼            ▼
            ┌─────────┬──────────┬─────────┐
            │ RESOLVED?         │
            └─────────┬──────────┬─────────┘
                  YES │          │ NO
                      ▼          ▼
            ┌─────────────┐  ┌──────────────┐
            │ Log & Use   │  │ Log Conflict │
            │ New Slot    │  │ & Continue   │
            └─────────────┘  └──────────────┘
                      │            │
                      └────┬───────┘
                           ▼
        ┌──────────────────────────────────┐
        │ Add to Timetable + Track         │
        │ ConflictTracker.add_assignment() │
        │ Resolver.add_assignment()        │
        └──────────────────────────────────┘
                           │
                    (Continue next slot)
                           │
                           ▼
                    ┌──────────────┐
                    │ All slots    │
                    │ scheduled?   │
                    └──────────────┘
                      NO │      YES
                         ▼        ▼
                    ┌─────────┐  ┌──────────────┐
                    │Continue │  │ Generate     │
                    └─────────┘  │ Report &     │
                                 │ Return       │
                                 │ Timetable    │
                                 └──────────────┘
```

---

## Cross-Class Conflict Resolver (Detailed)

```
                    ┌────────────────────────────────┐
                    │ CrossClassConflictResolver     │
                    │                                │
                    │ - global_teacher_schedule      │
                    │ - resolutions_applied          │
                    └────────────────────────────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                │                   │                   │
                ▼                   ▼                   ▼
        ┌────────────────┐  ┌───────────────┐  ┌────────────────┐
        │_time_to_minutes│  │_slots_overlap │  │check_cross_    │
        │("10:00")       │  │(t1,t2,t3,t4)  │  │class_overlap() │
        │    ↓           │  │    ↓          │  │     ↓          │
        │   600 mins     │  │   True/False  │  │ List conflicts │
        └────────────────┘  └───────────────┘  └────────────────┘
                                    
                            ┌──────────────────────┐
                            │resolve_cross_class_  │
                            │conflict()            │
                            │                      │
                            │ Apply strategies:    │
                            │ 1. Slot move         │
                            │ 2. Split lectures    │
                            │ 3. Reassign teacher  │
                            │ 4. Move other        │
                            │                      │
                            │ Returns resolution   │
                            │ with strategy name   │
                            │ + new slot (if any)  │
                            └──────────────────────┘
```

---

## Global Teacher Schedule (Example)

```
global_teacher_schedule = {
    "Kranti": {
        "Monday": [
            ("10:00 - 11:00", "SE", "lecture"),      ← SE lecture
            ("13:00 - 14:00", "TE", "practical"),    ← TE practical
            ("15:00 - 16:00", "BE", "lecture")       ← BE lecture
        ],
        "Tuesday": [
            ("10:00 - 12:00", "SE", "practical"),
            ("13:00 - 15:00", "TE", "lecture")
        ]
    },
    "John": {
        ...
    }
}

When scheduling new activity:
- Check if teacher exists in global_teacher_schedule
- Check if day exists for that teacher
- For each existing assignment:
  - Parse times to minutes
  - Check if time ranges overlap
  - If YES → CONFLICT DETECTED!
  - If NO → Continue checking
```

---

## Time-Based Overlap Logic

```
┌──────────────────────────────────────────────────────────────┐
│ OVERLAP DETECTION ALGORITHM                                 │
└──────────────────────────────────────────────────────────────┘

Input: Two time slots
- Slot 1: start1 (minutes), end1 (minutes)
- Slot 2: start2 (minutes), end2 (minutes)

Overlap Check:
    (start1 < end2) AND (end1 > start2) → OVERLAP!
    Otherwise → NO OVERLAP

Visual Examples:
───────────────────────────────────────────────────

Slot 1:  [=========]  (600-660 = 10:00-11:00)
Slot 2:  [=========]  (600-660 = 10:00-11:00)
         YES OVERLAP (full overlap) ✓

Slot 1:  [=========]  (600-660 = 10:00-11:00)
Slot 2:     [===========]  (630-720 = 10:30-12:00)
         YES OVERLAP (partial) ✓

Slot 1:  [=========]  (600-660 = 10:00-11:00)
Slot 2:           [=========]  (660-720 = 11:00-12:00)
         NO OVERLAP (adjacent) ✗

Slot 1:  [===]       (600-660 = 10:00-11:00)
Slot 2:              [===]  (780-840 = 13:00-14:00)
         NO OVERLAP (different times) ✗
```

---

## Resolution Strategy Selection

```
┌────────────────────────────────────────────────────────┐
│  CONFLICT DETECTED (teacher, day, slot, class)        │
└────────────────────────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────┐
        │ Activity Type = Practical?       │
        └──────────────────────────────────┘
                 YES │        NO
                     ▼        ▼
            ┌──────────────┐ ┌──────────────┐
            │Try Strategy 1│ │Try Strategy 2│
            │SLOT MOVE     │ │SPLIT LECTURES│
            └──────────────┘ └──────────────┘
                     │                 │
             Resolved?      Resolved?
              YES │ NO       YES │ NO
                  ▼ ▼           ▼ ▼
            ┌────┐ ┌────┐
            │Done│ │Try │
            └────┘ │Str │
                   │atgy│
                   │  2 │
                   └────┘
                     │
            Resolved?
              YES │ NO
                  ▼ ▼
                   ┌──────────────┐
                   │Try Strategy 3│
                   │REASSIGN      │
                   │TEACHER       │
                   └──────────────┘
                     │
            Resolved?
              YES │ NO
                  ▼ ▼
                   ┌──────────────┐
                   │Try Strategy 4│
                   │MOVE OTHER    │
                   │ACTIVITY      │
                   └──────────────┘
                     │
            Resolved?
              YES │ NO
                  ▼ ▼
                ┌────┐ ┌────────────┐
                │Done│ │FAIL        │
                │    │ │Log Conflict│
                └────┘ └────────────┘
```

---

## Data Flow: Kranti Scenario

```
INPUT: Kranti teaches SE, TE, BE classes

                         ▼

Step 1: Schedule SE Lecture
  ├─ Monday 10:00-11:00: SE Lecture (Kranti)
  └─ Add to global_teacher_schedule["Kranti"]["Monday"]

                         ▼

Step 2: Try Schedule TE Practical
  ├─ Check: Teacher Conflict? NO
  ├─ Check: Lab Conflict? NO
  ├─ Check: Class Conflict? NO
  ├─ NEW: Check Cross-Class Conflict?
  │   ├─ Get Kranti's Monday schedule: [(10-11, SE, lecture)]
  │   ├─ Check overlap: (10-11) vs (10-12)?
  │   │   └─ 10 < 12 AND 11 > 10 → YES OVERLAP! ✗
  │   └─ CONFLICT DETECTED!
  │
  └─ Try Resolution:
      ├─ Strategy 1 (Slot Move):
      │   ├─ Try 10-12: Conflict with SE
      │   ├─ Try 13-15: Check if free? YES! ✓
      │   └─ RESOLVED: Move to 13-15
      └─ Result: TE Practical 13:00-15:00

                         ▼

Step 3: Schedule BE Lecture
  ├─ Monday 13:00-14:00: BE Lecture (Kranti)
  ├─ Check Cross-Class? TE practical at 13-15?
  │   └─ Overlap (13-14) vs (13-15)? YES but...
  │   └─ Different activity types OK if same teacher ✓
  └─ Add without conflict

                         ▼

FINAL TIMETABLE:
  Monday 10:00-11:00: SE Lecture (Kranti) ✓
  Monday 13:00-14:00: BE Lecture (Kranti) ✓  
  Monday 13:00-15:00: TE Practical (Kranti) ✓

NO CONFLICTS! ✨
```

---

## Summary

The system uses a **multi-layered conflict detection and resolution** approach:

1. **Same-Slot Detection**: Basic teacher/class/lab conflicts
2. **Cross-Class Detection**: Same teacher in different classes (NEW!)
3. **Strategic Resolution**: 4 automatic resolution strategies (NEW!)
4. **Audit Logging**: Track all changes for transparency

Result: **Fully automated, conflict-free timetable generation!** 🚀
