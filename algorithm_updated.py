import random
from collections import defaultdict

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

TIMESLOTS = [
    ("10:00 - 11:00", "lecture"),
    ("11:00 - 12:00", "lecture"),
    ("12:00 - 13:00", "lunch"),
    ("13:00 - 14:00", "lecture"),
    ("14:00 - 15:00", "lecture"),
    ("15:00 - 16:00", "lecture"),
    ("16:00 - 17:00", "lecture"),
]

# Default fixed practical slots per class (pairs of slots merged into 2-hour practicals)
PRACTICAL_SLOTS = {
    "SE": ["10:00 - 11:00", "11:00 - 12:00"],
    "TE": ["13:00 - 14:00", "14:00 - 15:00"],
    "BE": ["15:00 - 16:00", "16:00 - 17:00"],
}

# Cross-class conflict resolution strategies
class CrossClassConflictResolver:
    """Detect and resolve teacher conflicts across multiple classes
    
    Handles scenarios like:
    - Teacher 'Kranti' has SE lecture 10-11 AND TE practical 10-12 (OVERLAP!)
    
    Resolution strategies:
    1. Move practical to alternative 2-hour slot
    2. Split lectures across available 1-hour slots
    3. Reassign to different teacher
    4. Move overlapping activity in another class
    """
    
    def __init__(self):
        # Track all assignments: teacher -> day -> list of (slot_time, class, activity_type, details)
        self.global_teacher_schedule = defaultdict(lambda: defaultdict(list))
        # Track resolutions applied
        self.resolutions_applied = []
    
    def _time_to_minutes(self, time_str):
        """Convert '10:00' or '10:00 - 11:00' to minutes since midnight
        
        Examples:
        >>> _time_to_minutes('10:00')
        600
        >>> _time_to_minutes('10:30')
        630
        """
        if ' - ' in time_str:
            time_str = time_str.split(' - ')[0]
        try:
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        except:
            return 0
    
    def _slots_overlap(self, slot1_start_min, slot1_end_min, slot2_start_min, slot2_end_min):
        """Check if two time slots overlap
        
        Examples:
        - 10:00-11:00 vs 11:00-12:00 → False (adjacent)
        - 10:00-12:00 vs 10:30-11:30 → True (partial overlap)
        - 10:00-11:00 vs 10:00-11:00 → True (exact overlap)
        """
        return (slot1_start_min < slot2_end_min) and (slot1_end_min > slot2_start_min)
    
    def check_cross_class_overlap(self, day, slot_str, teacher, cls, activity_type):
        """Check if teacher has conflicting assignments in OTHER classes
        
        Returns:
            List of dicts: [{'class': str, 'activity': str, 'slot': str, 'type': str}, ...]
            type: 'full' | 'partial'
        """
        # Parse slot times
        if ' - ' in slot_str:
            slot_start_time, slot_end_time = slot_str.split(' - ')
        else:
            slot_start_time = slot_str
            # Assume 1-hour if not specified
            start_min = self._time_to_minutes(slot_start_time)
            slot_end_time = f"{start_min // 60 + 1}:00"
        
        slot_start_min = self._time_to_minutes(slot_start_time)
        slot_end_min = self._time_to_minutes(slot_end_time)
        
        conflicts = []
        
        # Check all other classes for same teacher
        if teacher in self.global_teacher_schedule:
            if day in self.global_teacher_schedule[teacher]:
                for other_slot, other_class, other_activity, _ in self.global_teacher_schedule[teacher][day]:
                    # Skip same class
                    if other_class == cls:
                        continue
                    
                    # Parse other slot
                    if ' - ' in other_slot:
                        other_start_time, other_end_time = other_slot.split(' - ')
                    else:
                        other_start_time = other_slot
                        other_start_min = self._time_to_minutes(other_start_time)
                        other_end_min = other_start_min + 60
                    
                    other_start_min = self._time_to_minutes(other_start_time)
                    other_end_min = self._time_to_minutes(other_end_time)
                    
                    # Check overlap
                    if self._slots_overlap(slot_start_min, slot_end_min, other_start_min, other_end_min):
                        overlap_type = 'full' if (slot_start_min == other_start_min and slot_end_min == other_end_min) else 'partial'
                        conflicts.append({
                            'class': other_class,
                            'activity': other_activity,
                            'slot': other_slot,
                            'type': overlap_type
                        })
        
        return conflicts
    
    def resolve_cross_class_conflict(self, day, slot_str, teacher, cls, activity_type, 
                                    available_slots=None, all_teachers=None):
        """Resolve conflict using strategies in priority order
        
        Strategies:
        1. SLOT_MOVE: Move practical to alternative 2-hour slot
        2. SPLIT_LECTURES: Split 1-hour lectures across available slots
        3. REASSIGN_TEACHER: Use different teacher for this activity
        4. MOVE_OTHER: Move conflicting activity in other class
        
        Returns:
            {
                'resolved': bool,
                'strategy': str,  # 'slot_move' | 'split_lectures' | 'reassign_teacher' | 'move_other'
                'reason': str,
                'new_slot': str (if applicable),
                'recommended_teacher': str (if applicable)
            }
        """
        if available_slots is None:
            available_slots = ["10:00 - 11:00", "11:00 - 12:00", "13:00 - 14:00", 
                             "14:00 - 15:00", "15:00 - 16:00", "16:00 - 17:00"]
        
        conflicts = self.check_cross_class_overlap(day, slot_str, teacher, cls, activity_type)
        
        if not conflicts:
            return {'resolved': True, 'strategy': 'no_conflict', 'reason': 'No conflicts detected'}
        
        # Strategy 1: SLOT_MOVE (for 2-hour practicals)
        if activity_type == 'practical' and ' - ' in slot_str:
            start_time, end_time = slot_str.split(' - ')
            slot_duration_min = self._time_to_minutes(end_time) - self._time_to_minutes(start_time)
            
            # Try alternative 2-hour slots
            alternative_slots = [
                "10:00 - 12:00",
                "13:00 - 15:00",
                "15:00 - 17:00"
            ]
            
            for alt_slot in alternative_slots:
                if alt_slot == slot_str:
                    continue
                # Check if teacher is free in this slot
                alt_conflicts = self.check_cross_class_overlap(day, alt_slot, teacher, cls, activity_type)
                if not alt_conflicts:
                    self.resolutions_applied.append({
                        'type': 'slot_move',
                        'day': day,
                        'class': cls,
                        'teacher': teacher,
                        'old_slot': slot_str,
                        'new_slot': alt_slot
                    })
                    return {
                        'resolved': True,
                        'strategy': 'slot_move',
                        'reason': f'Move {activity_type} to {alt_slot} to avoid conflict with {[c["class"] for c in conflicts]}',
                        'old_slot': slot_str,
                        'new_slot': alt_slot
                    }
        
        # Strategy 2: SPLIT_LECTURES (for 1-hour lectures)
        if activity_type == 'lecture':
            free_slots = []
            for slot in available_slots:
                if ' - ' not in slot:
                    continue
                slot_conflicts = self.check_cross_class_overlap(day, slot, teacher, cls, activity_type)
                if not slot_conflicts:
                    free_slots.append(slot)
            
            if len(free_slots) > 0:
                self.resolutions_applied.append({
                    'type': 'split_lectures',
                    'day': day,
                    'class': cls,
                    'teacher': teacher,
                    'old_slot': slot_str,
                    'new_slots': free_slots[:2]
                })
                return {
                    'resolved': True,
                    'strategy': 'split_lectures',
                    'reason': f'Distribute lecture across {free_slots[:2]}',
                    'slots': free_slots[:2]
                }
        
        # Strategy 3: REASSIGN_TEACHER
        if all_teachers:
            available_teachers = [t for t in all_teachers if t != teacher]
            return {
                'resolved': False,  # Can't auto-resolve, needs approval
                'strategy': 'reassign_teacher',
                'reason': f'Recommend assigning to different teacher: {available_teachers[:2] if available_teachers else "None available"}',
                'recommended_teachers': available_teachers[:2] if available_teachers else []
            }
        
        # Strategy 4: MOVE_OTHER (placeholder)
        return {
            'resolved': False,
            'strategy': 'manual_review',
            'reason': f'Cannot auto-resolve. Conflicting classes: {[c["class"] for c in conflicts]}'
        }
    
    def add_assignment(self, day, slot_time, cls, teacher, activity_type, details=""):
        """Record teacher assignment in global schedule"""
        self.global_teacher_schedule[teacher][day].append((slot_time, cls, activity_type, details))
    
    def generate_conflict_report(self):
        """Generate summary of all conflicts and resolutions"""
        return {
            'resolutions_applied': self.resolutions_applied,
            'count': len(self.resolutions_applied)
        }


