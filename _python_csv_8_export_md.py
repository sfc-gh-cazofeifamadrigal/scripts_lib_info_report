import csv


def csv_to_markdown(csv_file_path, md_file_path):
    with open(csv_file_path, "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        headers = next(csv_reader)

        with open(md_file_path, "w") as md_file:
            md_file.write("| " + " | ".join(headers) + " |\n")
            md_file.write("|" + "---|" * len(headers) + "\n")

            for row in csv_reader:
                md_file.write("| " + " | ".join(row) + " |\n")


# nuget
csv_to_markdown("updated_filtered_output_nuget.csv", "updated_filtered_output_nuget.md")
# npm
csv_to_markdown("updated_filtered_output_npm.csv", "updated_filtered_output_npm..md")
