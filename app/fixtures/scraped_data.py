from dataclasses import dataclass
import re
import csv


@dataclass
class Address:
    country: str
    state: str
    city: str
    address: str
    postal_code: str


def parse_address(address_str: str) -> Address | None:
    # Improved regex patterns to match various address formats
    patterns = [
        re.compile(
            r"(?P<address>.+?),\s*(?P<city>[^,]+?),\s*(?P<state>\w{2})\s*(?P<postal_code>\d{5})(?:-\d{4})?,\s*(?P<country>.+)"
        ),
        re.compile(
            r"(?P<city>[^,]+?),\s*(?P<state>\w{2})\s*(?P<postal_code>\d{5})(?:-\d{4})?,\s*(?P<country>.+)"
        ),
        re.compile(
            r"(?P<address>.+?),\s*(?P<city>[^,]+?),\s*(?P<state>\w{2})\s*(?P<postal_code>\d{5})"
        ),
        re.compile(
            r"(?P<city>[^,]+?),\s*(?P<state>\w{2})\s*(?P<postal_code>\d{5})"
        ),
    ]

    for pattern in patterns:
        match = pattern.match(address_str.strip())
        if match:
            address_components = match.groupdict()

            # Extract and validate components
            city = address_components.get("city", "")
            state = address_components.get("state", "")
            postal_code = address_components.get("postal_code", "")

            if "address" in address_components:
                # Construct a pattern to identify duplicates
                duplicate_pattern = f"{city}, {state} {postal_code}"
                if duplicate_pattern in address_components["address"]:
                    address_components["address"] = (
                        address_components["address"]
                        .replace(duplicate_pattern, "")
                        .strip(", ")
                    )

            country = address_components.get("country", "United States")
            if re.match(
                r"\d{5}", country
            ):  # Check if the country field is actually a postal code
                country = "United States"

            return Address(
                country=country,
                state=state,
                city=city,
                address=address_components.get("address", ""),
                postal_code=postal_code,
            )

    print(f"Warning: Address '{address_str}' is not in the expected format.")
    return None


@dataclass
class ScrapedData:
    title: str
    address: str
    phone: str
    website: str
    location: str
    country: str
    business_type: str
    zip_code: str


def load_scraped_data() -> (
    tuple[list[ScrapedData], list[str], list[str], list[str]]
):
    countries = []
    states = []
    cities = []
    scraped_data: list[ScrapedData] = []
    business_types = []

    skipped_addresses = 0

    with open("/code/app/fixtures/scraped_data.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if not "address" in row or not row["address"]:
                continue

            if "business" in row and row["business"] not in business_types:
                business_types.append(row["business"])

            address = parse_address(row["address"])
            if address:
                if address.country not in countries:
                    countries.append(address.country)
                if address.state not in states:
                    states.append(address.state)
                if address.city not in cities:
                    cities.append(address.city)

                scraped_data.append(
                    ScrapedData(
                        title=row["name"],
                        address=row["address"],
                        phone=row["phone"],
                        website=row["website"],
                        location=address.state,
                        country=address.country,
                        business_type=row["business"],
                        zip_code=address.postal_code,
                    )
                )
            else:
                skipped_addresses += 1

    print(f"Skipped {skipped_addresses} addresses.")
    return scraped_data, countries, states, business_types
