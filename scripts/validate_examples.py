from pathlib import Path

import yaml
from openapi_schema_validator import OAS30Validator

ROOT = Path(__file__).resolve().parents[1]


def expand_schema(value, document):
    """Resolve local references in our non-recursive schemas."""
    if isinstance(value, dict):
        if "$ref" in value:
            reference = value["$ref"]
            if not reference.startswith("#/"):
                raise ValueError(f"Unsupported reference: {reference}")

            target = document
            for part in reference[2:].split("/"):
                target = target[part.replace("~1", "/").replace("~0", "~")]

            return expand_schema(target, document)

        return {key: expand_schema(item, document) for key, item in value.items()}

    if isinstance(value, list):
        return [expand_schema(item, document) for item in value]

    return value


def check_examples(node, document, location):
    count = 0

    if isinstance(node, dict):
        if "schema" in node and "example" in node:
            schema = expand_schema(node["schema"], document)
            OAS30Validator(schema).validate(node["example"])
            print(f"PASS: {location}")
            count += 1

        for key, value in node.items():
            count += check_examples(value, document, f"{location}/{key}")

    elif isinstance(node, list):
        for index, value in enumerate(node):
            count += check_examples(value, document, f"{location}/{index}")

    return count


for filename in ("order-api.yaml", "fulfilment-api.yaml"):
    path = ROOT / "contracts" / filename
    document = yaml.safe_load(path.read_text(encoding="utf-8"))

    count = check_examples(document, document, filename)

    if count == 0:
        raise ValueError(f"No schema-associated examples found: {filename}")

    print(f"{filename}: {count} examples passed\n")
