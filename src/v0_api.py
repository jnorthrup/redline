import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    filename="v0_api.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def query_v0_api(endpoint, payload):
    logging.info(f"Querying v0 API at endpoint: {endpoint} with payload: {payload}")
    # Simulate API query
    response = {"status": "success", "data": "response data"}  # Placeholder response
    logging.info(f"Received response: {response}")
    return response


if __name__ == "__main__":
    endpoint = "/api/v0/tooling"
    payload = {"query": "example query"}
    query_v0_api(endpoint, payload)
