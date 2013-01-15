defaultSettings = {
    # Task input
    'get_tasks_from_file' : True,
    'task_source_file' : r"""C:\MyTemp\juherask\Dropbox\Notebook\Work\Tasks\2-Active.txt""",
    'tasks_organized_under_headers' : False,
    'text_in_header' : "===== In =====",
    'text_do_header' : "===== Do =====",
    'text_out_header' : "===== Done =====",
    'text_rejected_header' : "===== Rejected =====",
    
    'require_zim_task_format' : True,
    'encourage_use_of_verb_tag' : True,
    
    # Logging
    'keep_task_activity_log' : True,
    'task_activity_log_file' : r"""C:\MyTemp\juherask\Dropbox\Notebook\Work\Tasks\Logging\TaskActivityLog.txt""",
    
    'keep_user_activity_log' : True,
    'user_activity_log_file' : r"""C:\MyTemp\juherask\Dropbox\Notebook\Work\Tasks\Logging\UserActivityLog.txt""",
    'user_activity_refresh_interval' : 5000, #in ms
    'user_idle_threshold' : 120000, #in ms
    
    # Nagging
    'nag' : True, # Requires 'keep_task_activity_log' to be True
    'nag_teach_file' : r"""C:\MyTemp\juherask\Dropbox\Notebook\Work\Tasks\Logging\NagTeachLog.txt""",
    'nag_motivational_posters_folder' : r"""Nags""",
    'nag_slack' : 10000, # in ms, a violation longer than this leads to a nag
    'nag_require_all_tags' : False, # The activity is required to be relevant to all tags (True not recommended)
}