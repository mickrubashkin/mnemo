# import json
# import subprocess
# import pickle
# from datetime import datetime


# def export_apple_notes():
#     # get all notes data ({id, title, body})
#     print("Running apple notes export...")
#     result = subprocess.run(
#         ['osascript', "./apple_scripts/get_notes.scpt"],
#         capture_output=True,
#         text=True,
#         timeout=300
#     )

#     if result.returncode != 0:
#         raise Exception(f"AppleScript error: {result.stderr}")

#     notes = json.loads(result.stdout)

#     for note in notes:
#         created = datetime.strptime(note['created'], '%Y-%m-%d %H:%M:%S')
#         modified = datetime.strptime(note['modified'], '%Y-%m-%d %H:%M:%S')

#     return notes

# def process_and_save(notes, output_path='./data/apple_notes.pkl'):
#     processed = []

#     for note in notes:
#         processed.append({
#             'id': note['id'],
#             'source': 'apple',
#             'title': note['title'],
#             'body': note['body'],
#             'created': note['created'],
#             'modified': note['modified']
#         })

#     with open(output_path, 'wb') as f:
#         pickle.dump(processed, f, protocol=pickle.HIGHEST_PROTOCOL)

#     return processed
