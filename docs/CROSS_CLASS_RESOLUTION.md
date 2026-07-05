# Cross-Class Teacher Conflict Resolution 🎯

## Problem Statement

**Scenario**: Teacher Kranti has:
- **SE class**: Lecture from 10:00-11:00
- **TE class**: Practical from 10:00-12:00 (2-hour slot)

**Conflict**: At 10:00-11:00, Kranti cannot teach BOTH simultaneously!

---

## Advanced Resolution Strategies

### Strategy 1: Move Practical to Different 2-Hour Slot ✅

**When applicable**: Practical slot is flexible  
**How it works**: Attempt to reschedule the practical to an available 2-hour window

```
BEFORE (Conflict ❌):
Monday  10:00-11:00 | SE: Lecture (Kranti)
Monday  10:00-12:00 | TE: Practical (Kranti) ← CONFLICT!

AFTER (Strategy 1 ✅):
Monday  10:00-11:00 | SE: Lecture (Kranti)
Monday  13:00-15:00 | TE: Practical (Kranti) ← Moved to free slot
                       ↑ Check: No conflicts? YES → Assign here
```

**Available 2-hour slots**:
- 10:00-12:00
- 13:00-15:00  
- 15:00-17:00

**Algorithm**:
```python
for slot in ["10:00-12:00", "13:00-15:00", "15:00-17:00"]:
    if no_conflicts_for_teacher_in_slot(teacher, day, slot):
        return {"resolved": True, "new_slot": slot}
```

---

### Strategy 2: Split Lectures Across Multiple 1-Hour Slots ✅

**When applicable**: Activity is a lecture, not a practical  
**How it works**: Distribute lecture across available 1-hour slots

```
BEFORE (Conflict ❌):
Monday  10:00-11:00 | SE: Lecture (Kranti)
Monday  10:00-12:00 | BE: Lecture (Kranti) ← CONFLICT!

AFTER (Strategy 2 ✅):
Monday  10:00-11:00 | SE: Lecture (Kranti)
Monday  11:00-12:00 | BE: Lecture (Kranti) ← Moved to adjacent slot
                       ↑ No conflicts: YES → Assign here
```

**Available 1-hour slots**:
- 10:00-11:00
- 11:00-12:00
- 13:00-14:00
- 14:00-15:00
- 15:00-16:00
- 16:00-17:00

**Algorithm**:
```python
available_slots = []
for slot in ["10:00-11:00", "11:00-12:00", ...]:
    if no_conflicts_for_teacher(teacher, day, slot):
        available_slots.append(slot)

if len(available_slots) >= 2:
    return {"resolved": True, "slots": available_slots[:2]}
```

---

### Strategy 3: Reassign to Different Teacher ⚠️

**When applicable**: Strategies 1 & 2 fail  
**How it works**: Recommend reassigning the activity to a different teacher

```
BEFORE (Conflict ❌):
Monday  10:00-11:00 | SE: Lecture (Kranti)
Monday  13:00-14:00 | TE: Practical (Kranti)
Monday  14:00-15:00 | BE: Lecture (Kranti) ← CONFLICT with BE!

AFTER (Strategy 3 ⚠️):
Monday  10:00-11:00 | SE: Lecture (Kranti)
Monday  13:00-14:00 | TE: Practical (Kranti)
Monday  14:00-15:00 | BE: Lecture (Different Teacher)
                       ↑ Reassigned to avoid conflict
```

**Algorithm**:
```python
if strategy_1_failed and strategy_2_failed:
    available_teachers = [t for t in all_teachers 
                         if no_conflicts(t, day, slot)]
    if available_teachers:
        return {"resolved": True, "reassign_to": available_teachers[0]}
    else:
        return {"resolved": False, "reason": "No available teachers"}
```

---

### Strategy 4: Move Overlapping Activity Instead

**When applicable**: Other class's activity is more flexible  
**How it works**: Move the conflicting activity from another class instead

```
BEFORE (Conflict ❌):
Monday  10:00-11:00 | SE: Practical (Kranti)
Monday  10:00-11:00 | TE: Lecture (Kranti) ← CONFLICT!

AFTER (Strategy 4 ✅):
Monday  10:00-11:00 | SE: Practical (Kranti)
Monday  11:00-12:00 | TE: Lecture (Kranti) ← Moved TE lecture
                       ↑ TE lecture moved to avoid SE practical
```

---

## CrossClassConflictResolver Class

```python
class CrossClassConflictResolver:
    """Advanced cross-class conflict detection and resolution"""
    
    def check_cross_class_overlap(self, day, slot_start, slot_end, teacher, cls, activity_type):
        """
        Detect overlapping assignments in OTHER classes
        
        Returns:
            [(other_class, other_activity, other_slot_time, conflict_type), ...]
            conflict_type: "full_overlap" | "partial_overlap" | "adjacent"
        """
    
    def resolve_cross_class_conflict(self, day, slot_start, slot_end, teacher, cls, 
                                    activity_type, subject, all_classes, all_subjects):
        """
        Attempt to resolve conflict using strategies in order:
        1. Move practical to different slot
        2. Split lectures
        3. Reassign teacher
        4. Move other activity
        
        Returns:
            {
                'resolved': bool,
                'strategy': str,
                'reason': str,
                'new_slot': str (if applicable),
                'conflicting_classes': [str, ...]
            }
        """
```

---

## Implementation Details

### Overlap Detection Algorithm