# Conflict tracking structures
class ConflictTracker:
    """Track and resolve scheduling conflicts"""
    def __init__(self):
        # (day, slot_time) -> [(class, teacher), ...]
        self.teacher_assignments = defaultdict(list)
        # (day, slot_time, lab) -> [batch, ...]
        self.lab_assignments = defaultdict(list)
        # (day, slot_time, class) -> [batch, ...]
        self.class_assignments = defaultdict(list)
        # Cross-class conflict resolver
        self.cross_class_resolver = CrossClassConflictResolver()
        self.conflicts = {"teacher": [], "lab": [], "class": [], "cross_class": []}
    
    def has_teacher_conflict(self, day, slot_time, teacher_short):
        """Check if teacher is already assigned at this time"""
        key = (day, slot_time)
        return any(t == teacher_short for _, t in self.teacher_assignments[key])
    
    def has_lab_conflict(self, day, slot_time, lab, batch):
        """Check if lab is already assigned to different batch at this time"""
        key = (day, slot_time, lab)
        return batch not in self.lab_assignments[key] and len(self.lab_assignments[key]) > 0
    
    def has_class_conflict(self, day, slot_time, cls):
        """Check if class already has an assignment at this time"""
        key = (day, slot_time, cls)
        return len(self.class_assignments[key]) > 0
    
    def add_assignment(self, day, slot_time, cls, batch, teacher, lab=None, activity_type='lecture'):
        """Record an assignment and track in global schedule"""
        if not (day == "Lunch" or "Project" in str(teacher) or "Library" in str(teacher)):
            # Track teacher
            self.teacher_assignments[(day, slot_time)].append((cls, teacher))
            # Track class
            self.class_assignments[(day, slot_time, cls)].append(batch)
            # Track lab if provided
            if lab:
                self.lab_assignments[(day, slot_time, lab)].append(batch)
        
        # Also track in cross-class resolver
        self.cross_class_resolver.add_assignment(day, slot_time, cls, teacher, activity_type)
    
    def check_cross_class_conflict(self, day, slot_time, cls, teacher, activity_type='lecture'):
        """Check for cross-class teacher conflicts"""
        return self.cross_class_resolver.check_cross_class_overlap(day, slot_time, teacher, cls, activity_type)
    
    def resolve_cross_class_conflict(self, day, slot_time, cls, teacher, activity_type='lecture', 
                                     available_slots=None, all_teachers=None):
        """Try to resolve cross-class conflict"""
        return self.cross_class_resolver.resolve_cross_class_conflict(
            day, slot_time, teacher, cls, activity_type, available_slots, all_teachers
        )
    
    def report_conflicts(self):
        """Generate conflict report"""
        return self.conflicts


