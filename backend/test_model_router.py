from app.ai.model_router import ModelRouter, ModelRoutingError
from app.ai.model_routes import ModelRoute


def print_selection(router: ModelRouter, route: ModelRoute) -> None:
    try:
        selection = router.select(route)

        print(f"Route: {selection.route.value}")
        print(f"Provider: {selection.provider}")
        print(f"Model: {selection.model}")
        print()

    except ModelRoutingError as error:
        print(f"Route error: {error}")
        print()


router = ModelRouter()

for route in ModelRoute:
    print_selection(router, route)