import json
import os
from datetime import datetime

DATA_FILE = "erp_data.json"

# ------------------ Data Handling ------------------
def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
        else:
            data = {"streams": {}, "student_counter": 1, "faculty_counter": 1}
    except (IOError, json.JSONDecodeError) as e:
        print(f"⚠️ Error loading data: {e}")
        data = {"streams": {}, "student_counter": 1, "faculty_counter": 1}

    # Ensure counters exist (for backward compatibility)
    if "student_counter" not in data:
        data["student_counter"] = 1
    if "faculty_counter" not in data:
        data["faculty_counter"] = 1

    # Auto-migrate students if stored as list
    for stream, sdata in data.get("streams", {}).items():
        for cls, cls_data in sdata.get("classes", {}).items():
            if isinstance(cls_data.get("students"), list):
                new_students = {}
                for i, name in enumerate(cls_data["students"], start=1):
                    sid = f"STU{data['student_counter']:03d}"
                    data["student_counter"] += 1
                    new_students[sid] = {"name": name}
                cls_data["students"] = new_students

    return data

def save_data(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"⚠️ Error saving data: {e}")

def backup_data(data):
    backup_file = f"erp_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(backup_file, "w") as f:
            json.dump(data, f, indent=4)
        print(f"✅ Backup created: {backup_file}")
        return True
    except IOError as e:
        print(f"⚠️ Error creating backup: {e}")
        return False


# ------------------ Utility ------------------
def get_valid_input(prompt, input_type=str, validation_func=None, allow_empty=False):
    while True:
        try:
            value = input(prompt).strip()
            if allow_empty and not value:
                return None
            if not value and not allow_empty:
                print("⚠️ This field cannot be empty!")
                continue
                
            if input_type != str:
                value = input_type(value)
                
            if validation_func and not validation_func(value):
                raise ValueError
            return value
        except ValueError:
            print("⚠️ Invalid input! Please try again.")

def select_option(options, title="Choose an option", allow_back=False):
    """Helper to display numbered menu from a list/dict keys"""
    if not options:
        print("⚠️ Nothing available!")
        return None
        
    print(f"\n--- {title} ---")
    options_list = list(options)
    
    for i, opt in enumerate(options_list, 1):
        print(f"{i}. {opt}")
        
    if allow_back:
        print(f"{len(options_list) + 1}. Back")
    
    try:
        choice = get_valid_input("Enter choice: ", int)
        if allow_back and choice == len(options_list) + 1:
            return None
            
        if 1 <= choice <= len(options_list):
            return options_list[choice - 1]
        else:
            print("⚠️ Invalid choice!")
            return None
    except ValueError:
        print("⚠️ Enter a number!")
        return None


# ------------------ ERP Operations ------------------
def add_stream(data):
    stream_name = get_valid_input("Enter stream name (e.g. BCA, BSc IT): ", validation_func=lambda x: len(x) > 0)
    if stream_name not in data["streams"]:
        data["streams"][stream_name] = {"classes": {}, "faculty": {}}
        print(f"✅ Stream '{stream_name}' added.")
    else:
        print("⚠️ Stream already exists!")

def add_class(data):
    stream = select_option(data["streams"], "Select Stream", allow_back=True)
    if not stream:
        return
        
    class_name = get_valid_input("Enter class (e.g. 1A, 2B): ", validation_func=lambda x: len(x) > 0)
    if class_name not in data["streams"][stream]["classes"]:
        data["streams"][stream]["classes"][class_name] = {"students": {}}
        print(f"✅ Class '{class_name}' added in {stream}.")
    else:
        print("⚠️ Class already exists!")

def add_student(data):
    stream = select_option(data["streams"], "Select Stream", allow_back=True)
    if not stream:
        return
        
    classes = data["streams"][stream]["classes"]
    if not classes:
        print("⚠️ No classes available in this stream!")
        return
        
    class_name = select_option(classes, f"Select Class in {stream}", allow_back=True)
    if not class_name:
        return
        
    student_name = get_valid_input("Enter student name: ", validation_func=lambda x: len(x) > 0)
    student_id = f"STU{data['student_counter']:03d}"
    data["student_counter"] += 1
    classes[class_name]["students"][student_id] = {"name": student_name}
    print(f"✅ Student '{student_name}' (ID: {student_id}) added to {stream} - {class_name}.")