def validate_inputs_and_build_maps(classes, teachers, optional_subjects):
    """Build subject-teacher mappings and optional subject map"""
    subject_teacher = {}
    teacher_fullname_map = {}
    teacher_to_subjects = {}  # Track all subjects per teacher

    for t in teachers:
        for subj in t["subjects"]:
            subject_teacher[subj] = t["name"]   # short name for timetable
        teacher_fullname_map[t["name"]] = t.get("fullName", t["name"])
        teacher_to_subjects[t["name"]] = t["subjects"]

    # Optional subjects mapping: (class, batch, subject) → info
    optional_map = {}
    for opt in optional_subjects:
        optional_map[(opt["className"], opt["batch"], opt["subject"])] = opt

    return {
        "subject_teacher": subject_teacher,
        "teacher_fullname_map": teacher_fullname_map,
        "optional_map": optional_map,
        "teacher_to_subjects": teacher_to_subjects
    }, None


def generate_weekly_specials(fixed_project_day=None):
    """Assign special days (project, lecture-only, library, T&P, experiential)

    Can be used to generate a full set of specials for each class, but the
    *project day* is often shared across all classes. When a
    ``fixed_project_day`` is provided, that day will be used instead of
    picking a random one. This lets the caller ensure a single common
    project day while still allowing the other special days to vary by
    class.

    Returns: (project_day, lecture_day, library_day, tp_day, exp_day)
    """
    # choose a project day globally if not already fixed
    project_day = fixed_project_day if fixed_project_day is not None else random.choice(DAYS)
    other_days = [d for d in DAYS if d != project_day]
    lecture_day = random.choice(other_days)
    remaining_days = [d for d in other_days if d != lecture_day]
    library_day = random.choice(remaining_days)
    tp_day = random.choice([d for d in remaining_days if d != library_day])
    exp_day = random.choice([d for d in remaining_days if d not in [library_day, tp_day]])
    return project_day, lecture_day, library_day, tp_day, exp_day


