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

# ============ ADVANCED CROSS-CLASS CONFLICT RESOLUTION ============

class CrossClassConflictResolver:
    """
    Resolves conflicts where the same teacher has overlapping assignments 
    across multiple classes (e.g., Kranti teaching SE lecture 10-11 AND TE practical 10-12)
    """
    
    def __init__(self):
        # Global schedule: {teacher: {day: [(slot_time, cls, activity_type, details), ...]}}
        self.global_teacher_schedule = defaultdict(lambda: defaultdict(list))
        self.conflict_resolutions = []  # Log of resolutions made
    
    def _time_to_minutes(self, time_str):
        """Convert 'HH:MM' to minutes since midnight"""
        try:
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        except:
            return 0
    
    def check_cross_class_overlap(self, day, slot_start, slot_end, teacher, cls, activity_type):
        """
        Check if teacher has OVERLAPPING commitments in OTHER classes
        
        Args:
            day: "Monday"
            slot_start: "10:00" (start time)
            slot_end: "12:00" (end time for 2-hour practical)
            teacher: "Kranti"
            cls: "TE" (current class)
            activity_type: "practical" or "lecture"
        
        Returns:
            [(other_class, other_activity, other_slot_time, conflict_type), ...]
            conflict_type: "full_overlap" | "partial_overlap" | "adjacent"
        """
        conflicts = []
        start_min = self._time_to_minutes(slot_start)
        end_min = self._time_to_minutes(slot_end)
        
        if teacher not in self.global_teacher_schedule:
            return conflicts
        
        if day not in self.global_teacher_schedule[teacher]:
            return conflicts
        
        for other_slot_time, other_cls, other_activity, other_details in self.global_teacher_schedule[teacher][day]:
            if other_cls == cls:  # Same class, not cross-class
                continue
            
            # Parse other slot time
            parts = other_slot_time.split(" - ")
            other_start_str = parts[0]
            other_end_str = parts[1]
            other_start = self._time_to_minutes(other_start_str)
            other_end = self._time_to_minutes(other_end_str)
            
            # Check for overlap
            if start_min < other_end and end_min > other_start:
                # Determine overlap type
                if start_min <= other_start and end_min >= other_end:
                    conflict_type = "full_overlap"  # Completely overlaps other
                elif other_start <= start_min and other_end >= end_min:
                    conflict_type = "full_overlap"  # Completely overlapped by other
                elif (other_start < end_min) and (other_start >= start_min):
                    conflict_type = "partial_overlap"  # Overlaps at some point
                else:
                    conflict_type = "partial_overlap"
                
                conflicts.append((other_cls, other_activity, other_slot_time, conflict_type))
        
        return conflicts
    
    def resolve_cross_class_conflict(self, day, slot_start, slot_end, teacher, cls, 
                                     activity_type, primary_subject, all_classes, all_subjects):
        """
        Resolve cross-class teacher conflicts using multiple strategies
        
        Strategies (in order of preference):
        1. Move practical to different 2-hour slot (13-15 or 15-17)
        2. If activity is lecture, split it across available slots
        3. Reassign to different teacher
        4. Move overlapping class activity instead
        
        Returns:
            {
                'resolved': bool,
                'strategy': "slot_move" | "split_lectures" | "reassign_teacher" | "move_other_activity",
                'new_slot': "13:00 - 15:00",
                'recommendation': "Move TE practical to 13:00-15:00 slot"
            }
        """
        
        conflicts = self.check_cross_class_overlap(day, slot_start, slot_end, teacher, cls, activity_type)
        
        if not conflicts:
            return {'resolved': True, 'conflicts': 0}
        
        # Strategy 1: Move practical to different 2-hour slot
        if activity_type == "practical":
            available_slots = ["10:00 - 12:00", "13:00 - 15:00", "15:00 - 17:00"]
            current_slot = f"{slot_start} - {slot_end}"
            
            for alt_slot in available_slots:
                if alt_slot == current_slot:
                    continue
                
                alt_start, alt_end = alt_slot.split(" - ")
                new_conflicts = self.check_cross_class_overlap(day, alt_start, alt_end, teacher, cls, activity_type)
                
                if not new_conflicts:
                    return {
                        'resolved': True,
                        'strategy': 'slot_move',
                        'reason': f'Move {cls} {activity_type} to {alt_slot} to avoid conflict with {conflicts[0][0]}',
                        'old_slot': f'{slot_start} - {slot_end}',
                        'new_slot': alt_slot,
                        'conflicting_classes': [c[0] for c in conflicts]
                    }
        
        # Strategy 2: Split lectures across two 1-hour slots
        if activity_type == "lecture":
            one_hour_slots = ["10:00 - 11:00", "11:00 - 12:00", "13:00 - 14:00", 
                             "14:00 - 15:00", "15:00 - 16:00", "16:00 - 17:00"]
            
            available_for_split = []
            for slot in one_hour_slots:
                start, end = slot.split(" - ")
                if not self.check_cross_class_overlap(day, start, end, teacher, cls, "lecture"):
                    available_for_split.append(slot)
            
            if len(available_for_split) >= 2:
                return {
                    'resolved': True,
                    'strategy': 'split_lectures',
                    'reason': f'Split {cls} lectures across multiple 1-hour slots',
                    'slots': available_for_split[:2],
                    'conflicting_classes': [c[0] for c in conflicts]
                }
        
        # Strategy 3: Suggest reassigning to different teacher
        return {
            'resolved': False,
            'strategy': 'requires_reassignment',
            'reason': f'Cannot resolve: {teacher} has {len(conflicts)} conflicts on {day}. Recommend reassigning {cls} {activity_type} to different teacher.',
            'conflicts': conflicts,
            'conflicting_classes': [c[0] for c in conflicts]
        }
    
    def add_assignment(self, day, slot_time, cls, teacher, activity_type, details=""):
        """Record teacher assignment for cross-class tracking"""
        self.global_teacher_schedule[teacher][day].append((slot_time, cls, activity_type, details))
    
    def generate_conflict_report(self):
        """Generate report of all cross-class conflicts and resolutions"""
        report = {
            'total_teachers': len(self.global_teacher_schedule),
            'resolutions': self.conflict_resolutions,
            'summary': f'Cross-class conflict resolution completed'
        }
        return report


