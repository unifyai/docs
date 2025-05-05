import unify
import random

random.seed(0)
unify.activate("line_graph_grouped", overwrite=True)

model_speeds = {
    "llama-3.1-8b-chat": 12,
    "llama-3.1-70b-chat": 7,
    "llama-3.1-405b-chat": 4,
}
provider_speeds = {"fireworks-ai": 10, "together-ai": 9, "aws-bedrock": 8}
for i in range(25):
    for model, model_speed in model_speeds.items():
        for provider, provider_speed in provider_speeds.items():
            unify.log(
                model=model,
                provider=provider,
                time=i,
                speed=(model_speed + provider_speed + random.uniform(-2, 2)),
            )
