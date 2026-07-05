from algorithm import validate_inputs_and_build_maps, generate_timetable

classes = ['SE']
teachers = [{'name':'PK', 'fullName':'Dr. Pankaj K.', 'subjects':['AI']}]
subjects = {'SE': {'lectures': ['AI'], 'practicals': []}}
batches = {'SE': ['A']}
labs = ['AI Lab']

maps, err = validate_inputs_and_build_maps(classes, teachers, [])
print('maps err', err)
print('subject_teacher', maps['subject_teacher'])
try:
    tt = generate_timetable(classes, teachers, subjects, [('10:00 - 11:00', 'lecture')], batches, labs, maps)
    print('tt', tt)
except Exception as e:
    import traceback
    traceback.print_exc()
