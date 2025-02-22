import unify
unify.activate("entries-context", overwrite=True)
all_student_data = {
    "Maths": {
        "A": [
            ("Alice", "Smith", "23/04/2005"),
            ("Bob", "Johnson", "12/07/2004"),
        ],
        "B": [
            ("Eve", "Brown", "15/09/2003"),
            ("Frank", "Jones", "22/11/2005"),
        ],
        "C": [
            ("Henry", "Miller", "01/01/2004"),
            ("Ian", "Davis", "10/03/2005"),
        ],
    },
    "Physics": {
        "A": [
            ("Frank", "Jones", "22/11/2005"),
        ],
        "B": [
            ("Alice", "Smith", "23/04/2005"),
            ("Eve", "Brown", "15/09/2003"),
            ("Henry", "Miller", "01/01/2004"),
            ("Ian", "Davis", "10/03/2005"),
        ],
        "C": [
            ("Bob", "Johnson", "12/07/2004"),
        ],
    },
}
for subject, studate_data in all_student_data.items():
    for grade, students in studate_data.items():
        for first_name, last_name, dob in students:
            unify.log(
                subject=subject,
                grade=grade,
                first_name=first_name,
                last_name=last_name, 
                data_of_birth=dob
            )
