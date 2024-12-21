import logging
import sys

def review_latch_visitor(code: str, flavor: str):
    """
    Provides a review checkpoint to accept or reject proposed changes.
    """
    logging.debug("Executing ReviewLatchVisitor")
    user_input = input("Do you accept the proposed changes? (yes/no): ").strip().lower()
    if user_input != 'yes':
        logging.info("Refactoring changes have been rejected by the user.")
        sys.exit("Refactoring aborted by the user.")
    logging.debug("Refactoring changes accepted by the user.")
