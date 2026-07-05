import sys
sys.path.insert(0, 'c:/Users/Lenovo/Downloads/newtb_comp/newtb')
from algorithm import (
    generate_timetable, 
    validate_inputs_and_build_maps, 
    DAYS,
    TIMESLOTS,
)

# Your actual data
classes = ["SE", "TE", "BE"]
teachers = [
    {"name": "KMG", "fullName": "Kranti M Gajmal", "subjects": ["DS", "AOA"]},
    {"name": "SST", "fullName": "Sameer S Tathare", "subjects": ["DSGT", "CN"]},
    {"name": "SDL", "fullName": "Sachin D Latkar", "subjects": ["DLOC", "CSL"]},
    {"name": "JVK", "fullName": "Jyoti V Khalkar", "subjects": ["CG", "ADS"]},
    {"name": "VNR", "fullName": "Vaishali N Rane", "subjects": ["DBMS", "SMA"]},
    {"name": "SFS", "fullName": "Swaleha F Shaikh", "subjects": ["BDA", "DC"]},
    {"name": "STK", "fullName": "Sandeep T Kelkar", "subjects": ["DBM"]},
]

subjects = {
    "SE": {
        "lectures": ["DS", "CG", "DLOC", "DSGT", "DBMS"],
        "practicals": ["DS Lab", "CG Lab", "DLOC Lab", "DBMS Lab"]
    },
    "TE": {
        "lectures": ["AOA", "BDA", "CN", "CSL"],
        "practicals": ["AOA Lab", "BDA Lab", "CN Lab", "CSL Lab"]
    },
    "BE": {
        "lectures": ["SMA", "ADS", "DBM", "DC"],
        "practicals": ["SMA Lab", "ADS Lab", "DBM Lab", "DC Lab"]
    }
}

timeslots = TIMESLOTS
batches = {"SE": ["B1", "B2", "B3", "B4"], "TE": ["B1", "B2", "B3", "B4"], "BE": ["B1", "B2", "B3", "B4"]}
labs = ["Lab1", "Lab2", "Lab3", "Lab4"]

maps, _ = validate_inputs_and_build_maps(classes, teachers, [])

print("\n=== TEACHER-CLASS MAPPING ===")
teacher_classes = {}
for t in teachers:
    classes_for_teacher = set()
    for subj in t["subjects"]:
        if subj in subjects["SE"]["lectures"] or subj + " Lab" in subjects["SE"]["practicals"]:
            classes_for_teacher.add("SE")
        if subj in subjects["TE"]["lectures"] or subj + " Lab" in subjects["TE"]["practicals"]:
            classes_for_teacher.add("TE")
        if subj in subjects["BE"]["lectures"] or subj + " Lab" in subjects["BE"]["practicals"]:
            classes_for_teacher.add("BE")
    teacher_classes[t["name"]] = classes_for_teacher
    print(f"{t['name']} ({t['fullName']}): teaches {', '.join(sorted(classes_for_teacher))}")

print("\n=== CHECKING FOR OVERLAPS ===\n")

overlap_count = 0
total_checks = 0

for gen in range(10):
    timetable = generate_timetable(classes, teachers, subjects, timeslots, batches, labs, maps)
    
    print(f"\n--- Generation {gen + 1} ---")
    gen_overlap = 0
    
    # Check each teacher for overlaps
    for teacher in teachers:
        tname = teacher["name"]
        teacher_schedule = {}  # day -> slot -> [(class, activity)]
        
        for cls in classes:
            for day in DAYS:
                if day not in teacher_schedule:
                    teacher_schedule[day] = {}
                    
                for slot_time in TIMESLOTS:
                    slot = slot_time[0]
                    entry = timetable[cls][day].get(slot, "")
                    
                    if tname in entry:
                        if slot not in teacher_schedule[day]:
                            teacher_schedule[day][slot] = []
                        teacher_schedule[day][slot].append((cls, entry[:60]))
        
        # Check for overlaps
        for day in DAYS:
            for slot, activities in teacher_schedule[day].items():
                total_checks += 1
                if len(activities) > 1:
                    gen_overlap += 1
                    overlap_count += 1
                    if gen == 0:  # Only show details for first generation
                        print(f"\nOVERLAP: {tname} on {day} at {slot}:")
                        for cls, activity in activities:
                            print(f"  - {cls}: {activity}")
    
    if gen_overlap == 0:
        print("✓ No overlaps detected!")
    else:
        print(f"⚠ {gen_overlap} overlaps found")

print(f"\n=== SUMMARY ===")
print(f"Total overlap checks: {total_checks}")
print(f"Total overlaps found: {overlap_count}")
if overlap_count == 0:
    print("✓✓✓ ALL OVERLAPS RESOLVED! ✓✓✓")
else:
    print(f"⚠ Still have {overlap_count} overlaps to fix")
