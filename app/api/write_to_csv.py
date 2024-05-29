import csv
from io import StringIO
from typing import Any, List


def write_to_csv(csv_file_path: str, headers: List[str], scraped_datas: List[Any]) -> None:
    output = StringIO()
    writer = csv.writer(output)

    # Write the headers to the CSV file
    writer.writerow(headers)

    # Write the data to the CSV file
    for data in scraped_datas:
        writer.writerow([getattr(data, header) for header in headers])

    # Save the CSV content to the specified file path
    with open(csv_file_path, "w", newline="") as file:
        file.write(output.getvalue())