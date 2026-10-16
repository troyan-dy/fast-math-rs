import os

from hypothesis import settings

# `HYPOTHESIS_PROFILE=thorough make test` for a longer search than the default run
settings.register_profile("default", max_examples=300, deadline=None)
settings.register_profile("thorough", max_examples=5000, deadline=None)
settings.load_profile(os.environ.get("HYPOTHESIS_PROFILE", "default"))
