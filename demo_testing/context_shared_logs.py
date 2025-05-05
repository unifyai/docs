import unify

unify.activate("context-shared-logs", overwrite=True)

exam_results = [{"name": "Zoe", "passed": False}, {"name": "John", "passed": True}]
results_logs = unify.create_logs(entries=exam_results, context="Results")
support_log = unify.log(name="Zoe", passed=False, context="ExtraSupport")
breakpoint()
unify.update_logs(
    logs=[results_logs[0], support_log],
    entries=[{"passed": True}, {"passed": True}],
    overwrite=True,
)
