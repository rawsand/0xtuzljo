import gzip
import os
import re
import requests
import shutil

# ==========================================================
# Configuration
# ==========================================================

xmlGzUrl = "https://tsepg.cf/jio.xml.gz"  # Replace with your actual source URL
localGzFile = "downloaded_epg.xml.gz"
outputXmlFile = "filtered.xml"
outputGzFile = "filtered.xml.gz"

# Define multiple target channels and their new mapping IDs
channelMapping = {
    "jio-185": "31",
    "jio-1668" => "300322",
    "jio-289" => "47",
  	"jio-156" => "17",
  	"jio-3096" => "25",
  	"jio-1113" => "3",
  	"jio-165" => "30",	
  	"jio-1477" => "52",
  	"jio-3097" => "26",
  	"jio-476111" => "2834",
  	"jio-1136" => "9",
  	"jio-1839" => "33",
  	"jio-476111" => "1125",
  	"jio-476111" => "1154",
  	"jio-476111" => "1119",
  	"jio-484" => "484",
  	"jio-487" => "38",
  	"jio-1691" => "1691",
  	"jio-488" => "36",
  	"jio-1358" => "12",
  	"jio-153" => "16",	
  	"jio-476111" => "1450",	
  	"jio-476111" => "1763",
  	"jio-2761" => "23",	
  	"jio-415" => "34",
  	"jio-1104" => "1",
  	"jio-1110" => "2",
  	"jio-762" => "51",
  	"jio-1763" => "19",
	"jio-1450" => "15"
}

# ==========================================================
# Step 2a & 2b: Download the remote .xml.gz file
# ==========================================================

print("Downloading source XML.GZ from URL...")

response = requests.get(xmlGzUrl, stream=True)
response.raise_for_status()

with open(localGzFile, "wb") as fp:
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            fp.write(chunk)

# ==========================================================
# Step 2c, 2d, 3 & Filter: Parse, Rename, and Filter Title
# ==========================================================

print("Parsing, skipping 'Movie' titles, and filtering records...")

with gzip.open(localGzFile, "rt", encoding="utf-8", errors="ignore") as sourceHandle, \
     open(outputXmlFile, "w", encoding="utf-8") as outFile:

    # Write XML headers
    outFile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    outFile.write("<tv>\n")

    inChannelBlock = False
    channelBlockData = ""

    inTargetProgramme = False
    programmeBuffer = ""
    shouldSkipProgramme = False

    # Read the uncompressed stream line by line
    for line in sourceHandle:

        # --------------------------------------------------
        # 1. HANDLE CHANNELS (Keep completely intact)
        # --------------------------------------------------
        match = re.search(r'<channel\s+id="([^"]+)"', line)
        if match:
            sourceId = match.group(1)

            if sourceId in channelMapping:
                inChannelBlock = True
                line = re.sub(
                    rf'id="{re.escape(sourceId)}"',
                    f'id="{channelMapping[sourceId]}"',
                    line
                )

        if inChannelBlock:
            channelBlockData += line

            if "</channel>" in line:
                outFile.write(channelBlockData)
                inChannelBlock = False
                channelBlockData = ""

            continue

        # --------------------------------------------------
        # 2. HANDLE PROGRAMMES
        # --------------------------------------------------
        match = re.search(r'<programme\s+[^>]*channel="([^"]+)"', line)

        if match:
            sourceId = match.group(1)

            if sourceId in channelMapping:
                inTargetProgramme = True
                shouldSkipProgramme = False

                cleanedOpeningLine = re.sub(
                    rf'channel="{re.escape(sourceId)}"',
                    f'channel="{channelMapping[sourceId]}"',
                    line
                )

                programmeBuffer = "  " + cleanedOpeningLine.strip() + "\n"

        if inTargetProgramme:

            # If the line contains a title tag, analyze it
            if "<title" in line:

                if re.search(r'<title[^>]*>\s*Movie\s*</title>', line, re.IGNORECASE):
                    shouldSkipProgramme = True
                else:
                    programmeBuffer += "    " + line.strip() + "\n"

            # Once we hit the closing tag
            if "</programme>" in line:

                if not shouldSkipProgramme:
                    programmeBuffer += "  </programme>\n"
                    outFile.write(programmeBuffer)

                inTargetProgramme = False
                programmeBuffer = ""
                shouldSkipProgramme = False

    outFile.write("</tv>\n")

# ==========================================================
# Clean up temporary downloaded archive
# ==========================================================

if os.path.exists(localGzFile):
    os.remove(localGzFile)

# ==========================================================
# Step 3: Compress filtered.xml into filtered.xml.gz
# ==========================================================

print(f"Compressing into {outputGzFile}...")

with open(outputXmlFile, "rb") as xmlHandle:
    with gzip.open(outputGzFile, "wb", compresslevel=6) as gzFile:
        shutil.copyfileobj(xmlHandle, gzFile)

print("Finished! Filtered EPG created successfully.")
