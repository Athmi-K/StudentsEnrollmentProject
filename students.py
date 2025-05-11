from sqlmodel import Field,SQLModel,Session,create_engine,select,Relationship
from typing import List,Optional
from datetime import datetime,timezone
class StudentCourseLink(SQLModel,table=True):
    student_id:int=Field(foreign_key="student.id",primary_key=True)
    course_id:int=Field(foreign_key="course.id",primary_key=True)
    enrollment_date:Optional[datetime]=None
    grade:Optional[str]=None
class Student(SQLModel,table=True):
    id:int|None=Field(default=None,primary_key=True)
    first_name:str
    last_name:str
    email:str=Field(unique=True)
    courses:List["Course"]=Relationship(back_populates="students",link_model=StudentCourseLink)
class Course(SQLModel,table=True):
    id:int|None=Field(default=None,primary_key=True)
    title:str=Field(index=True)
    code:str=Field(unique=True)
    department_id:int|None=Field(default=None,foreign_key="department.id")
    department:Optional["Department"]=Relationship(back_populates="courses")
    students:List[Student]=Relationship(back_populates="courses",link_model=StudentCourseLink)
class Department(SQLModel,table=True):
    id:int|None=Field(default=None,primary_key=True)
    name:str=Field(unique=True)
    building:str|None
    courses:List[Course] = Relationship(back_populates="department")
sqlFileName="StudentDetailss.db"
engine=create_engine(f"sqlite:///{sqlFileName}",echo=True)
def createAll():
    SQLModel.metadata.create_all(engine)
def create_department(id:int,name:str,building:str):
    with Session(engine) as session:
        details=Department(id=id,name=name,building=building)
        session.add_all([details])
        session.commit()
        print(f"Details:{details}")
def create_student(id:int,first_name:str,last_name:str,email:str):
    with Session(engine) as session:
        studetail=Student(id=id,first_name=first_name,last_name=last_name,email=email)
        session.add_all([studetail])
        session.commit()
        print(f"Details:{studetail}")
def create_course(id:int,title:str,code:str,department_id:int):
    with Session(engine) as session:
        coursedetail=Course(id=id,title=title,code=code,department_id=department_id)
        session.add_all([coursedetail])
        session.commit()
        print(f"Details:{coursedetail}")
def get_department_by_name(name:str):
    with Session(engine) as session:
        try:
            parts=name.split(sep=" ")
            first,last=parts
            statement=select(Student).where(Student.first_name==first,Student.last_name==last)
            result=session.exec(statement).first()
            for course in result.courses:
                print(course.title)
                if course.department:
                    print(f"Department:{course.department.name} Building:{course.department.building}")
        except Exception as e:
            print("Error",e)
def get_student_by_email(email:str):
    with Session(engine) as session:
        try:
            statement=select(Student).where(Student.email==email)
            student=session.exec(statement).first()
            if student:
                print(f"Student Details:{student.first_name},{student.last_name},{student.id}")
            else:
                print("No student found")
        except Exception as e:
            print("Error",e)
def get_course_by_code(code:str):
    with Session(engine) as session:
        try:
            statement=select(Course).where(Course.code==code)
            course=session.exec(statement).first()
            if course:
                print(f"Course Details:{course.id},{course.title}")
            else:
                print("No course is found")
        except Exception as e:
            print("Error",e)
def list_all_students():
    with Session(engine) as session:
        try:
            statement=select(Student)
            result=session.exec(statement)
            for students in result:
                print(f"{students.id}{students.first_name} {students.last_name}{students.email}")
        except Exception as e:
            print("Error",e)
def list_all_Courses():
    with Session(engine) as session:
        try:
            statement=select(Course)
            result=session.exec(statement)
            for courses in result:
                print(f"{courses.id} {courses.title} {courses.code} {courses.department_id}")
        except Exception as e:
            print("Error",e)
def list_all_departments():
    with Session(engine) as session:
        try:
            statement=select(Department)
            result=session.exec(statement)
            for department in result:
                print(f"{department.id} {department.building} {department.name}")
        except Exception as e:
            print("Error",e)
def update_student_email(name:str,new_email:str):
    with Session(engine) as session:
        try:
            statement=select(Student).where(Student.first_name==name)
            student=session.exec(statement).first()
            if student:
                print("Result Got")
                student.email=new_email
                session.commit()
                session.refresh(student)
                print("Email Updated")
            else:
                print("No such Student having same name ")
        except Exception as e:
            print("Error",e)