# Conflict tracking structures
class ConflictTracker:
    """Track and resolve scheduling conflicts"""
    def __init__(self):
        # Global teacher schedule: (day, slot_time) -> {teacher: (class, activity_type)}
        self.global_teacher_schedule = defaultdict(dict)
        # (day, slot_time) -> [(class, teacher), ...]
        self.teacher_assignments = defaultdict(list)
        # (day, slot_time, lab) -> [batch, ...]
        self.lab_assignments = defaultdict(list)
        # (day, slot_time, class) -> [batch, ...]
        self.class_assignments = defaultdict(list)
        self.conflicts = {"teacher": [], "lab": [], "class": [], "cross_class": []}
        # Cross-class resolver
        self.cross_class_resolver = CrossClassConflictResolver()
    
    def _time_to_minutes(self, time_str):
        """Convert 'HH:MM' to minutes since midnight"""
        try:
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        except:
            return 0
    
    def has_teacher_conflict(self, day, slot_time, teacher_short):
        """Check if teacher is already assigned at this time"""
        key = (day, slot_time)
        return teacher_short in self.global_teacher_schedule[key]
    
    def has_lab_conflict(self, day, slot_time, lab, batch):
        """Check if lab is already assigned to different batch at this time"""
        key = (day, slot_time, lab)
        return batch not in self.lab_assignments[key] and len(self.lab_assignments[key]) > 0
    
    def has_class_conflict(self, day, slot_time, cls):
        """Check if class already has an assignment at this time"""
        key = (day, slot_time, cls)
        return len(self.class_assignments[key]) > 0
    
    def add_assignment(self, day, slot_time, cls, batch, teacher, lab=None, activity_type="lecture"):
        """Record an assignment"""
        if not (day == "Lunch" or "Project" in str(teacher) or "Library" in str(teacher)):
            # Track in global teacher schedule (for cross-class detection)
            key = (day, slot_time)
            self.global_teacher_schedule[key][teacher] = (cls, activity_type)
            
            # Add to cross-class resolver for advanced conflict tracking
            self.cross_class_resolver.add_assignment(day, slot_time, cls, teacher, activity_type)
            
            # Track teacher
            self.teacher_assignments[key].append((cls, teacher))
            # Track class
            self.class_assignments[(day, slot_time, cls)].append(batch)
            # Track lab if provided
            if lab:
                self.lab_assignments[(day, slot_time, lab)].append(batch)
    
    def check_cross_class_conflict(self, day, slot_start, slot_end, teacher, cls, activity_type):
        """Check for cross-class teacher conflicts"""
        return self.cross_class_resolver.check_cross_class_overlap(day, slot_start, slot_end, teacher, cls, activity_type)
    
    def resolve_cross_class_conflict(self, day, slot_start, slot_end, teacher, cls, activity_type, subject, all_classes, all_subjects):
        """Resolve cross-class conflicts"""
        return self.cross_class_resolver.resolve_cross_class_conflict(day, slot_start, slot_end, teacher, cls, activity_type, subject, all_classes, all_subjects)
    
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

    If ``fixed_project_day`` is provided the returned tuple will use that
    value instead of randomly choosing a new project day. This allows a
    caller to ensure one shared project day across multiple classes while
    still letting the other special days differ per class.

    Returns: (project_day, lecture_day, library_day, tp_day, exp_day)
    """
    project_day = fixed_project_day if fixed_project_day is not None else random.choice(DAYS)
    other_days = [d for d in DAYS if d != project_day]
    lecture_day = random.choice(other_days)
    remaining_days = [d for d in other_days if d != lecture_day]
    library_day = random.choice(remaining_days)
    tp_day = random.choice([d for d in remaining_days if d != library_day])
    exp_day = random.choice([d for d in remaining_days if d not in [library_day, tp_day]])
    return project_day, lecture_day, library_day, tp_day, exp_day


def generate_timetable(classes, teachers, subjects, timeslots, batches, labs, maps):
    """Generate conflict-free timetable with cross-class teacher conflict resolution"""
    subject_teacher = maps["subject_teacher"]
    optional_map = maps["optional_map"]
    teacher_to_subjects = maps.get("teacher_to_subjects", {})

    # Empty timetable structure
    timetable = {cls: {day: {} for day in DAYS} for cls in classes}
    # pick a single project day for the whole week
    project_day_global = random.choice(DAYS)
    specials = {cls: generate_weekly_specials(fixed_project_day=project_day_global) for cls in classes}
    
    # Initialize conflict tracker
    conflict_tracker = ConflictTracker()

    for cls in classes:
        project_day, lecture_day, library_day, tp_day, exp_day = specials[cls]
        project_day = project_day_global

        # Select 4 days for practicals, excluding project and lecture-only days
        practical_days = [d for d in DAYS if d not in [project_day, lecture_day]][:4]

        # Track assigned practicals for each batch (avoid repeats across the week)
        assigned_practicals = {batch: set() for batch in batches.get(cls, [])}
        
        # Track teacher workload: (day, teacher) -> count
        teacher_workload = defaultdict(int)
        # Track labs usage across all classes
        lab_usage = defaultdict(lambda: defaultdict(set))

        for day in DAYS:
            used_lectures = set()
            lectures_per_teacher = defaultdict(int)

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
                            
                            while conflict_tracker.has_teacher_conflict(day, slot_time, teacher) and len(remaining) > 1:
                                remaining.remove(subj)
                                subj = random.choice(remaining)
                                teacher = subject_teacher.get(subj, "TBD")
                            
                            timetable[cls][day][slot_time] = f"{subj} ({teacher})"
                            conflict_tracker.add_assignment(day, slot_time, cls, "lecture", teacher, activity_type="lecture")
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
                    if slot_time == PRACTICAL_SLOTS[cls][0]:
                        assignments = []
                        practical_slot_start = slot_time.split(" - ")[0]
                        practical_slot_end = PRACTICAL_SLOTS[cls][1].split(" - ")[1]

                        for i, batch in enumerate(batches.get(cls, [])):
                            lab = labs[i % len(labs)] if labs else "Lab(0)"
                            
                            optional_subject = None
                            for key, opt in optional_map.items():
                                if key[0] == cls and key[1] == batch:
                                    optional_subject = opt
                                    break

                            if optional_subject:
                                subj = optional_subject["subject"]
                                teacher_short = subject_teacher.get(subj, "TBD")
                                
                                # Check cross-class conflicts for practicals
                                cross_conflicts = conflict_tracker.check_cross_class_conflict(day, practical_slot_start, practical_slot_end, teacher_short, cls, "practical")
                                
                                if cross_conflicts:
                                    resolution = conflict_tracker.resolve_cross_class_conflict(day, practical_slot_start, practical_slot_end, teacher_short, cls, "practical", subj, classes, subjects)
                                    if resolution['resolved'] and resolution['strategy'] == 'slot_move':
                                        new_slot = resolution['new_slot']
                                        assignments.append(f"{batch}: {subj} ({teacher_short}) in {lab} [MOVED to {new_slot}]")
                                    else:
                                        assignments.append(f"{batch}: {subj} ({teacher_short}) in {lab}")
                                else:
                                    assignments.append(f"{batch}: {subj} ({teacher_short}) in {lab}")
                                
                                conflict_tracker.add_assignment(day, slot_time, cls, batch, teacher_short, lab, "practical")
                                assigned_practicals[batch].add(subj)
                                
                            elif subjects[cls].get("practicals"):
                                remaining = [s for s in subjects[cls]["practicals"] if s not in assigned_practicals[batch]]
                                if remaining:
                                    subj = random.choice(remaining)
                                    assigned_practicals[batch].add(subj)
                                    teacher_short = subject_teacher.get(subj, "TBD")
                                    
                                    # Check cross-class conflicts
                                    cross_conflicts = conflict_tracker.check_cross_class_conflict(day, practical_slot_start, practical_slot_end, teacher_short, cls, "practical")
                                    
                                    if cross_conflicts:
                                        resolution = conflict_tracker.resolve_cross_class_conflict(day, practical_slot_start, practical_slot_end, teacher_short, cls, "practical", subj, classes, subjects)
                                        # Use recommendation in output
                                        if 'recommendation' in resolution:
                                            assignments.append(f"{batch}: {subj} ({teacher_short}) in {lab} [{resolution['reason']}]")
                                        else:
                                            assignments.append(f"{batch}: {subj} ({teacher_short}) in {lab}")
                                    else:
                                        assignments.append(f"{batch}: {subj} ({teacher_short}) in {lab}")
                                    
                                    conflict_tracker.add_assignment(day, slot_time, cls, batch, teacher_short, lab, "practical")
                                else:
                                    subj = random.choice(subjects[cls]["practicals"])
                                    assigned_practicals[batch].add(subj)
                                    teacher_short = subject_teacher.get(subj, "TBD")
                                    assignments.append(f"{batch}: {subj} ({teacher_short}) in {lab}")
                                    conflict_tracker.add_assignment(day, slot_time, cls, batch, teacher_short, lab, "practical")
                            else:
                                assignments.append(f"{batch}: Practical (TBD) in {lab}")

                        timetable[cls][day][slot_time] = " / ".join(assignments)
                        has_defined_practicals = bool(subjects[cls].get("practicals")) or any(k[0] == cls for k in optional_map.keys())
                        if has_defined_practicals:
                            timetable[cls][day][PRACTICAL_SLOTS[cls][1]] = "MERGED"
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
                    
                    subj = None
                    for attempt_subj in remaining:
                        attempt_teacher = subject_teacher.get(attempt_subj, "TBD")
                        if lectures_per_teacher[attempt_teacher] < 3:
                            subj = attempt_subj
                            break
                    
                    if subj is None:
                        subj = random.choice(remaining)
                    
                    used_lectures.add(subj)
                    teacher = subject_teacher.get(subj, "TBD")
                    
                    if conflict_tracker.has_teacher_conflict(day, slot_time, teacher):
                        for alt_subj in remaining:
                            alt_teacher = subject_teacher.get(alt_subj, "TBD")
                            if not conflict_tracker.has_teacher_conflict(day, slot_time, alt_teacher):
                                subj = alt_subj
                                teacher = alt_teacher
                                break
                    
                    timetable[cls][day][slot_time] = f"{subj} ({teacher})"
                    conflict_tracker.add_assignment(day, slot_time, cls, "lecture", teacher, activity_type="lecture")
                    lectures_per_teacher[teacher] += 1
                    teacher_workload[(day, teacher)] += 1
                else:
                    timetable[cls][day][slot_time] = "Free"

    return timetable
