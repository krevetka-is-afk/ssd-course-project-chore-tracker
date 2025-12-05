from datetime import date

from domain.tracker import Tracker


def test_assignment_only_for_group_members():
    tracker = Tracker()
    user1 = tracker.create_user("alice")
    user2 = tracker.create_user("bob")
    group = tracker.create_group("Flatmates")

    # user2 not in group yet -> assignment fails
    chore = tracker.create_chore("Trash", "Take out trash", created_by_user_id=user1.id)
    assert (
        tracker.assign_chore(
            chore_id=chore.id,
            group_id=group.id,
            to_user_id=user2.id,
            by_user_id=user1.id,
            due_date=date.today(),
        )
        is None
    )

    tracker.add_user_to_group(user2.id, group.id)
    assignment = tracker.assign_chore(
        chore_id=chore.id,
        group_id=group.id,
        to_user_id=user2.id,
        by_user_id=user1.id,
        due_date=date.today(),
    )
    assert assignment is not None
    assert assignment.assigned_to_user_id == user2.id
    assert tracker.mark_assignment_done(assignment.id) is True
    assert tracker.get_assignment(assignment.id).status.value == "done"
