#!/bin/bash
# Batch process multiple YouTube videos
#
# Usage:
#   1. Create a file video_urls.txt with one URL per line
#   2. Run: bash examples/batch_process.sh

# Check if video_urls.txt exists
if [ ! -f "video_urls.txt" ]; then
    echo "Error: video_urls.txt not found"
    echo "Create a file with one YouTube URL per line"
    exit 1
fi

# Create output directory
mkdir -p batch_output

# Process each video
count=0
while IFS= read -r url; do
    # Skip empty lines and comments
    if [ -z "$url" ] || [[ "$url" == \#* ]]; then
        continue
    fi

    count=$((count + 1))
    echo ""
    echo "========================================="
    echo "Processing video $count: $url"
    echo "========================================="

    # Extract video ID from URL
    video_id=$(echo "$url" | sed -n 's/.*v=\([^&]*\).*/\1/p')
    if [ -z "$video_id" ]; then
        video_id="video_$count"
    fi

    # Process video
    python scripts/process_video.py "$url" "lecture_${video_id}" \
        --output-dir batch_output \
        --format html

    # Check if successful
    if [ $? -eq 0 ]; then
        echo "✅ Successfully processed: $video_id"
    else
        echo "❌ Failed to process: $video_id"
    fi
done < video_urls.txt

echo ""
echo "========================================="
echo "Batch processing complete!"
echo "Processed $count videos"
echo "Output directory: batch_output/"
echo "========================================="