def add_faculty(data):
    stream = select_option(data["streams"], "Select Stream", allow_back=True)
    if not stream:
        return
        
    faculty_name = get_valid_input("Enter faculty name: ", validation_func=lambda x: len(x) > 0)
    faculty_id = f"FAC{data['faculty_counter']:03d}"
    data["faculty_counter"] += 1
    data["streams"][stream]["faculty"][faculty_id] = {
        "name": faculty_name,
        "assigned_class": None,
    }
    print(f"✅ Faculty '{faculty_name}' (ID: {faculty_id}) added in {stream}.")

def assign_faculty(data):
    stream = select_option(data["streams"], "Select Stream", allow_back=True)
    if not stream:
        return
        
    faculty_list = data["streams"][stream]["faculty"]
    if not faculty_list:
        print("⚠️ No faculty available in this stream!")
        return
        
    faculty = select_option(faculty_list, "Select Faculty", allow_back=True)
    if not faculty:
        return
        
    classes = data["streams"][stream]["classes"]
    if not classes:
        print("⚠️ No classes available in this stream!")
        return
        
    class_name = select_option(classes, f"Select Class in {stream}", allow_back=True)
    if not class_name:
        return
        
    data["streams"][stream]["faculty"][faculty]["assigned_class"] = class_name
    print(
        f"✅ Faculty '{data['streams'][stream]['faculty'][faculty]['name']}' "
        f"assigned to {stream} - {class_name}."
    )

def remove_stream(data):
    stream = select_option(data["streams"], "Select Stream to Remove", allow_back=True)
    if not stream:
        return
        
    confirm = get_valid_input(f"Are you sure you want to remove stream '{stream}'? (y/n): ", 
                             validation_func=lambda x: x.lower() in ['y', 'n'])
    if confirm.lower() == 'y':
        del data["streams"][stream]
        print(f"✅ Stream '{stream}' removed.")
    else:
        print("❌ Stream removal cancelled.")

def remove_class(data):
    stream = select_option(data["streams"], "Select Stream", allow_back=True)
    if not stream:
        return
        
    classes = data["streams"][stream]["classes"]
    if not classes:
        print("⚠️ No classes available in this stream!")
        return
        
    class_name = select_option(classes, f"Select Class to Remove from {stream}", allow_back=True)
    if not class_name:
        return
        
    # Check if any faculty is assigned to this class
    faculty_assigned = False
    for faculty in data["streams"][stream]["faculty"].values():
        if faculty["assigned_class"] == class_name:
            faculty_assigned = True
            break
            
    if faculty_assigned:
        print("⚠️ Cannot remove class - faculty members are assigned to it!")
        return
        
    confirm = get_valid_input(f"Are you sure you want to remove class '{class_name}'? (y/n): ", 
                             validation_func=lambda x: x.lower() in ['y', 'n'])
    if confirm.lower() == 'y':
        del data["streams"][stream]["classes"][class_name]
        print(f"✅ Class '{class_name}' removed from {stream}.")
    else:
        print("❌ Class removal cancelled.")

def remove_student(data):
    stream = select_option(data["streams"], "Select Stream", allow_back=True)
    if not stream:
        return
        
    classes = data["streams"][stream]["classes"]
    if not classes:
        print("⚠️ No classes available in this stream!")
        return
        
    class_name = select_option(classes, f"Select Class in {stream}", allow_back=True)
    if not class_name:
        return
        
    students = classes[class_name]["students"]
    if not students:
        print("⚠️ No students in this class!")
        return
        
    student_id = select_option(students, "Select Student to Remove", allow_back=True)
    if not student_id:
        return
        
    confirm = get_valid_input(f"Are you sure you want to remove student '{students[student_id]['name']}'? (y/n): ", 
                             validation_func=lambda x: x.lower() in ['y', 'n'])
    if confirm.lower() == 'y':
        del classes[class_name]["students"][student_id]
        print(f"✅ Student removed from {stream} - {class_name}.")
    else:
        print("❌ Student removal cancelled.")

def remove_faculty(data):
    stream = select_option(data["streams"], "Select Stream", allow_back=True)
    if not stream:
        return
        
    faculty_list = data["streams"][stream]["faculty"]
    if not faculty_list:
        print("⚠️ No faculty available in this stream!")
        return
        
    faculty_id = select_option(faculty_list, "Select Faculty to Remove", allow_back=True)
    if not faculty_id:
        return
        
    confirm = get_valid_input(f"Are you sure you want to remove faculty '{faculty_list[faculty_id]['name']}'? (y/n): ", 
                             validation_func=lambda x: x.lower() in ['y', 'n'])
    if confirm.lower() == 'y':
        del data["streams"][stream]["faculty"][faculty_id]
        print(f"✅ Faculty removed from {stream}.")
    else:
        print("❌ Faculty removal cancelled.")

