from core.core import Core, Entity
from memory.memory import *

description = [
    "You'r a Blacksmith nammed Martin, you love soccers and you are married with Janisse.",
    "You'r a cook nammed Janisse, you love soccers and you are married with Martin.",
]


if __name__ == "__main__":
    core = Core(
        entities={
            "Martin" : Entity("Martin", Memory("Martin", description[0])),
            "Janisse" : Entity("Janisse", Memory("Janisse", description[1])),
        },
        debug=True
    )

    list_of_entities_name = ["Martin", "Janisse", "Patrick", "Maurice"]
    for entities in core.entities.values():
        group = ", ".join(filter(lambda name: name != entities.name, list_of_entities_name))
        print(entities.memory.get_action(position, env, time, group))
