from mapmyrun import parse_mapmyrun_file

url = "https://objectstoragehabit.blob.core.windows.net/filestorage/07a0c576-7972-4f7b-a429-3ff140bd9fa5.xlsx"

parsed_data, error = parse_mapmyrun_file(url)

print("Error:", error)
print("Rows:", 0 if parsed_data is None else len(parsed_data))
print("First row:", None if not parsed_data else parsed_data[0])