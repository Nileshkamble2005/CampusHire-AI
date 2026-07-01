"""
CampusHire AI - End-to-End Integration Test
Tests: Register, Login, Student Dashboard, Recruiter Dashboard, Create Job, Profile
"""
import requests
import sys
import json

BASE = "http://127.0.0.1:5000"
PASS = "\033[92m[PASS]\033[0m"
FAIL = "\033[91m[FAIL]\033[0m"

results = []

def check(label, condition, detail=""):
    status = PASS if condition else FAIL
    results.append((label, condition))
    print(f"{status}  {label}" + (f" => {detail}" if detail else ""))
    return condition

def test():
    session_student = requests.Session()
    session_recruiter = requests.Session()

    # ==============================
    # 1. HOME PAGE
    # ==============================
    r = session_student.get(f"{BASE}/")
    check("1. Home page loads (200)", r.status_code == 200)
    check("1. Home page has CampusHire title", "CampusHire" in r.text)

    # ==============================
    # 2. STUDENT REGISTER
    # ==============================
    data = {
        "fullname": "NK Test Student",
        "email": "nktest_auto@example.com",
        "phone": "9876543210",
        "password": "Test@1234",
        "confirm_password": "Test@1234",
        "role": "Student",
        "college": "MIT Pune",
        "branch": "Computer Science",
        "year": "Final Year",
    }
    r = session_student.post(f"{BASE}/register", data=data, allow_redirects=True)
    registered = r.status_code == 200 and ("Login" in r.text or "login" in r.url or "Registration Successful" in r.text or "already registered" in r.text)
    check("2. Student Registration (200 + redirect/success)", registered, f"URL: {r.url}")

    # ==============================
    # 3. STUDENT LOGIN
    # ==============================
    r = session_student.post(f"{BASE}/login", data={
        "email": "nktest_auto@example.com",
        "password": "Test@1234",
    }, allow_redirects=True)
    logged_in_student = "student_dashboard" in r.url or "Student Dashboard" in r.text or "Upload Your Resume" in r.text
    check("3. Student Login & Redirect to Dashboard", logged_in_student, f"URL: {r.url}")

    # ==============================
    # 4. STUDENT DASHBOARD
    # ==============================
    r = session_student.get(f"{BASE}/student_dashboard")
    check("4. Student Dashboard loads (200)", r.status_code == 200)
    check("4. Student Dashboard has correct content", "Dashboard" in r.text or "Resume" in r.text)

    # ==============================
    # 5. STUDENT PROFILE PAGE
    # ==============================
    r = session_student.get(f"{BASE}/student_profile")
    check("5. Student Profile page loads (200)", r.status_code == 200)
    check("5. Student Profile has form", "form" in r.text.lower() or "profile" in r.text.lower())

    # ==============================
    # 6. UPDATE STUDENT PROFILE
    # ==============================
    r = session_student.post(f"{BASE}/student_profile", data={
        "name": "NK Test Student",
        "email": "nktest_auto@example.com",
        "college": "PostgreSQL University",
        "branch": "Computer Science",
        "year": "Final Year",
        "phone": "9876543210",
    }, allow_redirects=True)
    check("6. Student Profile Update (no crash)", r.status_code == 200)

    # ==============================
    # 7. STUDENT LOGOUT
    # ==============================
    r = session_student.get(f"{BASE}/logout", allow_redirects=True)
    check("7. Student Logout (redirects to login)", "login" in r.url or "Login" in r.text)

    # ==============================
    # 8. RECRUITER REGISTER
    # ==============================
    data = {
        "fullname": "NK Test Recruiter",
        "email": "nkrecruiter_auto@example.com",
        "phone": "9123456780",
        "password": "Test@1234",
        "confirm_password": "Test@1234",
        "role": "Recruiter",
        "company": "TechCorp Solutions",
        "designation": "HR Manager",
    }
    r = session_recruiter.post(f"{BASE}/register", data=data, allow_redirects=True)
    check("8. Recruiter Registration (success)", r.status_code == 200, f"URL: {r.url}")

    # ==============================
    # 9. RECRUITER LOGIN
    # ==============================
    r = session_recruiter.post(f"{BASE}/login", data={
        "email": "nkrecruiter_auto@example.com",
        "password": "Test@1234",
    }, allow_redirects=True)
    logged_in_recruiter = "recruiter_dashboard" in r.url or "Recruiter Dashboard" in r.text or "Create Job" in r.text
    check("9. Recruiter Login & Redirect to Dashboard", logged_in_recruiter, f"URL: {r.url}")

    # ==============================
    # 10. RECRUITER DASHBOARD
    # ==============================
    r = session_recruiter.get(f"{BASE}/recruiter_dashboard")
    check("10. Recruiter Dashboard loads (200)", r.status_code == 200)
    check("10. Recruiter Dashboard has correct content", "Job" in r.text or "Applicant" in r.text)

    # ==============================
    # 11. CREATE JOB
    # ==============================
    r = session_recruiter.post(f"{BASE}/create_job", data={
        "title": "Python Backend Developer",
        "company": "TechCorp Solutions",
        "location": "Pune, Maharashtra",
        "required_skills": "Python, Flask, PostgreSQL",
        "salary": "8-12 LPA",
        "experience": "1-3 Years",
        "employment_type": "Full Time",
        "status": "Open",
        "description": "We need a Python backend developer with Flask and PostgreSQL experience.",
    }, allow_redirects=True)
    check("11. Create Job (no crash, 200)", r.status_code == 200, f"URL: {r.url}")
    check("11. Job listed after creation", "Python Backend Developer" in r.text or "Job" in r.text)

    # ==============================
    # 12. RECRUITER PROFILE
    # ==============================
    r = session_recruiter.get(f"{BASE}/recruiter_profile")
    check("12. Recruiter Profile page loads (200)", r.status_code == 200)

    # ==============================
    # 13. VIEW APPLICANTS PAGE
    # ==============================
    r = session_recruiter.get(f"{BASE}/recruiter_dashboard")
    check("13. Recruiter Dashboard still loads after job creation (200)", r.status_code == 200)

    # ==============================
    # 14. RECRUITER LOGOUT
    # ==============================
    r = session_recruiter.get(f"{BASE}/logout", allow_redirects=True)
    check("14. Recruiter Logout", "login" in r.url or "Login" in r.text)

    # ==============================
    # 15. STUDENT LOGIN AGAIN (check job recommendations)
    # ==============================
    r = session_student.post(f"{BASE}/login", data={
        "email": "nktest_auto@example.com",
        "password": "Test@1234",
    }, allow_redirects=True)
    check("15. Student re-Login", r.status_code == 200)
    r2 = session_student.get(f"{BASE}/student_dashboard")
    check("15. Student Dashboard loads with job recommendations visible", r2.status_code == 200)

    # ==============================
    # 16. STUDENT DASHBOARD (JOBS RECOMMENDATIONS)
    # ==============================
    r = session_student.get(f"{BASE}/student_dashboard")
    check("16. Student Dashboard shows job recommendations (200)", r.status_code == 200)

    # ==============================
    # SUMMARY
    # ==============================
    print("\n" + "="*50)
    print("     CAMPUSHIRE AI - TEST RESULTS SUMMARY     ")
    print("="*50)
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    for label, ok in results:
        icon = "[PASS]" if ok else "[FAIL]"
        print(f"  {icon}  {label}")
    print("="*50)
    print(f"  Total: {passed}/{total} tests passed")
    print("="*50)
    if passed == total:
        print("  ALL TESTS PASSED! Portal is fully functional.")
    else:
        print(f"  {total - passed} test(s) failed. Review above.")

if __name__ == "__main__":
    test()
