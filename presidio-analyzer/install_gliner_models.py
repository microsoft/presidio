"""Install the default gliner models."""

import argparse
import logging

from gliner import GLiNER

TEXT = """Cristiano Ronaldo dos Santos Aveiro (Portuguese pronunciation: [kɾiʃˈtjɐnu ʁɔˈnaldu]; born 5 February 1985) is a Portuguese professional footballer who plays as a forward for and captains both Saudi Pro League club Al Nassr and the Portugal national team. Widely regarded as one of the greatest players of all time, Ronaldo has won five Ballon d'Or awards,[note 3] a record three UEFA Men's Player of the Year Awards, and four European Golden Shoes, the most by a European player. He has won 33 trophies in his career, including seven league titles, five UEFA Champions Leagues, the UEFA European Championship and the UEFA Nations League. Ronaldo holds the records for most appearances (183), goals (140) and assists (42) in the Champions League, goals in the European Championship (14), international goals (128) and international appearances (205). He is one of the few players to have made over 1,200 professional career appearances, the most by an outfield player, and has scored over 850 official senior career goals for club and country, making him the top goalscorer of all time."""
LABELS = ["person", "award", "date", "competitions", "teams"]

logger = logging.getLogger()
logger.setLevel("INFO")
logger.addHandler(logging.StreamHandler())


def install_model(model_name) -> None:
    """Installs models """

    model = GLiNER.from_pretrained(model_name)
    model.predict_entities(TEXT, LABELS)

    logger.info("finished installing models")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Install gliner models into the presidio-analyzer Docker container"
    )
    parser.add_argument("--models", help="model(s) to install", type=str, nargs="+", default=["urchade/gliner_multi_pii-v1"])
    args = parser.parse_args()

    for model in args.models:
        install_model(model)