```python
def check_overlap(slot_start_min, slot_end_min, other_start_min, other_end_min):
    """
    Check if two time slots overlap
    
    Examples:
    - 10:00-11:00 vs 11:00-12:00 → NO overlap (adjacent)
    - 10:00-12:00 vs 10:00-11:00 → YES overlap (partial)
    - 10:00-11:00 vs 10:00-11:00 → YES overlap (full)
    """
    return (slot_start_min < other_end_min) and (slot_end_min > other_start_min)
```

### Time Conversion

```python
def _time_to_minutes(time_str: "10:30") -> 630:
    """Convert 'HH:MM' to minutes since midnight for easy comparison"""
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes
```

### Global Teacher Schedule

```python
# Tracks: teacher -> day -> [(slot_time, class, activity_type), ...]
global_teacher_schedule = {
    "Kranti": {
        "Monday": [
            ("10:00 - 11:00", "SE", "lecture"),
            ("10:00 - 12:00", "TE", "practical"),  ← CONFLICT!
        ],
        "Tuesday": [...]
    },
    "John": {...}
}
```

---

## Example Resolution Flow

### Scenario: Kranti Teaching 3 Classes

```
Input:
- Monday 10:00-11:00: SE Lecture (Kranti)
- Monday 10:00-12:00: TE Practical (Kranti) ← Conflict!
- Monday 13:00-14:00: BE Lecture (Kranti)

Step 1: Check Cross-Class Overlap
└─ TE practical (10:00-12:00) overlaps with SE lecture (10:00-11:00)
   └─ Different classes? YES → Cross-class conflict detected!

Step 2: Try Strategy 1 (Move Practical)
├─ Try slot 13:00-15:00
│  └─ Check: Kranti free 13:00-15:00? NO (has BE lecture at 13:00-14:00)
├─ Try slot 15:00-17:00
│  └─ Check: Kranti free 15:00-17:00? YES!
└─ Resolution: MOVE TE practical from 10:00-12:00 to 15:00-17:00 ✅

Output:
- Monday 10:00-11:00: SE Lecture (Kranti) ✓
- Monday 13:00-14:00: BE Lecture (Kranti) ✓
- Monday 15:00-17:00: TE Practical (Kranti) ✓
           ↑ Automatically moved to resolve conflict!
```

---

## Test Cases

### Test 1: Two-Class Overlap → Move Practical

```python
def test_overlap_move_practical():
    # Kranti teaches SE (10-11) and TE practical (10-12)
    conflicts = resolver.check_cross_class_overlap(
        "Monday", "10:00", "12:00", "Kranti", "TE", "practical"
    )
    assert len(conflicts) == 1
    
    resolution = resolver.resolve_cross_class_conflict(...)
    assert resolution['strategy'] == 'slot_move'
    assert resolution['new_slot'] == '15:00 - 17:00'
    assert resolution['resolved'] == True
```

### Test 2: Multiple Overlaps → Split Lectures

```python
def test_multiple_overlaps_split_lectures():
    # Kranti has 3 lectures that all overlap
    resolution = resolver.resolve_cross_class_conflict(...)
    assert resolution['strategy'] == 'split_lectures'
    assert len(resolution['slots']) == 2
```

### Test 3: Cannot Resolve → Recommend Reassignment

```python
def test_cannot_resolve_recommend_reassignment():
    # All slots and strategies fail
    resolution = resolver.resolve_cross_class_conflict(...)
    assert resolution['resolved'] == False
    assert resolution['strategy'] == 'requires_reassignment'
```

---

## Configuration

Adjust resolution priority in **algorithm.py**:

```python
# Line ~X: Modify strategy order
RESOLUTION_STRATEGIES = [
    'slot_move',              # Try moving practical to different slot first
    'split_lectures',         # Then try splitting lectures
    'reassign_teacher',       # Then recommend reassignment
    'move_other_activity'     # Finally, move other activity
]
```

---

## Output Format

When cross-class conflict is detected and resolved:

```python
{
    'resolved': True,
    'strategy': 'slot_move',
    'reason': 'Move TE practical to 15:00-17:00 to avoid SE lecture conflict',
    'old_slot': '10:00 - 12:00',
    'new_slot': '15:00 - 17:00',
    'conflicting_classes': ['SE'],
    'teacher': 'Kranti',
    'class': 'TE',
    'activity_type': 'practical'
}
```

---

## Integration with Existing System

1. **ConflictTracker** now includes `CrossClassConflictResolver`
2. **generate_timetable()** checks for cross-class conflicts for practicals
3. **Timetable output** includes resolution notes (e.g., "[MOVED to 15:00-17:00]")

---

## Advantages

✅ **Automatic Resolution**: No manual conflict fixing  
✅ **Smart Strategies**: Multiple resolution approaches  
✅ **Teacher-Centric**: Tracks all teacher assignments globally  
✅ **Flexible**: Works with lectures, practicals, special activities  
✅ **Logged**: All resolutions tracked for audit  
✅ **Transparent**: Output shows what was moved/changed  

---

## Limitations & Future Work

⚠️ Current limitations:
- Single strategy resolution (picks first that works)
- Doesn't optimize for teacher preference
- Doesn't consider student schedule changes

🔮 Future enhancements:
- Multi-objective optimization (minimize changes)
- AI-based strategy selection
- Student conflict detection
- Lab/facility conflict integration

---

## Summary

Your timetable system can now handle **sophisticated cross-class teacher conflicts** like:

- Teacher A teaching multiple classes at overlapping times
- Practical slots conflicting with lectures
- Complex scheduling scenarios with 3+ classes

**All resolved automatically using intelligent strategies!** 🚀
