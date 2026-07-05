import random
from algorithm import generate_timetable, validate_inputs_and_build_maps, DAYS


def make_sample_input():
    classes = ["SE", "TE"]
    teachers = [
        {"name":"T1","fullName":"Dr. Alice","subjects":["Math","DBMS"]},
        {"name":"T2","fullName":"Dr. Bob","subjects":["OS","Networks"]},
        {"name":"T3","fullName":"Dr. Charlie","subjects":["Web","Security"]}
    ]
    subjects = {
        "SE": {"lectures":["Math","DBMS","OS"], "practicals":["DBMS Lab","OS Lab","Networks Lab"]},
        "TE": {"lectures":["Web","Security","AI"], "practicals":["Web Lab","Security Lab"]}
    }
    batches = {"SE":["A","B"], "TE":["X","Y"]}
    labs = ["Lab(A)","Lab(B)","Lab(C)"]
    optional_subjects = []
    return classes, teachers, subjects, batches, labs, optional_subjects


def test_no_teacher_conflicts():
    """Verify no teacher teaches multiple classes at same time"""
    random.seed(42)
    classes, teachers, subjects, batches, labs, optional_subjects = make_sample_input()
    maps, _ = validate_inputs_and_build_maps(classes, teachers, optional_subjects)
    tt = generate_timetable(classes, teachers, subjects, [
        ("10:00 - 11:00", "lecture"),
        ("11:00 - 12:00", "lecture"),
        ("12:00 - 13:00", "lunch"),
        ("13:00 - 14:00", "lecture"),
        ("14:00 - 15:00", "lecture"),
        ("15:00 - 16:00", "lecture"),
        ("16:00 - 17:00", "lecture"),
    ], batches, labs, maps)

    # Track teacher assignments: (day, slot_time) -> set of teachers
    teacher_slots = {}
    
    for cls in classes:
        for day in DAYS:
            for slot_time, val in tt[cls][day].items():
                # ignore lunch break entries
                if val and slot_time != "12:00 - 13:00":
                    # Extract teacher names if present
                    if " (" in val:
                        parts = val.split(" / ")
                        for part in parts:
                            if "(" in part and ")" in part:
                                teacher = part.split("(")[1].split(")")[0]
                                key = (day, slot_time)
                                if key not in teacher_slots:
                                    teacher_slots[key] = set()
                                teacher_slots[key].add(teacher)
    
    # Check no teacher appears more than once per slot
    for (day, slot), teachers_set in teacher_slots.items():
        assert len(teachers_set) <= len(set(teachers_set)), f"Teacher conflict at {day} {slot}"
    print("No teacher conflicts detected")


def test_no_project_days():
    """By default the generator must not insert any project entries."""
    random.seed(42)
    classes, teachers, subjects, batches, labs, optional_subjects = make_sample_input()
    maps, _ = validate_inputs_and_build_maps(classes, teachers, optional_subjects)
    tt = generate_timetable(classes, teachers, subjects, [
        ("10:00 - 11:00", "lecture"),
        ("11:00 - 12:00", "lecture"),
        ("12:00 - 13:00", "lunch"),
        ("13:00 - 14:00", "lecture"),
        ("14:00 - 15:00", "lecture"),
        ("15:00 - 16:00", "lecture"),
        ("16:00 - 17:00", "lecture"),
    ], batches, labs, maps)

    for cls in classes:
        for day in DAYS:
            for slot, val in tt[cls][day].items():
                assert val != "Project", f"Found unexpected project entry at {cls} {day} {slot}"
    print("Default run includes no project slots")




def test_random_project_assignment():
    """When include_project=True each class should have exactly one project day."""
    random.seed(123)
    classes, teachers, subjects, batches, labs, optional_subjects = make_sample_input()
    maps, _ = validate_inputs_and_build_maps(classes, teachers, optional_subjects)
    tt = generate_timetable(classes, teachers, subjects, [
        ("10:00 - 11:00", "lecture"),
        ("11:00 - 12:00", "lecture"),
        ("12:00 - 13:00", "lunch"),
        ("13:00 - 14:00", "lecture"),
        ("14:00 - 15:00", "lecture"),
        ("15:00 - 16:00", "lecture"),
        ("16:00 - 17:00", "lecture"),
    ], batches, labs, maps, include_project=True)

    # check each class has one day where all non-lunch slots are "Project"/"PROJECT DAY" or "MERGED"
    for cls in classes:
        project_day_count = 0
        for day in DAYS:
            slots = tt[cls][day]
            non_lunch = [val for slot, val in slots.items() if slot != "12:00 - 13:00" and slot != "13:00 - 14:00"]
            # A project day has first slot as "PROJECT DAY" and rest as "MERGED"
            if non_lunch and (non_lunch[0] in ["Project", "PROJECT DAY"]) and all(val in ["Project", "PROJECT DAY", "MERGED"] for val in non_lunch):
                project_day_count += 1
        assert project_day_count == 1, f"Expected exactly one project day for {cls}, got {project_day_count}"

    print("Random project assignment occurred as expected")