def search_student(data):
    name = get_valid_input("Enter student name to search: ", allow_empty=True)
    if not name:
        return
        
    name = name.lower()
    found = False
    
    for stream, details in data["streams"].items():
        for cls, cls_data in details["classes"].items():
            for sid, sdata in cls_data["students"].items():
                if name in sdata["name"].lower():
                    print(f"Found: {sdata['name']} (ID: {sid}) in {stream} - {cls}")
                    found = True
    
    if not found:
        print("No students found with that name.")

def search_faculty(data):
    name = get_valid_input("Enter faculty name to search: ", allow_empty=True)
    if not name:
        return
        
    name = name.lower()
    found = False
    
    for stream, details in data["streams"].items():
        for fid, fdata in details["faculty"].items():
            if name in fdata["name"].lower():
                print(f"Found: {fdata['name']} (ID: {fid}) in {stream} - Assigned to: {fdata['assigned_class']}")
                found = True
    
    if not found:
        print("No faculty found with that name.")

def view_data(data):
    if not data["streams"]:
        print("No data available. Add streams, classes, students, and faculty first.")
        return
        
    for stream, details in data["streams"].items():
        print(f"\n📘 Stream: {stream}")

        # Show classes and students
        print("   Classes & Students:")
        if details["classes"]:
            for cls, cls_data in details["classes"].items():
                print(f"     • {cls}:")
                students = cls_data["students"]
                if students:
                    for sid, sdata in students.items():
                        print(f"         - {sid}: {sdata['name']}")
                else:
                    print("         (No students yet)")
        else:
            print("     (No classes yet)")

        # Show faculty
        print("   Faculty:")
        if details["faculty"]:
            for fid, fac_data in details["faculty"].items():
                print(
                    f"     • {fid}: {fac_data['name']} "
                    f"(Assigned Class: {fac_data['assigned_class'] or 'None'})"
                )
        else:
            print("     (No faculty yet)")

def view_faculty_without_assignments(data):
    found = False
    for stream, details in data["streams"].items():
        for fid, fac_data in details["faculty"].items():
            if not fac_data["assigned_class"]:
                print(f"{fid}: {fac_data['name']} in {stream} (No assignment)")
                found = True
    
    if not found:
        print("All faculty members have assignments.")

def view_classes_without_faculty(data):
    found = False
    for stream, details in data["streams"].items():
        for cls in details["classes"]:
            # Check if any faculty is assigned to this class
            faculty_assigned = False
            for faculty in details["faculty"].values():
                if faculty["assigned_class"] == cls:
                    faculty_assigned = True
                    break
                    
            if not faculty_assigned:
                print(f"{stream} - {cls}: No faculty assigned")
                found = True
    
    if not found:
        print("All classes have faculty assignments.")


# ------------------ Menu ------------------
def main():
    data = load_data()

    while True:
        print("\n--- Educational ERP ---")
        print("1. Add Stream")
        print("2. Add Class")
        print("3. Add Student")
        print("4. Add Faculty")
        print("5. Assign Faculty to Class")
        print("6. View All Data")
        print("7. Remove Stream")
        print("8. Remove Class")
        print("9. Remove Student")
        print("10. Remove Faculty")
        print("11. Search Student")
        print("12. Search Faculty")
        print("13. View Unassigned Faculty")
        print("14. View Classes Without Faculty")
        print("15. Create Backup")
        print("16. Exit")

        choice = get_valid_input("Enter choice: ", int)

        if choice == 1:
            add_stream(data)
        elif choice == 2:
            add_class(data)
        elif choice == 3:
            add_student(data)
        elif choice == 4:
            add_faculty(data)
        elif choice == 5:
            assign_faculty(data)
        elif choice == 6:
            view_data(data)
        elif choice == 7:
            remove_stream(data)
        elif choice == 8:
            remove_class(data)
        elif choice == 9:
            remove_student(data)
        elif choice == 10:
            remove_faculty(data)
        elif choice == 11:
            search_student(data)
        elif choice == 12:
            search_faculty(data)
        elif choice == 13:
            view_faculty_without_assignments(data)
        elif choice == 14:
            view_classes_without_faculty(data)
        elif choice == 15:
            backup_data(data)
        elif choice == 16:
            save_data(data)
            print("💾 Data saved. Exiting...")
            break
        else:
            print("⚠️ Invalid choice!")


if __name__ == "__main__":
    main()
