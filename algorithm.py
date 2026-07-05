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

# Three distinct timing groups for classes to avoid conflicts
# Group 1: Morning practical (10-12) + Lunch 12-13
# Group 2: Mid-afternoon practical (13-15) + Lunch 12-13
# Group 3: Late afternoon practical (15-17) + Lunch 13-14
# NOTE: Group 2 (13-15) is used for classes with unique teachers or when only one class is scheduled.
CLASS_TIMING_GROUPS = {
    "Group1": ["SE"],  # Morning practical slots (10:00 - 12:00)
    "Group2": ["BE"],  # Mid-afternoon practical slots (13:00 - 15:00)
    "Group3": ["TE"],  # Late afternoon practical slots (15:00 - 17:00)
}

# Practical slots based on timing groups
PRACTICAL_SLOTS = {
    "Group1": ["10:00 - 11:00", "11:00 - 12:00"],  # Morning practical
    "Group2": ["13:00 - 14:00", "14:00 - 15:00"],  # Mid-afternoon practical
    "Group3": ["15:00 - 16:00", "16:00 - 17:00"],  # Late afternoon practical
}

# Lunch slot assignment based on timing group
LUNCH_SLOTS = {
    "Group1": "12:00 - 13:00",  # Morning classes get standard lunch
    "Group2": "12:00 - 13:00",  # Mid-afternoon classes get standard lunch
    "Group3": "13:00 - 14:00",  # Afternoon classes get shifted lunch
}

# Define which slot options have gaps between them
# Group 1 (10-12) and Group 3 (15-17) have a gap
SLOT_GAP_MATRIX = {
    "Group1": {"Group3"},  # Group1 has gap with Group3
    "Group2": set(),       # Group2 is adjacent to both
    "Group3": {"Group1"},  # Group3 has gap with Group1
}

# Helper function to get class timing group
def get_class_timing_group(cls):
    for group, classes in CLASS_TIMING_GROUPS.items():
        if cls in classes:
            return group
    return "Group1"  # Default to Group1

# Helper function to get practical slots for class
def get_practical_slots(cls):
    group = get_class_timing_group(cls)
    return PRACTICAL_SLOTS[group]

# Helper function to get lunch slot for class
def get_lunch_slot(cls):
    group = get_class_timing_group(cls)
    return LUNCH_SLOTS[group]
    
