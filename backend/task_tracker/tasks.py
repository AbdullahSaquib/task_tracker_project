from task_tracker.models import Task
from datetime import date, timedelta
from django.core.mail import send_mail
from celery import shared_task


@shared_task()
def notify_missed_tasks():
    """Send missed deadline emails to users"""
    from_email = "from@example.com"
    missed_tasks = Task.objects\
        .filter(end_date__lt=date.today())\
        .exclude(status=Task.Status.DONE)\
        .values("id", "name", "team_leader__email", "team_members__email", "end_date")
    tasks = {}  # {<task id>: <task object>, ...}
    for task in missed_tasks:
        if task["id"] not in tasks:
            tasks[task["id"]] = {
                "name": task["name"],
                "users": {task["team_leader__email"]},
                "end_date": task["end_date"],
            }
        tasks[task["id"]]["users"].add(task["team_members__email"])
    for task in tasks.values():
        subject = "Missed Task Deadline"
        message = f"""Dear User,

The deadline of the task "{task["name"]}" has been missed. The last date of the task was {task["end_date"]}.

Thank You
Task Tracker Team
    """
        to_emails = list(task["users"])
        send_mail(subject, message, from_email, to_emails, fail_silently=False)


@shared_task()
def notify_status_updates():
    """Send email notifying status updates of the tasks to team leaders"""
    from_email = "from@example.com"
    today_updated_tasks = Task.objects\
        .filter(status_updated_at__date=date.today())\
        .values("name", "team_leader__email", "status")
    leader_tasks = {}  # {<team_leader>: [list of updated tasks], ...}
    for task in today_updated_tasks:
        if task["team_leader__email"] not in leader_tasks:
            leader_tasks[task["team_leader__email"]] = [task]
        else:
            leader_tasks[task["team_leader__email"]].append(task)
    subject = "Task Status Updates"
    for team_leader, tasks in leader_tasks.items():
        rows = "\n".join(f'{task["name"]}: {task["status"]}' for task in tasks)
        message = f"""Dear User,

The status of the following tasks changed today:
{rows}

Thank You
Task Tracker Team
        """
        send_mail(subject, message, from_email, [team_leader], fail_silently=False)
