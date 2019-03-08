#Twitter Dataset.json is composed of many lines.
#Each line is one tweet formed as a JSON object
import json
with open("Twitter Dataset.json", encoding="utf8") as f:
    maxCount = 100;
    count = 0;
    jLines = []
    for line in f:
        count += 1
        #convert json object into python dict, append to list
        jLines.append(json.loads(line))
        if count > maxCount:
            break

print("\nFile closed")

#Print out first tweet with formatting
print(json.dumps(jLines[0], indent=4, sort_keys=True))