def delete_course(code:int):
    with Session(engine) as session:
        try:
            statement=select(Course).where(Course.code==code)
            result=session.exec(statement).first()
            if result:
                session.delete(result)
                session.commit()
                session.refresh(result)
                print(f"Deleted course is {result.title} {result.code}")
            else:
                print("No such courses")
        except Exception as e:
            print("Error",e)
def enroll_student(student_id:int,course_id:int,enrollment_date:Optional[datetime]=None):
    enrollment_date=enrollment_date or datetime.now(timezone.utc)
    with Session(engine) as session:
        try:
            student=session.get(Student,student_id)
            if not student:
                print(f"Student with {student_id} is not found")
                return
            course=session.get(Course,course_id)
            if not course:
                print(f"Course with {course_id} is not found")
                return 
            statement=select(StudentCourseLink).where((StudentCourseLink.student_id==student_id) & (StudentCourseLink.course_id==course_id))
            result=session.exec(statement).first()
            if result:
                print("Student already enrolled")
                return
            else:
                enrollment_details=StudentCourseLink(student_id=student_id,course_id=course_id,enrollment_date=enrollment_date)
                session.add_all([enrollment_details])
                session.commit()
                print(f"Enrollemnt Details:{enrollment_details}")
        except Exception as e:
            print("Error",e)
def get_courses_for_student(student_id:int):
    with Session(engine) as session:
        try:
            student=session.get(Student,student_id)
            if not student:
                print(f"Student with {student_id} is not enrolled")
                return 
            if not student.courses:
                print("Student is not enrolled to any of courses")
            print(f"Courses for {student.first_name}{student.last_name} is")
            for course in student.courses:
               print(f"{course.title}{course.code}")
        except Exception as e:
            print("Error",e)
def get_students_in_course(course_id:int):
    with Session(engine) as session:
        try:
            course=session.get(Course,course_id) 
            if not course:
                print(f"No course has been enrolled")
                return 
            if not course.students:
                print("No student are enrolled tho this course")
                return
            print(f"Students enrolled in {course.title}")
            for student in course.students:
                print(f"{student.first_name}{student.last_name}{student.id}")
        except Exception as e:
            print("Error",e)
def set_enrollment_grades(student_id:int,course_id:int,grade:str):
    with Session(engine) as session:
        try:
            enroll=session.get(StudentCourseLink,(student_id,course_id))
            if not enroll:
                print("Student has not enrolled to this course")
                return 
            enroll.grade=grade
            session.commit()
            session.refresh(enroll)
            print("Updated successfully")       
        except Exception as e:
            print("Error",e)
def unenroll_students(student_id:int,course_id:int):
    with Session(engine) as session:
        try:
            unenroll=session.get(StudentCourseLink,(student_id,course_id))
            if not unenroll:
                print("Student has not enrolled to this course")
            session.delete(unenroll)
            session.commit()
            session.refresh(unenroll)
            print("Deleted Successfully")
        except Exception as e:
            print("Error",e)

if __name__=="__main__":
    createAll()
    create_department(1,"CSE","Block-1")
    create_department(2,"Information Science","Block-2")
    create_department(3,"AIML","Block-3")
    create_department(4,"Mechanical","Block-4")
    create_course(1,"OS","OS123",1)
    create_course(2,"DAA","DA345",1)
    create_course(3,"COA","CO1223",2)
    create_course(4,"Biology","BO3445",2)
    create_course(5,"Maths","MA6778",4)
    create_course(6,"English","EG1223",3)
    create_course(7,"DSA","DS3445",3)
    create_student(1,"Athmi","k","atyjumol@email.com")
    create_student(2,"John","Abraham","john@email.com")
    create_student(3,"Aksar","Patel","aksar@email.com")
    create_student(4,"Rohit","Sharma","RohitSharma@gmail.com")
    create_student(5,"David","Warner","davidWarner@email.com")
    enroll_student(1,1)
    enroll_student(1,3)
    enroll_student(2,2)
    enroll_student(2,4)
    enroll_student(3,5)
    get_department_by_name("Athmi k") 
    get_student_by_email("aksar@email.com")
    get_course_by_code("MA6778")
    get_courses_for_student(1)
    get_students_in_course(3)
    list_all_Courses()
    list_all_departments()
    list_all_students()
    update_student_email("Athmi","athmik@email.com")
    delete_course(3)
    set_enrollment_grades(1,1,"A+")
    unenroll_students(1,1)
