from freeds.config.file import get_current_config_set

print(list(get_current_config_set().config_set().keys()))
