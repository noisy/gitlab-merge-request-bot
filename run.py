import gitlab
import os

gl = gitlab.Gitlab('https://gitlab.com', private_token=os.environ.get('GITLAB_ACCESS_TOKEN'))
PROJECT_NAMES_TO_TRACK = os.environ.get('GITLAB_PROJECT_NAMES').split(',')

group = gl.groups.get(os.environ.get('GITLAB_GROUP_ID'))
group_projects = group.projects.list(all=True)
for group_project in group_projects:
    if group_project.name not in PROJECT_NAMES_TO_TRACK:
        continue
    project = gl.projects.get(group_project.id, lazy=True)
    merge_requests = project.mergerequests.list(state='opened', all=True)
    # gl.mergerequests.list(project=project.id, state='opened')[0].title
    # [mr.project_id for mr in gl.projects.get(project.id).mergerequests.list()], project.id

    for mr in merge_requests:
        if mr.title.startswith('Draft') or mr.title.startswith('WIP'):
            continue
        print("─" * 80)
        print(f'Title: {mr.title}')
        print(f'URL: {mr.web_url}')

        # print('Approval Rules:')
        # for rule in mr.approval_rules.list():
        #     print(f'  - {rule.name}, approvals_required={rule.approvals_required}')

        approval = mr.approvals.get()

        needed = mr.approval_rules.list()[0].approvals_required
        received = len(approval.approved_by)

        if approval.approved:
            print(f'Approved: ✔ ({received}/{needed})️')
            for approver in approval.approved_by:
                print(f'  - ✔️  by {approver["user"]["name"]}')
            print(f'Pipelines:')
            for index, pipeline in enumerate(mr.pipelines.list()):
                if index != 0:
                    print("    " + ('┈' * 75))
                print(f'    Source: {pipeline.source}')
                status = '✔️  ' + pipeline.status if pipeline.status == 'success' else pipeline.status
                print(f'    Status: {status}')

        else:
            print(f'Approved: ❌️ ({received}/{needed})')
            for approver in approval.approved_by:
                print(f'  - ✔️  by {approver["user"]["name"]}')
            for picked_reviewer in mr.reviewers:
                if picked_reviewer["id"] not in [a["user"]["id"] for a in approval.approved_by]:
                    print(f'  - ❔ by {picked_reviewer["name"]} ')

        # requested = len(mr.reviewers)
        # approved = 0
        # print(f'Approves: {requested}/{approved}')
        # # for reviewer in mr.reviewers:
        # #     print(reviewer)

print("─" * 80)
