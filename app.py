import csv
import random
from flask import request, Flask, render_template, send_file

app = Flask(__name__)

def mainFunction(inputFile):
    # Dictionary to track teacher assignments
    teacher_assignments = {}

    # Maximum and minimum number of students per teacher
    MAX_STUDENTS_PER_TEACHER = 11
    MIN_STUDENTS_PER_TEACHER = 7

    # List to store final assignments
    final_assignments = []

    # Open the CSV file
    with open(inputFile, "r") as file:
        reader = csv.reader(file)
        index = 0  # To track rows

        for row in reader:
            # Skip the header row
            if index == 0:
                index += 1
                continue

            # Read row data
            timestamp, last_name, first_name, grade, homeroom, yes_or_no, all_teachers = row[:7]

            # Skip students with "Yes" in yes_or_no
            if yes_or_no.strip().lower() == "yes":
                continue

            # Split teacher preferences into a list
            teacher_preferences = [teacher.strip() for teacher in all_teachers.split(",") if teacher.strip()]

            # Try to assign the student to a preferred teacher randomly
            assigned_teacher = None
            random.shuffle(teacher_preferences)
            for teacher in teacher_preferences:
                if teacher not in teacher_assignments:
                    teacher_assignments[teacher] = 0

                if teacher_assignments[teacher] < MAX_STUDENTS_PER_TEACHER:
                    assigned_teacher = teacher
                    teacher_assignments[assigned_teacher] += 1
                    break

            # If no preferred teachers are available, assign to a teacher with fewer than 11 students and at least 7
            if not assigned_teacher:
                least_loaded_teacher = None
                least_students = MAX_STUDENTS_PER_TEACHER + 1

                # Find a teacher with space and with at least 7 students
                for teacher, count in teacher_assignments.items():
                    if count <= 3:
                        least_loaded_teacher = teacher
                        break
                    if count < least_students:
                        least_loaded_teacher = teacher
                        least_students = count

                if least_loaded_teacher:
                    assigned_teacher = least_loaded_teacher
                    teacher_assignments[assigned_teacher] += 1
                else:
                    # If no teacher meets the requirement, assign to any teacher with the least number of students
                    least_loaded_teacher = "Default Teacher"
                    teacher_assignments[least_loaded_teacher] = 0
                    assigned_teacher = least_loaded_teacher
                    teacher_assignments[assigned_teacher] += 1

            # if any of the teachers do not have any students assigned, remove students from the most loaded teacher and assign to the teacher

            # equalize the number of students assigned to each teacher by moving students from the most loaded teacher to the least loaded teacher
            while max(teacher_assignments.values()) - min(teacher_assignments.values()) > 1:
                most_loaded_teacher = max(teacher_assignments, key=teacher_assignments.get)
                least_loaded_teacher = min(teacher_assignments, key=teacher_assignments.get)
                teacher_assignments[most_loaded_teacher] -= 1
                teacher_assignments[least_loaded_teacher] += 1

            # Add the student to the final assignments list
            final_assignments.append((first_name, last_name, grade, assigned_teacher))
        
        # if the student does not have any teacher preference, assign to a teacher with fewer than 7 students
        if len(teacher_preferences) == 0:
            least_loaded_teacher = None
            least_students = MAX_STUDENTS_PER_TEACHER + 1

            # Find a teacher who has less than 7 students
            for teacher, count in teacher_assignments.items():
                if count < MIN_STUDENTS_PER_TEACHER:
                    least_loaded_teacher = teacher
                    break
                if count < least_students:
                    least_loaded_teacher = teacher
                    least_students = count

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

    # format the final assignments into a .csv file

    # Create a new CSV file
    output_file = '/tmp/final_assignments.csv'
    with open(output_file, "w", newline="") as file:
        writer = csv.writer(file)

        # Write the header row
        writer.writerow(["First Name", "Last Name", "Grade", "Advisor Name"])

        # Write the data rows
        for first_name, last_name, grade, assigned_teacher in final_assignments:
            writer.writerow([first_name, last_name, grade, assigned_teacher])

    return output_file


@app.route('/')
def mainPage():
    # Renders the HTML form
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if a file was uploaded
    if 'file' not in request.files:
        return print ("No file part"), 400

    file = request.files['file']
    if file.filename == '':
        return print ("No file selected"), 400

    # Save the uploaded file to a temporary location
    temp_file = '/tmp/uploaded_file.csv'
    file.save(temp_file)

    # Call the main function with the uploaded file
    result = mainFunction(temp_file)

    # download url 
    downLoadUrl = f"<a href='{result}' download='finalOutput'>here</a>"


    return send_file('/tmp/final_assignments.csv', as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)