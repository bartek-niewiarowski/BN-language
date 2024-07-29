# plik: student.py

class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def greet(self):
        return f"Hello, my name is {self.name} and I am {self.age} years old."

class Class:
    def __init__(self, students, teacher) -> None:
        self._students = students
        self._teacher = teacher
    
    def getStudents(self):
        return self._students
    
    def getTeacher(self):
        return self._teacher

    def setStudents(self, students):
        self._students = students
    
    def setTeacher(self, teacher):
        self._teacher = teacher
