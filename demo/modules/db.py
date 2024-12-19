import subprocess
from .logging import configure_logger
from .api import call_endpoint


def empty_db(config, remote=True):
    logger = configure_logger()
    if config.get("clean_database") == "yes":

        logger.info("Deleting all data, please wait...")
        if remote:
            response = call_endpoint("GET", "empty_database", None)
        else:
            subprocess.run(["./scripts/empty_db.sh"])
        logger.info("Database cleaned.")
        logger.info(response.text)

    else:
        logger.info(
            "The clean_database value is not set to 'yes', database not cleaned."
        )