# Helper function to check if two timing groups have consecutive practical slots
def are_practical_slots_consecutive(group1, group2):
    """Check if practical slots of two groups are consecutive (no gap between them)
    
    Returns True if slots are consecutive (BAD - causes teacher conflicts)
    Returns False if there's a gap between slots (GOOD - avoids conflicts)
    
    Group1: 10-12, Group2: 15-17
    - 13-15 is ALWAYS a lecture gap now.
    """
    if group1 == group2:
        return True # Same timing is always consecutive/overlapping
    
    # Use the gap matrix - if group2 is in group1's gap set, they're NOT consecutive
    if group2 in SLOT_GAP_MATRIX.get(group1, set()):
        return False  # Has gap - good!
    
    return True

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
        
        Enhanced detection with stricter overlap checking
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
                    
                    # Enhanced overlap detection - ANY overlap is a conflict
                    if self._slots_overlap(slot_start_min, slot_end_min, other_start_min, other_end_min):
                        overlap_type = 'full' if (slot_start_min == other_start_min and slot_end_min == other_end_min) else 'partial'
                        conflicts.append({
                            'class': other_class,
                            'activity': other_activity,
                            'slot': other_slot,
                            'type': overlap_type,
                            'severity': 'high' if overlap_type == 'full' else 'medium'
                        })
        
        return conflicts

    def resolve_cross_class_conflict(self, day, slot_str, teacher, cls, activity_type,
                                     available_slots=None, all_teachers=None):
        """Enhanced conflict resolution with multiple strategies"""
        conflicts = self.check_cross_class_overlap(day, slot_str, teacher, cls, activity_type)
        if not conflicts:
            return {'resolved': True, 'strategy': 'no_conflict', 'reason': 'No conflicts detected'}

        # Strategy 1: Try all alternative teachers for this slot
        if all_teachers:
            for alt_teacher in all_teachers:
                if alt_teacher == teacher or alt_teacher == "TBD":
                    continue
                alt_conflicts = self.check_cross_class_overlap(day, slot_str, alt_teacher, cls, activity_type)
                if not alt_conflicts:
                    self.resolutions_applied.append({
                        'type': 'teacher_reassign',
                        'day': day,
                        'class': cls,
                        'original_teacher': teacher,
                        'new_teacher': alt_teacher
                    })
                    return {
                        'resolved': True,
                        'strategy': 'teacher_reassign',
                        'reason': f'Reassigned from {teacher} to {alt_teacher}',
                        'new_teacher': alt_teacher
                    }

        # Strategy 2: Try alternate slots for the same teacher
        if available_slots:
            for alt_slot in available_slots:
                if alt_slot == slot_str:
                    continue
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
                        'reason': f'Moved {teacher} from {slot_str} to {alt_slot}',
                        'new_slot': alt_slot
                    }

        # Strategy 3: Try a different day for practicals
        if activity_type == 'practical' and available_slots:
            other_days = [d for d in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"] if d != day]
            for other_day in other_days:
                for alt_slot in available_slots:
                    alt_conflicts = self.check_cross_class_overlap(other_day, alt_slot, teacher, cls, activity_type)
                    if not alt_conflicts:
                        self.resolutions_applied.append({
                            'type': 'day_change',
                            'day': day,
                            'class': cls,
                            'teacher': teacher,
                            'old_slot': f'{day} {slot_str}',
                            'new_slot': f'{other_day} {alt_slot}'
                        })
                        return {
                            'resolved': True,
                            'strategy': 'day_change',
                            'reason': f'Moved {teacher} from {day} {slot_str} to {other_day} {alt_slot}',
                            'new_day': other_day,
                            'new_slot': alt_slot
                        }

        self.resolutions_applied.append({
            'type': 'unresolved',
            'day': day,
            'class': cls,
            'teacher': teacher,
            'slot': slot_str,
            'conflicts': conflicts
        })

        return {
            'resolved': False,
            'strategy': 'failed',
            'reason': f'Could not resolve conflicts for {teacher} at {slot_str}',
            'conflicts': conflicts
        }

    def add_assignment(self, day, slot_time, cls, teacher, activity_type, details=""):
        """Record teacher assignment in global schedule"""
        if teacher == "TBD" or not teacher:
            return
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
        """Record an assignment and track in global schedule
        
        For 2-hour practicals, this blocks BOTH hours for the teacher.
        """
        if not (day == "Lunch" or "Project" in str(teacher) or "Library" in str(teacher)):
            # Track teacher for this slot
            self.teacher_assignments[(day, slot_time)].append((cls, teacher))
            # Track class
            self.class_assignments[(day, slot_time, cls)].append(batch)
            # Track lab if provided
            if lab:
                self.lab_assignments[(day, slot_time, lab)].append(batch)
            
            # For 2-hour practicals, also block the next consecutive hour
            if activity_type == 'practical' and ' - ' in slot_time:
                start_time, end_time = slot_time.split(' - ')
                # Calculate next hour slot
                try:
                    start_minutes = CrossClassConflictResolver()._time_to_minutes(start_time)
                    end_minutes = CrossClassConflictResolver()._time_to_minutes(end_time)
                    duration = end_minutes - start_minutes
                    
                    # If it's a 2-hour slot, block the second hour too
                    if duration >= 120:
                        next_hour_start = start_minutes + 60
                        next_hour_end = start_minutes + 120
                        next_slot = f"{next_hour_start // 60:02d}:{next_hour_start % 60:02d} - {next_hour_end // 60:02d}:{next_hour_end % 60:02d}"
                        self.teacher_assignments[(day, next_slot)].append((cls, teacher))
                        # Also track in cross-class resolver for the second hour
                        self.cross_class_resolver.add_assignment(day, next_slot, cls, teacher, activity_type)
                        if lab:
                            self.lab_assignments[(day, next_slot, lab)].append(batch)
                except:
                    pass  # If parsing fails, just continue with single slot
        
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


def validate_inputs_and_build_maps(classes, teachers, elective_subjects):
    """Build subject-teacher mappings and optional subject map"""
    subject_teacher = {}
    teacher_fullname_map = {}
    teacher_to_subjects = {}  # Track all subjects per teacher

    for t in teachers:
        for subj in t["subjects"]:
            subject_teacher[subj] = t["name"]   # short name for timetable
        teacher_fullname_map[t["name"]] = t.get("fullName", t["name"])
        teacher_to_subjects[t["name"]] = t["subjects"]
    
    # Auto-map practical subjects to their lecture teachers
    # If "DS" has a teacher, then "DS Lab", "DS Practical", "DS Lab Manual" etc. should use the same teacher
    lecture_subjects = set(subject_teacher.keys())
    for lecture_subj in lecture_subjects:
        teacher = subject_teacher[lecture_subj]
        # Create mappings for common practical variants
        practical_variants = [
            f"{lecture_subj} Lab",
            f"{lecture_subj} Practical", 
            f"{lecture_subj} Lab Manual",
            f"{lecture_subj} Practical Manual",
            lecture_subj.lower().replace(' ', '') + "lab",
            lecture_subj.lower().replace(' ', '') + "practical"
        ]
        for variant in practical_variants:
            if variant not in subject_teacher:
                subject_teacher[variant] = teacher
        
        # Also map without spaces (e.g., "DBMS Lab" -> "DBMSLab" or "dbmslab")
        base_name = lecture_subj.lower().replace(' ', '')
        for suffix in ['lab', 'practical', 'manual', 'practicalmanual', 'labmanual']:
            variant = base_name + suffix
            if variant not in subject_teacher:
                subject_teacher[variant] = teacher
            # Also try with original case
            variant_original = lecture_subj.replace(' ', '') + suffix.capitalize()
            if variant_original not in subject_teacher:
                subject_teacher[variant_original] = teacher

    # Elective subjects mapping: class → {lecturePairs: [], practicalAssignments: {}, usedPracticalBatches: set(), lectureTeachers: {}, practicalTeachers: {}}
    elective_map = {}
    for opt in elective_subjects:
        cls = opt["className"]
        if cls not in elective_map:
            elective_map[cls] = {"lecturePairs": [], "practicalAssignments": {}, "usedPracticalBatches": set(), "lectureTeachers": {}, "practicalTeachers": {}}
        
        # Handle lecture pairs (format: BC/IR, ML/AI)
        if opt.get("lectureSubject"):
            lecture_pairs = [pair.strip() for pair in opt["lectureSubject"].split(",") if pair.strip()]
            elective_map[cls]["lecturePairs"].extend(lecture_pairs)
        
        # Handle lecture teachers (format: BC/IR (SFS/KMG))
        if opt.get("lectureTeachers"):
            elective_map[cls]["lectureTeachers"] = opt["lectureTeachers"]
        
        # Handle practical assignments (format: B1-BC, B2-ML)
        if opt.get("practicalSubject"):
            practical_assignments = [s.strip() for s in opt["practicalSubject"].split(",") if s.strip()]
            for assignment in practical_assignments:
                if "-" in assignment:
                    batch, subject = assignment.split("-", 1)
                    elective_map[cls]["practicalAssignments"][batch.strip()] = subject.strip()
        
        # Handle practical teachers (format: BC (SFS), ML (GDH))
        if opt.get("practicalTeachers"):
            elective_map[cls]["practicalTeachers"] = opt["practicalTeachers"]

    return {
        "subject_teacher": subject_teacher,
        "teacher_fullname_map": teacher_fullname_map,
        "elective_map": elective_map,
        "teacher_to_subjects": teacher_to_subjects
    }, None


def generate_weekly_specials():
    """Assign exactly one Project Day per week randomly (excluding Saturday)
    Also assign one T&P session and one Library session on different days
    
    Returns: (project_day, tp_day, library_day)
    """
    # Exclude Saturday from Project Day selection
    available_days = [day for day in DAYS if day != "Saturday"]
    project_day = random.choice(available_days)
    
    # Assign T&P and Library on different days (not Saturday, not project day)
    remaining_days = [d for d in available_days if d != project_day]
    if len(remaining_days) >= 2:
        tp_day = random.choice(remaining_days)
        library_day = random.choice([d for d in remaining_days if d != tp_day])
    else:
        tp_day = None
        library_day = None
    
    return project_day, tp_day, library_day


def generate_class_specials(cls, project_day):
    """Generate T&P or Library day for a specific class
    
    SE gets Library, TE and BE get T&P
    Returns the special day for this class
    """
    available_days = [day for day in DAYS if day != "Saturday" and day != project_day]
    
    if cls == "SE":
        # SE gets Library
        return random.choice(available_days) if available_days else None
    elif cls in ["TE", "BE"]:
        # TE and BE get T&P
        return random.choice(available_days) if available_days else None
    return None


def generate_timetable(classes, teachers, subjects, timeslots, batches, labs, maps, include_project=False):
    """Generate conflict-free timetable with cross-class conflict resolution using a multi-phase global approach."""
    
    subject_teacher = maps["subject_teacher"]
    elective_map = maps["elective_map"]
    all_teachers = list(set(subject_teacher.values()))

    # Initialize basic structure
    timetable = {cls: {day: {} for day in DAYS} for cls in classes}
    conflict_tracker = ConflictTracker()
    
    # Global Special Days
    if include_project:
        project_day, _, _ = generate_weekly_specials()
    else:
        project_day = None

    # Teacher mappings for shared teacher analysis
    class_teacher_map = defaultdict(set)
    for cls in classes:
        for subj in set(subjects.get(cls, {}).get("lectures", [])) | set(subjects.get(cls, {}).get("practicals", [])):
            t = subject_teacher.get(subj)
            if t: class_teacher_map[cls].add(t)
        # Add elective teachers
        elec = elective_map.get(cls, {})
        if elec.get("lectureTeachers"):
            for t in elec["lectureTeachers"].split(","):
                t_name = t.strip()
                if t_name: class_teacher_map[cls].add(t_name)
        if elec.get("practicalTeachers"):
            import re
            t_names = re.findall(r'\((.*?)\)', elec["practicalTeachers"])
            for t_name in t_names:
                t_name = t_name.strip()
                if t_name: class_teacher_map[cls].add(t_name)

    # Dynamic Timing Groups
    class_timing_group_map = {}
    if len(classes) == 1:
        class_timing_group_map[classes[0]] = "Group2"
    else:
        shared_groups = []
        processed = set()
        for cls in classes:
            if cls in processed: continue
            connected = {cls}
            queue = [cls]
            while queue:
                curr = queue.pop(0)
                for other in classes:
                    if other not in connected and (class_teacher_map[curr] & class_teacher_map[other]):
                        connected.add(other)
                        queue.append(other)
            shared_groups.append(connected)
            processed.update(connected)
        
        def preferred_group_for(cls_name):
            return get_class_timing_group(cls_name)

        for group_set in shared_groups:
            group_list = list(group_set)
            if len(group_list) == 1:
                class_timing_group_map[group_list[0]] = preferred_group_for(group_list[0])
            elif len(group_list) == 2:
                preferred0 = preferred_group_for(group_list[0])
                preferred1 = preferred_group_for(group_list[1])
                if preferred0 != preferred1:
                    class_timing_group_map[group_list[0]] = preferred0
                    class_timing_group_map[group_list[1]] = preferred1
                else:
                    # Avoid assigning both classes to the same default slot
                    class_timing_group_map[group_list[0]] = "Group1"
                    class_timing_group_map[group_list[1]] = "Group3"
            else:
                used_groups = set()
                groups = ["Group1", "Group2", "Group3"]
                for cls_name in group_list:
                    preferred = preferred_group_for(cls_name)
                    if preferred not in used_groups:
                        class_timing_group_map[cls_name] = preferred
                        used_groups.add(preferred)

                next_group_index = 0
                for cls_name in group_list:
                    if cls_name not in class_timing_group_map:
                        while groups[next_group_index] in used_groups:
                            next_group_index = (next_group_index + 1) % len(groups)
                        class_timing_group_map[cls_name] = groups[next_group_index]
                        used_groups.add(groups[next_group_index])
                        next_group_index = (next_group_index + 1) % len(groups)

    def get_prac_slots(cls): return PRACTICAL_SLOTS[class_timing_group_map.get(cls, "Group1")]
    def get_lunch(cls): return LUNCH_SLOTS[class_timing_group_map.get(cls, "Group1")]

    # Per-class Stats & Pre-calculation
    class_stats = {}
    for cls in classes:
        prac_slots = get_prac_slots(cls)
        avail_days = [d for d in DAYS if d != project_day]
        practical_days = random.sample(avail_days, min(4, len(avail_days)))
        
        total_lec_slots = 0
        for day in DAYS:
            if day == project_day: continue
            for slot, stype in timeslots:
                if stype == "lecture" and (day not in practical_days or slot not in prac_slots):
                    total_lec_slots += 1
        
        lecs = subjects[cls].get("lectures", [])
        target = total_lec_slots // len(lecs) if lecs else 0
        
        class_stats[cls] = {
            "practical_days": set(practical_days),
            "lecture_distribution": {s: 0 for s in lecs},
            "target_lectures": target,
            "extra_lectures": total_lec_slots % len(lecs) if lecs else 0,
            "day_practical_subjects": {d: set() for d in DAYS},
            "weekly_prac_count": {s: 0 for s in set(subjects[cls].get("practicals", [])) | set(elective_map.get(cls, {}).get("practicalAssignments", {}).values())},
            "assigned_practicals": {batch: set() for batch in batches.get(cls, [])},
            "special_day": generate_class_specials(cls, project_day)
        }

    # PHASE 1: Fixed Sessions
    for cls in classes:
        lunch = get_lunch(cls)
        special_day = class_stats[cls]["special_day"]
        for day in DAYS:
            timetable[cls][day][lunch] = "Lunch Break"
            if day == project_day:
                slots = [t[0] for t in timeslots if t[0] != lunch]
                for t in class_teacher_map[cls]:
                    for s in slots: conflict_tracker.add_assignment(day, s, cls, "All", t, activity_type='project')
                timetable[cls][day][slots[0]] = "PROJECT DAY"
                for s in slots[1:]: timetable[cls][day][s] = "MERGED"
            elif day == special_day:
                label = "T&P Session" if cls in ["TE", "BE"] else "Library" if cls == "SE" else None
                if label:
                    s1, s2 = "15:00 - 16:00", "16:00 - 17:00"
                    if timetable[cls][day].get(s1) or timetable[cls][day].get(s2): s1, s2 = "10:00 - 11:00", "11:00 - 12:00"
                    timetable[cls][day][s1] = label
                    timetable[cls][day][s2] = "MERGED"
                    conflict_tracker.add_assignment(day, s1, cls, "All", label, activity_type='special')
                    conflict_tracker.add_assignment(day, s2, cls, "All", label, activity_type='special')

    # PHASE 2: Global Lecture Scheduling (Prioritize Lectures)
    for day in DAYS:
        if day == project_day: continue
        for slot_time, stype in timeslots:
            if stype != "lecture": continue
            for cls in classes:
                if timetable[cls][day].get(slot_time): continue
                if day in class_stats[cls]["practical_days"] and slot_time in get_prac_slots(cls): continue
                
                stats = class_stats[cls]
                lecs = subjects[cls].get("lectures", [])
                random.shuffle(lecs)
                for s in lecs:
                    if stats["lecture_distribution"][s] < stats["target_lectures"] + (1 if stats["extra_lectures"] > 0 else 0):
                        t = subject_teacher.get(s, "TBD")
                        if not conflict_tracker.has_teacher_conflict(day, slot_time, t) and \
                           not conflict_tracker.check_cross_class_conflict(day, slot_time, cls, t):
                            timetable[cls][day][slot_time] = f"{s} ({t})"
                            conflict_tracker.add_assignment(day, slot_time, cls, "All", t, activity_type='lecture')
                            stats["lecture_distribution"][s] += 1
                            if stats["lecture_distribution"][s] > stats["target_lectures"]: stats["extra_lectures"] -= 1
                            break

    # PHASE 3: Global Practical Scheduling with Round-Robin Rotation
    # Track practical index rotation for each class (to shuffle subjects across days)
    practical_rotation_offset = {cls: 0 for cls in classes}
    
    for day in DAYS:
        if day == project_day: continue
        for cls in classes:
            stats = class_stats[cls]
            if day not in stats["practical_days"]: continue
            prac_slots = get_prac_slots(cls)
            s1, s2 = prac_slots[0], prac_slots[1]
            if timetable[cls][day].get(s1): continue
            
            prac_assignments = elective_map.get(cls, {}).get("practicalAssignments", {})
            class_batches = batches.get(cls, [])
            available_practicals = subjects[cls].get("practicals", [])
            
            # Use explicit assignments if available, otherwise use rotation
            if prac_assignments:
                # Fixed assignments: B1-DS, B2-CG, etc.
                line_assignments = []
                for i, batch in enumerate(class_batches):
                    lab = labs[i % len(labs)] if labs else f"Lab({i})"
                    subj = prac_assignments.get(batch)
                    if subj:
                        t = subject_teacher.get(subj, "TBD")
                        if conflict_tracker.has_teacher_conflict(day, s1, t) or conflict_tracker.has_teacher_conflict(day, s2, t):
                            for alt in all_teachers:
                                if not conflict_tracker.has_teacher_conflict(day, s1, alt) and not conflict_tracker.has_teacher_conflict(day, s2, alt):
                                    t = alt
                                    break
                        line_assignments.append(f"{batch}: {subj} ({t}) in {lab}")
                        conflict_tracker.add_assignment(day, s1, cls, batch, t, lab, activity_type='practical')
                        stats["assigned_practicals"][batch].add(subj)
                        stats["weekly_prac_count"][subj] += 1
                        stats["day_practical_subjects"][day].add(subj)
                
                if line_assignments:
                    timetable[cls][day][s1] = " / ".join(line_assignments)
                    timetable[cls][day][s2] = "MERGED"
            elif available_practicals:
                # Round-robin rotation: rotate subjects across batches on each practical day
                line_assignments = []
                num_batches = len(class_batches)
                num_practicals = len(available_practicals)
                
                for batch_idx, batch in enumerate(class_batches):
                    lab = labs[batch_idx % len(labs)] if labs else f"Lab({batch_idx})"
                    
                    # Calculate which practical this batch gets (rotated by offset)
                    practical_idx = (batch_idx + practical_rotation_offset[cls]) % num_practicals if num_practicals > 0 else 0
                    subj = available_practicals[practical_idx] if num_practicals > 0 else None
                    
                    if subj:
                        # Verify batch hasn't done this practical yet this week
                        if subj in stats["assigned_practicals"][batch]:
                            # Skip and find alternative
                            for alt_idx in range(num_practicals):
                                alt_subj = available_practicals[alt_idx]
                                if alt_subj not in stats["assigned_practicals"][batch]:
                                    subj = alt_subj
                                    break
                        
                        t = subject_teacher.get(subj, "TBD")
                        if conflict_tracker.has_teacher_conflict(day, s1, t) or conflict_tracker.has_teacher_conflict(day, s2, t):
                            for alt in all_teachers:
                                if not conflict_tracker.has_teacher_conflict(day, s1, alt) and not conflict_tracker.has_teacher_conflict(day, s2, alt):
                                    t = alt
                                    break
                        
                        line_assignments.append(f"{batch}: {subj} ({t}) in {lab}")
                        conflict_tracker.add_assignment(day, s1, cls, batch, t, lab, activity_type='practical')
                        stats["assigned_practicals"][batch].add(subj)
                        stats["weekly_prac_count"][subj] += 1
                        stats["day_practical_subjects"][day].add(subj)
                
                if line_assignments:
                    timetable[cls][day][s1] = " / ".join(line_assignments)
                    timetable[cls][day][s2] = "MERGED"
                
                # Increment rotation offset for next practical day of this class
                practical_rotation_offset[cls] += 1

    # PHASE 4: Cleanup
    for day in DAYS:
        if day == project_day: continue
        for slot_time, stype in timeslots:
            for cls in classes:
                if not timetable[cls][day].get(slot_time) and stype == "lecture":
                    lecs = subjects[cls].get("lectures", [])
                    random.shuffle(lecs)
                    for s in lecs:
                        t = subject_teacher.get(s, "TBD")
                        if not conflict_tracker.has_teacher_conflict(day, slot_time, t):
                            timetable[cls][day][slot_time] = f"{s} ({t})"
                            conflict_tracker.add_assignment(day, slot_time, cls, "All", t, activity_type='lecture')
                            break
                    if not timetable[cls][day].get(slot_time): timetable[cls][day][slot_time] = "Vacant Slot"

    return timetable
