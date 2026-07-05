import random
from algorithm import generate_timetable, validate_inputs_and_build_maps


def make_input_no_practicals():
    classes = ["BE"]
    teachers = [ {"name":"T1","subjects":["Math"]} ]
    subjects = {"BE": {"lectures":["Math"], "practicals":[]}}
    batches = {"BE":["A"]}
    labs = ["Lab(A)"]
    optional_subjects = []
    return classes, teachers, subjects, batches, labs, optional_subjects


def test_no_practicals_generates_lectures_and_project_day():
    random.seed(1)
    classes, teachers, subjects, batches, labs, optional_subjects = make_input_no_practicals()
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

    be = tt["BE"]
    # No project days should appear
    for day, slots in be.items():
        for val in slots.values():
            assert "Project Day" not in str(val), f"Unexpected project entry on {day}: {val}"

    # Since no practicals exist, merged markers should not appear
    for day, slots in be.items():
        assert 'MERGED' not in slots.values()

def test_practical_merges_use_marker():
    """When practicals are defined we should see at least one MERGED marker.
    This ensures the backend still flags two-hour slots for the UI to merge.
    """
    random.seed(2)
    classes = ["BE"]
    teachers = [{"name": "T1", "subjects": ["Physics"]}]
    subjects = {"BE": {"lectures": ["Physics"], "practicals": ["Physics Lab"]}}
    batches = {"BE": ["A"]}
    labs = ["Lab(A)"]
    optional_subjects = []
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

    merged_found = False
    for day, slots in tt["BE"].items():
        if any(val == 'MERGED' for val in slots.values()):
            merged_found = True
    assert merged_found, "Expected at least one MERGED slot for practicals"