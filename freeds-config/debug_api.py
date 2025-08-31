from freeds.config.file import get_current_config_set, get_config

print(get_config('s3').data)
print(get_current_config_set().config_set.keys())
