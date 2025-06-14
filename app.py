import csv
import random
from flask import request, Flask, render_template, send_file

app = Flask(__name__)

def mainFunction(inputFile):
    teacher_assignments = {}
    MAX_STUDENTS_PER_TEACHER = 11
    MIN_STUDENTS_PER_TEACHER = 7
    final_assignments = []
    students = []

    # Read all students first (excluding "yes" students)
    with open(inputFile, "r") as file:
        reader = csv.reader(file)
        header = next(reader, None)
        for row in reader:
            if len(row) < 7:
                continue  # skip incomplete rows
            timestamp, last_name, first_name, grade, homeroom, yes_or_no, all_teachers = row[:7]
            if yes_or_no.strip().lower() == "yes":
                continue
            teacher_preferences = [teacher.strip() for teacher in all_teachers.split(",") if teacher.strip()]
            students.append({
                "first_name": first_name,
                "last_name": last_name,
                "grade": grade,
                "preferences": teacher_preferences
            })

    # Shuffle students to randomize assignment order
    random.shuffle(students)

    for student in students:
        teacher_preferences = student["preferences"]
        assigned_teacher = None

        # Try to assign the student to a preferred teacher randomly
        random.shuffle(teacher_preferences)
        for teacher in teacher_preferences:
            if teacher not in teacher_assignments:
                teacher_assignments[teacher] = 0
            if teacher_assignments[teacher] < MAX_STUDENTS_PER_TEACHER:
                assigned_teacher = teacher
                teacher_assignments[assigned_teacher] += 1
                break

        # If no preferred teachers are available, assign to a teacher with space
        if not assigned_teacher:
            # Find a teacher with space
            possible_teachers = [t for t, count in teacher_assignments.items() if count < MAX_STUDENTS_PER_TEACHER]
            if possible_teachers:
                assigned_teacher = min(possible_teachers, key=lambda t: teacher_assignments[t])
                teacher_assignments[assigned_teacher] += 1
            else:
                # If no teacher meets the requirement, assign to a default teacher
                assigned_teacher = "Default Teacher"
                teacher_assignments[assigned_teacher] = teacher_assignments.get(assigned_teacher, 0) + 1

        final_assignments.append((student["first_name"], student["last_name"], student["grade"], assigned_teacher))

    # Print a formatted table of assignments
    print("\nFinal Student Assignments:")
    print(f"{'First Name':<15}{'Last Name':<15}{'Grade':<10}{'Advisor Name':<20}")
    print("-" * 60)
    for first_name, last_name, grade, assigned_teacher in final_assignments:
        print(f"{first_name:<15}{last_name:<15}{grade:<10}{assigned_teacher:<20}")

    # Print final teacher counts
    print("\nFinal Teacher Assignment Counts:")
    print(f"{'Teacher':<20}{'Number of Students':<20}")
    print("-" * 40)
    for teacher, count in teacher_assignments.items():
        print(f"{teacher:<20}{count:<20}")

    # Write final assignments to a CSV
    output_file = '/tmp/final_assignments.csv'
    with open(output_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["First Name", "Last Name", "Grade", "Advisor Name"])
        for first_name, last_name, grade, assigned_teacher in final_assignments:
            writer.writerow([first_name, last_name, grade, assigned_teacher])

    return output_file

@app.route('/')
def mainPage():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No file selected", 400
    temp_file = '/tmp/uploaded_file.csv'
    file.save(temp_file)
    result = mainFunction(temp_file)
    return send_file(result, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
