"""Requirements-based black-box tests. Expected results come from REQUIREMENTS.md."""
import pytest

from registration import (
    Course, Student, check_credit_limit, prerequisites_satisfied,
    register_course, registration_decision, withdraw_course,
)


@pytest.mark.parametrize("current,new,expected,test_id", [
    (0, 1, True, "ECP-CR-VALID-MIN"), (14, 4, True, "ECP-CR-VALID-MAX"),
    (15, 3, True, "BVA-TOTAL-18"), (16, 3, False, "BVA-TOTAL-19"),
    (17, 1, True, "BVA-TOTAL-18-MIN-COURSE"),
    (18, 1, False, "BVA-TOTAL-19-AT-MAX"),
])
def test_credit_limit_valid_classes_and_boundaries(current, new, expected, test_id):
    assert check_credit_limit(current, new) is expected, test_id


@pytest.mark.parametrize("current,new,message,test_id", [
    (-1, 1, "Invalid current credits", "ECP-CR-CURRENT-LOW"),
    (19, 1, "Invalid current credits", "ECP-CR-CURRENT-HIGH"),
    (0, 0, "Invalid course credits", "ECP-CR-COURSE-LOW"),
    (0, 5, "Invalid course credits", "ECP-CR-COURSE-HIGH"),
])
def test_credit_limit_invalid_classes(current, new, message, test_id):
    with pytest.raises(ValueError, match=message):
        check_credit_limit(current, new)


@pytest.mark.parametrize("completed,required,expected,test_id", [
    (set(), set(), True, "ECP-PR-NONE"),
    ({"CS101", "MATH101"}, {"CS101", "MATH101"}, True, "ECP-PR-ALL"),
    ({"CS101"}, {"CS101", "MATH101"}, False, "ECP-PR-SOME"),
    ({"BIO101"}, {"CS101", "MATH101"}, False, "ECP-PR-NONE-COMPLETED"),
])
def test_prerequisite_classes(completed, required, expected, test_id):
    assert prerequisites_satisfied(completed, required) is expected, test_id


def student(**kw):
    return Student("S1", **kw)


def course(**kw):
    capacity = kw.pop("capacity", 2)
    return Course("CS201", 3, capacity, **kw)


@pytest.mark.parametrize("dues,registered,completed,credits,enrolled,expected,test_id", [
    (0, set(), {"CS101", "MATH101"}, 0, 0, "REGISTERED", "DT-REGISTER"),
    (0, set(), {"CS101", "MATH101"}, 0, 2, "WAITLISTED", "BVA-CAPACITY-FULL"),
    (0, set(), {"CS101", "MATH101"}, 0, 1, "REGISTERED", "BVA-CAPACITY-ONE-BELOW"),
    (1, set(), {"CS101"}, 0, 0, "DUES_BLOCK", "BVA-DUES-1"),
    (1001, set(), {"CS101"}, 0, 0, "DUES_BLOCK", "ECP-DUES-POSITIVE"),
    (0, {"CS201"}, set(), 18, 2, "ALREADY_REGISTERED", "DT-PRIORITY-DUP"),
    (0, set(), set(), 18, 2, "PREREQUISITES_MISSING", "DT-PRIORITY-PREREQ"),
    (0, set(), {"CS101", "MATH101"}, 16, 2, "CREDIT_LIMIT", "DT-PRIORITY-CREDIT"),
    (1, {"CS201"}, set(), 18, 2, "DUES_BLOCK", "DT-PRIORITY-DUES"),
    (0, {"CS201"}, {"CS101"}, 16, 0, "ALREADY_REGISTERED", "DT-PRIORITY-SEAT"),
])
def test_decision_table_and_priority(dues, registered, completed, credits, enrolled, expected, test_id):
    s = student(outstanding_dues=dues, registered_courses=set(registered),
                completed_courses=set(completed), current_credits=credits)
    c = course(prerequisites={"CS101", "MATH101"}, enrolled=enrolled)
    before = (s.current_credits, s.outstanding_dues, set(s.registered_courses), c.enrolled, list(c.waitlist))
    assert registration_decision(s, c) == expected, test_id
    assert (s.current_credits, s.outstanding_dues, s.registered_courses, c.enrolled, c.waitlist) == before


@pytest.mark.parametrize("dues,capacity,enrolled,message,test_id", [
    (-1, 2, 0, "Invalid dues", "ECP-DUES-NEGATIVE"),
    (0, 0, 0, "Invalid capacity or enrollment", "ECP-CAPACITY-ZERO"),
    (0, 2, -1, "Invalid capacity or enrollment", "ECP-ENROLLMENT-NEGATIVE"),
    (0, 2, 3, "Invalid capacity or enrollment", "ECP-ENROLLMENT-OVER"),
])
def test_invalid_dues_and_seat_data(dues, capacity, enrolled, message, test_id):
    with pytest.raises(ValueError, match=message):
        registration_decision(student(outstanding_dues=dues), Course("CS201", 3, capacity, enrolled=enrolled))


def test_successful_registration_updates_all_state():
    s, c = student(current_credits=15, completed_courses={"CS101"}), course(capacity=1)
    assert register_course(s, c) == "REGISTERED"  # STATE-REGISTER
    assert (s.current_credits, s.registered_courses, c.enrolled) == (18, {"CS201"}, 1)


def test_waitlist_adds_once_and_preserves_enrollment_state():
    s, c = student(completed_courses={"CS101"}), course(capacity=1, enrolled=1, waitlist=["S1"])
    before = (s.current_credits, set(s.registered_courses), c.enrolled)
    assert register_course(s, c) == "WAITLISTED"  # STATE-WAITLIST
    assert c.waitlist == ["S1"]
    assert (s.current_credits, s.registered_courses, c.enrolled) == before


@pytest.mark.parametrize("dues,registered,completed,credits,expected,test_id", [
    (1, set(), {"CS101"}, 0, "DUES_BLOCK", "STATE-FAIL-DUES"),
    (0, set(), set(), 0, "PREREQUISITES_MISSING", "STATE-FAIL-PREREQ"),
    (0, set(), {"CS101", "MATH101"}, 16, "CREDIT_LIMIT", "STATE-FAIL-CREDIT"),
])
def test_unsuccessful_registration_does_not_mutate(dues, registered, completed, credits, expected, test_id):
    s = student(outstanding_dues=dues, registered_courses=registered,
                completed_courses=completed, current_credits=credits)
    c = course(capacity=3, enrolled=1, prerequisites={"CS101", "MATH101"})
    before = (s.current_credits, set(s.registered_courses), c.enrolled, list(c.waitlist))
    assert register_course(s, c) == expected, test_id
    assert (s.current_credits, s.registered_courses, c.enrolled, c.waitlist) == before


def test_withdrawal_updates_student_and_course():
    s, c = student(current_credits=6, registered_courses={"CS201"}), course(enrolled=1)
    assert withdraw_course(s, c) is True  # STATE-WITHDRAW
    assert (s.current_credits, s.registered_courses, c.enrolled) == (3, set(), 0)


def test_withdrawal_of_unregistered_course_preserves_state():
    s, c = student(current_credits=6), course(enrolled=1)
    before = (s.current_credits, set(s.registered_courses), c.enrolled)
    assert withdraw_course(s, c) is False  # STATE-WITHDRAW-ABSENT
    assert (s.current_credits, s.registered_courses, c.enrolled) == before
