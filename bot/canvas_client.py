import json
from canvasapi import Canvas
from bot.config import Config


class CanvasClient:
    def __init__(self):
        self._canvas = Canvas(Config.CANVAS_API_URL, Config.CANVAS_API_TOKEN)
        self._user = self._canvas.get_current_user()

    def list_courses(self, active_only: bool = True) -> str:
        try:
            kwargs = {}
            if active_only:
                kwargs["enrollment_state"] = "active"
            courses = self._canvas.get_courses(**kwargs)
            result = []
            for c in courses:
                result.append({
                    "id": c.id,
                    "name": c.name,
                    "course_code": getattr(c, "course_code", ""),
                })
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"error": str(e)})

    def list_assignments(self, course_id: int, bucket: str = "upcoming") -> str:
        try:
            course = self._canvas.get_course(course_id)
            assignments = course.get_assignments(bucket=bucket, order_by="due_at")
            result = []
            for a in assignments:
                desc = getattr(a, "description", "") or ""
                result.append({
                    "id": a.id,
                    "name": a.name,
                    "due_at": getattr(a, "due_at", None),
                    "points_possible": getattr(a, "points_possible", None),
                    "submission_types": getattr(a, "submission_types", []),
                    "description": desc[:500],
                })
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"error": str(e)})

    def get_assignment(self, course_id: int, assignment_id: int) -> str:
        try:
            course = self._canvas.get_course(course_id)
            a = course.get_assignment(assignment_id)
            return json.dumps({
                "id": a.id,
                "name": a.name,
                "due_at": getattr(a, "due_at", None),
                "points_possible": getattr(a, "points_possible", None),
                "submission_types": getattr(a, "submission_types", []),
                "description": getattr(a, "description", "") or "",
                "allowed_extensions": getattr(a, "allowed_extensions", []),
                "submission_status": getattr(a, "has_submitted_submissions", None),
            })
        except Exception as e:
            return json.dumps({"error": str(e)})

    def submit_assignment(
        self,
        course_id: int,
        assignment_id: int,
        submission_type: str,
        body: str = None,
        url: str = None,
    ) -> str:
        try:
            course = self._canvas.get_course(course_id)
            assignment = course.get_assignment(assignment_id)
            submission_data = {"submission_type": submission_type}
            if body is not None:
                submission_data["body"] = body
            if url is not None:
                submission_data["url"] = url
            submission = assignment.submit(submission_data)
            return json.dumps({
                "success": True,
                "submission_id": submission.id,
                "submitted_at": getattr(submission, "submitted_at", None),
                "workflow_state": getattr(submission, "workflow_state", None),
            })
        except Exception as e:
            return json.dumps({"error": str(e)})

    def get_grades(self, course_id: int) -> str:
        try:
            enrollments = self._user.get_enrollments(type=["StudentEnrollment"])
            for enrollment in enrollments:
                if enrollment.course_id == course_id:
                    grades = getattr(enrollment, "grades", {})
                    return json.dumps({
                        "course_id": course_id,
                        "current_score": grades.get("current_score"),
                        "final_score": grades.get("final_score"),
                        "current_grade": grades.get("current_grade"),
                        "final_grade": grades.get("final_grade"),
                    })
            return json.dumps({"error": f"No enrollment found for course {course_id}"})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def get_announcements(self, course_id: int, count: int = 5) -> str:
        try:
            course = self._canvas.get_course(course_id)
            announcements = course.get_discussion_topics(only_announcements=True)
            result = []
            for i, a in enumerate(announcements):
                if i >= count:
                    break
                result.append({
                    "id": a.id,
                    "title": a.title,
                    "posted_at": getattr(a, "posted_at", None),
                    "message": (getattr(a, "message", "") or "")[:500],
                })
            return json.dumps(result)
        except Exception as e:
            return json.dumps({"error": str(e)})
