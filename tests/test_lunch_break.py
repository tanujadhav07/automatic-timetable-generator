"""
Test to verify lunch break is properly enforced for all classes
12:00 - 13:00 should be 'Lunch Break' for every class, every day
"""

import pytest
import sys

sys.path.insert(0, '/c:/Users/Lenovo/Downloads/newtb_comp/newtb')
from algorithm import (
    generate_timetable, 
    validate_inputs_and_build_maps, 
    DAYS,
    TIMESLOTS,
    get_lunch_slot,
)


def test_lunch_break_enforced_all_classes():
    """Verify 12:00-13:00 is always 'Lunch Break' for ALL classes"""
    
    # Setup test data
    classes = ["SE", "TE", "BE"]
    teachers = [
        {"name": "T1", "subjects": ["S1", "S2"]},
        {"name": "T2", "subjects": ["S3", "S4"]},
        {"name": "T3", "subjects": ["S5", "S6"]}
    ]
    subjects = {
        "SE": {"lectures": ["S1", "S2"], "practicals": ["P1", "P2"]},
        "TE": {"lectures": ["S3", "S4"], "practicals": ["P3", "P4"]},
        "BE": {"lectures": ["S5", "S6"], "practicals": ["P5", "P6"]}
    }
    timeslots = TIMESLOTS
    batches = {"SE": ["A", "B"], "TE": ["A", "B"], "BE": ["A", "B"]}
    labs = ["Lab1", "Lab2"]
    
    # Build maps
    maps, _ = validate_inputs_and_build_maps(classes, teachers, [])
    
    # Generate timetable
    timetable = generate_timetable(classes, teachers, subjects, timeslots, batches, labs, maps)
    
    # Verify lunch break for all classes, all days
    for cls in classes:
        lunch_slot = get_lunch_slot(cls)
        for day in DAYS:
            # Check that lunch slot exists
            assert lunch_slot in timetable[cls][day], \
                f"{cls} missing lunch slot on {day}"
            # Check that it's marked only as "Lunch Break"
            lunch_entry = timetable[cls][day][lunch_slot]
            assert lunch_entry == "Lunch Break", \
                f"{cls} on {day}: Expected 'Lunch Break' but got '{lunch_entry}'"


def test_lunch_break_no_activities_during_12_13():
    """Verify no classes/teachers are scheduled during lunch"""
    
    classes = ["SE", "TE", "BE"]
    teachers = [
        {"name": "Kranti", "subjects": ["S1", "S2"]},
        {"name": "John", "subjects": ["S3", "S4"]},
        {"name": "Sarah", "subjects": ["S5", "S6"]}
    ]
    subjects = {
        "SE": {"lectures": ["S1", "S2"], "practicals": ["P1", "P2"]},
        "TE": {"lectures": ["S3", "S4"], "practicals": ["P3", "P4"]},
        "BE": {"lectures": ["S5", "S6"], "practicals": ["P5", "P6"]}
    }
    timeslots = TIMESLOTS
    batches = {"SE": ["A", "B"], "TE": ["A", "B"], "BE": ["A", "B"]}
    labs = ["Lab1", "Lab2"]
    
    maps, _ = validate_inputs_and_build_maps(classes, teachers, [])
    timetable = generate_timetable(classes, teachers, subjects, timeslots, batches, labs, maps)
    
    # Verify no activities during lunch
    for cls in classes:
        lunch_slot = get_lunch_slot(cls)
        for day in DAYS:
            entry = timetable[cls][day][lunch_slot]
            
            # Lunch should always be the protected break
            assert entry == "Lunch Break", \
                f"{cls} on {day} has unexpected value during lunch: '{entry}'"
            # ensure there is no subject/teacher text
            assert "(" not in entry, \
                f"{cls} on {day} has activity during lunch: {entry}"


def test_lunch_break_consistency():
    """Verify lunch break is consistent across multiple generations"""
    
    classes = ["SE", "TE", "BE"]
    teachers = [
        {"name": "T1", "subjects": ["S1", "S2"]},
        {"name": "T2", "subjects": ["S3", "S4"]},
        {"name": "T3", "subjects": ["S5", "S6"]}
    ]
    subjects = {
        "SE": {"lectures": ["S1", "S2"], "practicals": ["P1", "P2"]},
        "TE": {"lectures": ["S3", "S4"], "practicals": ["P3", "P4"]},
        "BE": {"lectures": ["S5", "S6"], "practicals": ["P5", "P6"]}
    }
    timeslots = TIMESLOTS
    batches = {"SE": ["A", "B"], "TE": ["A", "B"], "BE": ["A", "B"]}
    labs = ["Lab1", "Lab2"]
    
    maps, _ = validate_inputs_and_build_maps(classes, teachers, [])
    
    # Generate 3 times and verify lunch is always there
    for attempt in range(3):
        timetable = generate_timetable(classes, teachers, subjects, timeslots, batches, labs, maps)
        
        for cls in classes:
            lunch_slot = get_lunch_slot(cls)
            for day in DAYS:
                assert timetable[cls][day][lunch_slot] == "Lunch Break", \
                    f"Attempt {attempt}: {cls} on {day} missing lunch break"


def test_lunch_break_position():
    """Verify 12:00-13:00 is always in the middle of the day"""
    
    classes = ["SE", "TE", "BE"]
    teachers = [
        {"name": "T1", "subjects": ["S1", "S2"]},
        {"name": "T2", "subjects": ["S3", "S4"]},
        {"name": "T3", "subjects": ["S5", "S6"]}
    ]
    subjects = {
        "SE": {"lectures": ["S1", "S2"], "practicals": ["P1", "P2"]},
        "TE": {"lectures": ["S3", "S4"], "practicals": ["P3", "P4"]},
        "BE": {"lectures": ["S5", "S6"], "practicals": ["P5", "P6"]}
    }
    timeslots = TIMESLOTS
    batches = {"SE": ["A", "B"], "TE": ["A", "B"], "BE": ["A", "B"]}
    labs = ["Lab1", "Lab2"]
    
    maps, _ = validate_inputs_and_build_maps(classes, teachers, [])
    timetable = generate_timetable(classes, teachers, subjects, timeslots, batches, labs, maps)
    
    # verify position relative to neighboring slots for each class
    for cls in classes:
        lunch_slot = get_lunch_slot(cls)
        slot_times = [t[0] for t in TIMESLOTS]
        idx = slot_times.index(lunch_slot)
        morning_slot = slot_times[idx - 1] if idx > 0 else None
        afternoon_slot = slot_times[idx + 1] if idx < len(slot_times) - 1 else None
        
        for day in DAYS:
            lunch_entry = timetable[cls][day][lunch_slot]
            assert lunch_entry == "Lunch Break", \
                f"{cls} on {day}: lunch slot is '{lunch_entry}'"
            # ensure neighboring slots are not the same as lunch
            if morning_slot:
                mval = timetable[cls][day].get(morning_slot)
                if mval is not None:
                    assert mval != lunch_entry, \
                        f"{cls} on {day}: morning same as lunch"
            if afternoon_slot:
                aval = timetable[cls][day].get(afternoon_slot)
                if aval is not None:
                    assert aval != lunch_entry, \
                        f"{cls} on {day}: afternoon same as lunch"
    pytest.main([__file__, "-v"])
