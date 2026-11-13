"""Structural tests with explicit targets for short-circuit and priority paths."""
import pytest

import registration
from registration import Course, Student, registration_decision


def test_capacity_validation_short_circuits_on_negative_enrollment():
    # WB-CAP-A: first comparison is false; chained comparison remainder is skipped.
    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(Student("S"), Course("C", 1, 1, enrolled=-1))


def test_capacity_validation_short_circuits_on_enrollment_over_capacity():
    # WB-CAP-B: first comparison true, second false; the OR's right side is skipped.
    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(Student("S"), Course("C", 1, 1, enrolled=2))


def test_capacity_validation_evaluates_capacity_minimum():
    # WB-CAP-C: chained comparisons pass for (0, 0); capacity < 1 makes it invalid.
    with pytest.raises(ValueError, match="Invalid capacity or enrollment"):
        registration_decision(Student("S"), Course("C", 1, 0, enrolled=0))


def test_dues_validation_has_priority_over_capacity_validation():
    # WB-EXC-ORDER: dues validation raises before malformed course capacity is checked.
    with pytest.raises(ValueError, match="Invalid dues"):
        registration_decision(Student("S", outstanding_dues=-1), Course("C", 1, 0))


def test_valid_enrollment_zero_is_not_invalid_capacity():
    # WB-CAP-VALID: false edge from the capacity validation decision.
    s = Student("S", completed_courses={"P"})
    c = Course("C", 1, 1, enrolled=0, prerequisites={"P"})
    assert registration_decision(s, c) == "REGISTERED"


def test_register_course_waitlist_branch_adds_missing_student(monkeypatch):
    # WB-WAITLIST-ADD: isolate register_course's waitlist update from the unreachable
    # decision branch; the black-box test separately proves the integration defect.
    monkeypatch.setattr(registration, "registration_decision", lambda _s, _c: "WAITLISTED")
    s, c = Student("S"), Course("C", 1, 1, enrolled=1)
    assert registration.register_course(s, c) == "WAITLISTED"
    assert c.waitlist == ["S"]
    assert (s.current_credits, s.registered_courses, c.enrolled) == (0, set(), 1)


def test_register_course_waitlist_branch_does_not_duplicate_student(monkeypatch):
    # WB-WAITLIST-DUP: false edge of the membership condition at registration.py:70.
    monkeypatch.setattr(registration, "registration_decision", lambda _s, _c: "WAITLISTED")
    s, c = Student("S"), Course("C", 1, 1, enrolled=1, waitlist=["S"])
    assert registration.register_course(s, c) == "WAITLISTED"
    assert c.waitlist == ["S"]
