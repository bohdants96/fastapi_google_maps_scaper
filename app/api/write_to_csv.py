import csv
from io import StringIO
from typing import Sequence

from app.models import BusinessLeadPublic


def write_to_csv(
    csv_file_path: str,
    headers: list[str],
    scraped_datas: Sequence[BusinessLeadPublic],
) -> None:
    output = StringIO()
    writer = csv.writer(output)

    # Write the headers to the CSV file
    writer.writerow(headers)

    # Write the data to the CSV file
    for data in scraped_datas:
        row = []
        for header in headers:
            # Check if the header has a nested attribute (e.g., 'owner.person_position')
            if "." in header:
                # Split the header to get the root attribute and the nested attribute
                root_attr, nested_attr = header.split(".", 1)

                # Get the root attribute object
                root_value = getattr(data, root_attr, None)

                # If the root attribute exists and is an object, get the nested attribute
                if root_value:
                    value = getattr(root_value, nested_attr, None)
                else:
                    value = None
            else:
                # If it's not a nested attribute, get the value directly
                value = getattr(data, header, None)

            row.append(value)

        writer.writerow(row)

    # Save the CSV content to the specified file path
    with open(csv_file_path, "w", newline="") as file:
        file.write(output.getvalue())