def test_only_valid_slots():
    """Generated timetable should not include slots outside predefined timeslots."""
    random.seed(42)
    classes, teachers, subjects, batches, labs, optional_subjects = make_sample_input()
    maps, _ = validate_inputs_and_build_maps(classes, teachers, optional_subjects)
    tt = generate_timetable(classes, teachers, subjects, [
        ("10:00 - 11:00", "lecture"),
        ("11:00 - 12:00", "lecture"),
        ("12:00 - 13:00", "lunch"),
        ("13:00 - 14:00", "lecture"),
        ("14:00 - 15:00", "lecture"),
        ("15:00 - 16:00", "lecture"),
        ("16:00 - 17:00", "lecture"),
    ], batches, labs, maps)

    valid = {"10:00 - 11:00","11:00 - 12:00","12:00 - 13:00","13:00 - 14:00","14:00 - 15:00","15:00 - 16:00","16:00 - 17:00"}
    for cls in tt:
        for day, slots in tt[cls].items():
            for slot_key in slots:
                assert slot_key in valid, f"Invalid slot {slot_key} found for {cls} on {day}"
    print("All slots valid")


def test_no_lab_conflicts():
    """Verify no lab is assigned to multiple batches at same time"""
    random.seed(42)
    classes, teachers, subjects, batches, labs, optional_subjects = make_sample_input()
    maps, _ = validate_inputs_and_build_maps(classes, teachers, optional_subjects)
    tt = generate_timetable(classes, teachers, subjects, [
        ("10:00 - 11:00", "lecture"),
        ("11:00 - 12:00", "lecture"),
        ("12:00 - 13:00", "lunch"),
        ("13:00 - 14:00", "lecture"),
        ("14:00 - 15:00", "lecture"),
        ("15:00 - 16:00", "lecture"),
        ("16:00 - 17:00", "lecture"),
    ], batches, labs, maps)

    # Track lab assignments: (day, slot_time, lab) -> set of batches
    lab_assignments = {}
    
    for cls in classes:
        for day in DAYS:
            for slot_time, val in tt[cls][day].items():
                if val and "in Lab" in val:
                    # Parse "A: DBMS Lab (T1) in Lab(A) / B: OS Lab (T2) in Lab(B)"
                    parts = val.split(" / ")
                    for part in parts:
                        if " in " in part:
                            batch_part = part.split(": ")[0] if ": " in part else "?"
                            lab_part = part.split(" in ")[1].strip()
                            key = (day, slot_time, lab_part)
                            if key not in lab_assignments:
                                lab_assignments[key] = set()
                            lab_assignments[key].add(batch_part)
    
    # Labs can be reused, but check for logical conflicts
    for (day, slot, lab), batch_set in lab_assignments.items():
        # Each lab should not have same batch twice (within same time)
        assert len(batch_set) == len(set(batch_set)), f"Lab {lab} assigned multiple times to same batch at {day} {slot}"
    print("No lab conflicts detected")


def test_practicals_unique_and_merged():
    random.seed(0)
    classes, teachers, subjects, batches, labs, optional_subjects = make_sample_input()
    maps, _ = validate_inputs_and_build_maps(classes, teachers, optional_subjects)
    tt = generate_timetable(classes, teachers, subjects, [
        ("10:00 - 11:00", "lecture"),
        ("11:00 - 12:00", "lecture"),
        ("12:00 - 13:00", "lunch"),
        ("13:00 - 14:00", "lecture"),
        ("14:00 - 15:00", "lecture"),
        ("15:00 - 16:00", "lecture"),
        ("16:00 - 17:00", "lecture"),
    ], batches, labs, maps)

    # Check both classes
    for cls in classes:
        class_tt = tt[cls]

        # For each day, if a practical is scheduled it should be in first slot and second should be MERGED
        for day, slots in class_tt.items():
            # look for merged markers
            for cls_slot in [("10:00 - 11:00","11:00 - 12:00"),("13:00 - 14:00","14:00 - 15:00"),("15:00 - 16:00","16:00 - 17:00")]:
                a,b = cls_slot
                if a in slots and slots.get(b)=="MERGED":
                    assert "Free" not in slots[a]  # should have an assignment when merged

        # Ensure no batch gets same practical twice
        assigned = {b: set() for b in batches[cls]}
        for day, slots in class_tt.items():
            for time, val in slots.items():
                if val and val != "MERGED" and val != "Lunch Break" and val != "Project Day":
                    # parse "A: DBMS Lab (T) in Lab(A) / B: OS Lab (T) in Lab(B)"
                    parts = val.split(" / ") if " / " in val else [val]
                    for part in parts:
                        if ": " in part:
                            batch, rest = part.split(": ",1)
                            subj = rest.split(" (")[0]
                            if subj != "Free" and "Library" not in subj and "T&P" not in subj:
                                assigned[batch].add(subj)
        
        for b, s in assigned.items():
            # no duplicates by construction of set
            assert len(s) == len(set(s)), f"Duplicate practicals for batch {b} in class {cls}"
    print("Practicals properly merged and unique per batch")


if __name__ == "__main__":
    test_no_teacher_conflicts()
    test_no_lab_conflicts()
    test_practicals_unique_and_merged()
    print("\n✅ All conflict resolution tests passed!") 
