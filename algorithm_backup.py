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
        self.conflicts = {"teacher": [], "lab": [], "class": []}
    
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
    
    def add_assignment(self, day, slot_time, cls, batch, teacher, lab=None):
        """Record an assignment"""
        if not (day == "Lunch" or "Project" in str(teacher) or "Library" in str(teacher)):
            # Track teacher
            self.teacher_assignments[(day, slot_time)].append((cls, teacher))
            # Track class
            self.class_assignments[(day, slot_time, cls)].append(batch)
            # Track lab if provided
            if lab:
                self.lab_assignments[(day, slot_time, lab)].append(batch)
    
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


def generate_weekly_specials():
    """Assign special days (project, lecture-only, library, T&P, experiential)

    Returns: (project_day, lecture_day, library_day, tp_day, exp_day)
    """
    project_day = random.choice(DAYS)
    other_days = [d for d in DAYS if d != project_day]
    lecture_day = random.choice(other_days)
    remaining_days = [d for d in other_days if d != lecture_day]
    library_day = random.choice(remaining_days)
    tp_day = random.choice([d for d in remaining_days if d != library_day])
    exp_day = random.choice([d for d in remaining_days if d not in [library_day, tp_day]])
    return project_day, lecture_day, library_day, tp_day, exp_day


def generate_timetable(classes, teachers, subjects, timeslots, batches, labs, maps):
    subject_teacher = maps["subject_teacher"]
    optional_map = maps["optional_map"]
    teacher_to_subjects = maps.get("teacher_to_subjects", {})

    # Empty timetable structure
    timetable = {cls: {day: {} for day in DAYS} for cls in classes}
    specials = {cls: generate_weekly_specials() for cls in classes}
    
    # Initialize conflict tracker
    conflict_tracker = ConflictTracker()

    for cls in classes:
        project_day, lecture_day, library_day, tp_day, exp_day = specials[cls]

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
                            
                            timetable[cls][day][slot_time] = f"{subj} ({teacher})"
                            conflict_tracker.add_assignment(day, slot_time, cls, "lecture", teacher)
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
                                
                                # Resolve lab conflict by rotating labs
                                attempt = 0
                                while conflict_tracker.has_lab_conflict(day, slot_time, lab, batch) and attempt < len(labs):
                                    lab = labs[(i + attempt + 1) % len(labs)]
                                    attempt += 1
                                
                                assignments.append(f"{batch}: {subj} ({teacher_short}) in {lab}")
                                conflict_tracker.add_assignment(day, slot_time, cls, batch, teacher_short, lab)
                                assigned_practicals[batch].add(subj)
                                lab_usage[(day, slot_time, lab)][batch].add(subj)
                            elif subjects[cls].get("practicals"):
                                remaining = [s for s in subjects[cls]["practicals"] if s not in assigned_practicals[batch]]
                                if remaining:
                                    subj = random.choice(remaining)
                                    assigned_practicals[batch].add(subj)
                                    teacher_short = subject_teacher.get(subj, "TBD")
                                    
                                    # Resolve lab conflict
                                    attempt = 0
                                    while conflict_tracker.has_lab_conflict(day, slot_time, lab, batch) and attempt < len(labs):
                                        lab = labs[(i + attempt + 1) % len(labs)]
                                        attempt += 1
                                    
                                    assignments.append(f"{batch}: {subj} ({teacher_short}) in {lab}")
                                    conflict_tracker.add_assignment(day, slot_time, cls, batch, teacher_short, lab)
                                    lab_usage[(day, slot_time, lab)][batch].add(subj)
                                else:
                                    # All practicals already assigned once — reuse one (allow repeats)
                                    subj = random.choice(subjects[cls]["practicals"])
                                    assigned_practicals[batch].add(subj)
                                    teacher_short = subject_teacher.get(subj, "TBD")
                                    
                                    # Resolve lab conflict
                                    attempt = 0
                                    while conflict_tracker.has_lab_conflict(day, slot_time, lab, batch) and attempt < len(labs):
                                        lab = labs[(i + attempt + 1) % len(labs)]
                                        attempt += 1
                                    
                                    assignments.append(f"{batch}: {subj} ({teacher_short}) in {lab}")
                                    conflict_tracker.add_assignment(day, slot_time, cls, batch, teacher_short, lab)
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
                    
                    timetable[cls][day][slot_time] = f"{subj} ({teacher})"
                    conflict_tracker.add_assignment(day, slot_time, cls, "lecture", teacher)
                    lectures_per_teacher[teacher] += 1
                    teacher_workload[(day, teacher)] += 1
                else:
                    timetable[cls][day][slot_time] = "Free"

    return timetable
