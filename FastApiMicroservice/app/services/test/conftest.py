from hypothesis import settings, HealthCheck

# deadline=None: estos tests corren lógica pura (sin I/O), pero en CI compartido
# los tiempos pueden ser ruidosos -- preferimos que Hypothesis nunca falle por
# timing y sí por una propiedad real violada.
settings.register_profile(
    "default",
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
settings.load_profile("default")