def generate_timetable(classes, teachers, subjects, timeslots, batches, labs, maps):
    """Generate conflict-free timetable with cross-class conflict resolution
    
    Now includes intelligent handling of teacher overlaps across classes.
    Example: Teacher 'Kranti' with SE lecture 10-11 AND TE practical 10-12 
    will be auto-resolved by moving practical to 15-17.
    """
    subject_teacher = maps["subject_teacher"]
    optional_map = maps["optional_map"]
    teacher_to_subjects = maps.get("teacher_to_subjects", {})

    # Empty timetable structure
    timetable = {cls: {day: {} for day in DAYS} for cls in classes}
    # choose a single project day shared across all classes
    project_day_global = random.choice(DAYS)
    # generate other special days for each class, but pass in the fixed
    # project day so it doesn't vary per-class
    specials = {cls: generate_weekly_specials(fixed_project_day=project_day_global) for cls in classes}
    
    # Initialize conflict tracker (with cross-class resolution)
    conflict_tracker = ConflictTracker()
    all_teachers = list(set(subject_teacher.values()))

    for cls in classes:
        # override project_day with the global one for clarity (although
        # specials was generated with the same value already)
        project_day, lecture_day, library_day, tp_day, exp_day = specials[cls]
        project_day = project_day_global

        # Select 4 days for practicals, excluding project and lecture-only days
        practical_days = [d for d in DAYS if d not in [project_day, lecture_day]][:4]

        # Track assigned practicals for each batch (avoid repeats across the week)
        assigned_practicals = {batch: set() for batch in batches.get(cls, [])}
        
        # Track teacher workload: (day, teacher) -> count
        teacher_workload = defaultdict(int)
        # Track labs usage across all classes
        lab_usage = defaultdict(lambda: defaultdict(set))  # (day, slot_time, lab) -> set of batches

        for day in DAYS:
            used_lectures = set()
            lectures_per_teacher = defaultdict(int)  # Track lectures per teacher per day

            for slot_time, stype in timeslots:

                # Full project day off
                if day == project_day:
                    timetable[cls][day][slot_time] = "Project Day"
                    continue

                # Full lecture-only day: schedule only lectures and lunch
                if day == lecture_day:
                    if slot_time == "12:00 - 13:00":
                        timetable[cls][day][slot_time] = "Lunch Break"
                    elif stype == "lecture":
                        if subjects[cls].get("lectures"):
                            remaining = [s for s in subjects[cls]["lectures"] if s not in used_lectures]
                            if not remaining:
                                used_lectures.clear()
                                remaining = subjects[cls]["lectures"]
                            subj = random.choice(remaining)
                            used_lectures.add(subj)
                            teacher = subject_teacher.get(subj, "TBD")
                            
                            # Check teacher conflict - balance workload
                            while conflict_tracker.has_teacher_conflict(day, slot_time, teacher) and len(remaining) > 1:
                                remaining.remove(subj)
                                subj = random.choice(remaining)
                                teacher = subject_teacher.get(subj, "TBD")
                            
                            # Check cross-class conflicts
                            cross_conflicts = conflict_tracker.check_cross_class_conflict(day, slot_time, cls, teacher, 'lecture')
                            if cross_conflicts:
                                resolution = conflict_tracker.resolve_cross_class_conflict(
                                    day, slot_time, cls, teacher, 'lecture', timeslots, all_teachers
                                )
                                if resolution.get('resolved') and resolution.get('new_slot'):
                                    slot_time = resolution['new_slot']
                            
                            timetable[cls][day][slot_time] = f"{subj} ({teacher})"
                            conflict_tracker.add_assignment(day, slot_time, cls, "lecture", teacher, activity_type='lecture')
                            lectures_per_teacher[teacher] += 1
                        else:
                            timetable[cls][day][slot_time] = "Free"
                    else:
                        timetable[cls][day][slot_time] = "Free"
                    continue

                # Lunch break always fixed
                if slot_time == "12:00 - 13:00":
                    timetable[cls][day][slot_time] = "Lunch Break"
                    continue

                # Practical slots (2-hour merged) only on chosen practical_days
                if day in practical_days and slot_time in PRACTICAL_SLOTS.get(cls, []):
                    # Only schedule practical in the first slot of the pair
                    if slot_time == PRACTICAL_SLOTS[cls][0]:
                        assignments = []

                        for i, batch in enumerate(batches.get(cls, [])):
                            lab = labs[i % len(labs)] if labs else "Lab(0)"
                            
                            # Check for optional subject practicals
                            optional_subject = None
                            for key, opt in optional_map.items():
                                if key[0] == cls and key[1] == batch:
                                    optional_subject = opt
                                    break

                            if optional_subject:
                                subj = optional_subject["subject"]
                                teacher_short = subject_teacher.get(subj, "TBD")
                                
                                # Check cross-class conflicts for practicals (HIGH PRIORITY)
                                cross_conflicts = conflict_tracker.check_cross_class_conflict(day, slot_time, cls, teacher_short, 'practical')
                                if cross_conflicts:
                                    resolution = conflict_tracker.resolve_cross_class_conflict(
                                        day, slot_time, cls, teacher_short, 'practical', None, all_teachers
                                    )
                                    if resolution.get('resolved') and resolution.get('new_slot'):
                                        slot_time = resolution['new_slot']
                                
                                # Resolve lab conflict by rotating labs
                                attempt = 0
                                while conflict_tracker.has_lab_conflict(day, slot_time, lab, batch) and attempt < len(labs):
                                    lab = labs[(i + attempt + 1) % len(labs)]
                                    attempt += 1
                                
                                assignments.append(f"{batch}: {subj} ({teacher_short}) in {lab}")
                                conflict_tracker.add_assignment(day, slot_time, cls, batch, teacher_short, lab, activity_type='practical')
                                assigned_practicals[batch].add(subj)
                                lab_usage[(day, slot_time, lab)][batch].add(subj)
                            elif subjects[cls].get("practicals"):
                                remaining = [s for s in subjects[cls]["practicals"] if s not in assigned_practicals[batch]]
                                if remaining:
                                    subj = random.choice(remaining)
                                    assigned_practicals[batch].add(subj)
                                    teacher_short = subject_teacher.get(subj, "TBD")
                                    
                                    # Check cross-class conflicts
                                    cross_conflicts = conflict_tracker.check_cross_class_conflict(day, slot_time, cls, teacher_short, 'practical')
                                    if cross_conflicts:
                                        resolution = conflict_tracker.resolve_cross_class_conflict(
                                            day, slot_time, cls, teacher_short, 'practical', None, all_teachers
                                        )
                                        if resolution.get('resolved') and resolution.get('new_slot'):
                                            slot_time = resolution['new_slot']
                                    
                                    # Resolve lab conflict
                                    attempt = 0
                                    while conflict_tracker.has_lab_conflict(day, slot_time, lab, batch) and attempt < len(labs):
                                        lab = labs[(i + attempt + 1) % len(labs)]
                                        attempt += 1
                                    
                                    assignments.append(f"{batch}: {subj} ({teacher_short}) in {lab}")
                                    conflict_tracker.add_assignment(day, slot_time, cls, batch, teacher_short, lab, activity_type='practical')
                                    lab_usage[(day, slot_time, lab)][batch].add(subj)
                                else:
                                    # All practicals already assigned once — reuse one (allow repeats)
                                    subj = random.choice(subjects[cls]["practicals"])
                                    assigned_practicals[batch].add(subj)
                                    teacher_short = subject_teacher.get(subj, "TBD")
                                    
                                    # Check cross-class conflicts
                                    cross_conflicts = conflict_tracker.check_cross_class_conflict(day, slot_time, cls, teacher_short, 'practical')
                                    if cross_conflicts:
                                        resolution = conflict_tracker.resolve_cross_class_conflict(
                                            day, slot_time, cls, teacher_short, 'practical', None, all_teachers
                                        )
                                        if resolution.get('resolved') and resolution.get('new_slot'):
                                            slot_time = resolution['new_slot']
                                    
                                    # Resolve lab conflict
                                    attempt = 0
                                    while conflict_tracker.has_lab_conflict(day, slot_time, lab, batch) and attempt < len(labs):
                                        lab = labs[(i + attempt + 1) % len(labs)]
                                        attempt += 1
                                    
                                    assignments.append(f"{batch}: {subj} ({teacher_short}) in {lab}")
                                    conflict_tracker.add_assignment(day, slot_time, cls, batch, teacher_short, lab, activity_type='practical')
                                    lab_usage[(day, slot_time, lab)][batch].add(subj)
                            else:
                                # No practicals defined: show a generic practical placeholder text
                                assignments.append(f"{batch}: Practical (TBD) in {lab}")

                        timetable[cls][day][slot_time] = " / ".join(assignments)
                        # Only mark the second slot as merged when there are real practicals
                        has_defined_practicals = bool(subjects[cls].get("practicals")) or any(k[0] == cls for k in optional_map.keys())
                        if has_defined_practicals:
                            # Mark the second slot as merged so it's not used separately
                            timetable[cls][day][PRACTICAL_SLOTS[cls][1]] = "MERGED"
                    # skip the second slot of the practical pair
                    elif slot_time == PRACTICAL_SLOTS[cls][1]:
                        continue
                    continue

                # Special activities
                if slot_time == "10:00 - 11:00" and day == library_day:
                    timetable[cls][day][slot_time] = "Library Hour"
                    continue
                if slot_time == "13:00 - 14:00" and day == tp_day:
                    timetable[cls][day][slot_time] = "T&P Hour"
                    continue
                if slot_time == "15:00 - 16:00" and day == exp_day:
                    timetable[cls][day][slot_time] = "Experiential Learning"
                    continue

                # Regular lectures (fair distribution across subjects, no teacher conflicts)
                if subjects[cls].get("lectures"):
                    remaining = [s for s in subjects[cls]["lectures"] if s not in used_lectures]
                    if not remaining:
                        used_lectures.clear()
                        remaining = subjects[cls]["lectures"]
                    
                    # Try to find a subject whose teacher is not overbooked
                    subj = None
                    for attempt_subj in remaining:
                        attempt_teacher = subject_teacher.get(attempt_subj, "TBD")
                        # Check if teacher already has 3+ lectures today
                        if lectures_per_teacher[attempt_teacher] < 3:
                            subj = attempt_subj
                            break
                    
                    if subj is None:
                        # Fallback: just pick any remaining
                        subj = random.choice(remaining)
                    
                    used_lectures.add(subj)
                    teacher = subject_teacher.get(subj, "TBD")
                    
                    # Final check: if teacher still conflicts, find alternative
                    if conflict_tracker.has_teacher_conflict(day, slot_time, teacher):
                        # Try other remaining subjects
                        for alt_subj in remaining:
                            alt_teacher = subject_teacher.get(alt_subj, "TBD")
                            if not conflict_tracker.has_teacher_conflict(day, slot_time, alt_teacher):
                                subj = alt_subj
                                teacher = alt_teacher
                                break
                    
                    # Check cross-class conflicts
                    cross_conflicts = conflict_tracker.check_cross_class_conflict(day, slot_time, cls, teacher, 'lecture')
                    if cross_conflicts:
                        resolution = conflict_tracker.resolve_cross_class_conflict(
                            day, slot_time, cls, teacher, 'lecture', 
                            [(t[0], t[1]) for t in timeslots], all_teachers
                        )
                        if resolution.get('resolved') and resolution.get('new_slot'):
                            slot_time = resolution['new_slot']
                    
                    timetable[cls][day][slot_time] = f"{subj} ({teacher})"
                    conflict_tracker.add_assignment(day, slot_time, cls, "lecture", teacher, activity_type='lecture')
                    lectures_per_teacher[teacher] += 1
                    teacher_workload[(day, teacher)] += 1
                else:
                    timetable[cls][day][slot_time] = "Free"

    return timetable
