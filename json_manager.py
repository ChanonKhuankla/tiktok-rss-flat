#!/usr/bin/env python3
"""
JSON Data Manager for TikTok RSS
- Convert RSS to JSON
- Create consolidated JSON file with all users
- Export data in various formats
"""

import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
import csv


def rss_to_json(rss_file_path):
    """Convert RSS file to JSON format"""
    try:
        tree = ET.parse(rss_file_path)
        root = tree.getroot()

        # Find channel
        channel = root.find('channel')
        if channel is None:
            return None

        # Extract channel info
        title = channel.find('title').text if channel.find(
            'title') is not None else ""
        description = channel.find('description').text if channel.find(
            'description') is not None else ""

        # Extract user from title (format: "username TikTok")
        user = title.replace(' TikTok', '') if title.endswith(
            ' TikTok') else title

        json_data = {
            "user": user,
            "title": title,
            "description": description,
            "updated": None,
            "videos": []
        }

        # Extract items
        for item in channel.findall('item'):
            title_elem = item.find('title')
            link_elem = item.find('link')
            description_elem = item.find('description')
            pub_date_elem = item.find('pubDate')
            guid_elem = item.find('guid')

            video_data = {
                "id": guid_elem.text.split('/')[-1] if guid_elem is not None else "",
                "title": title_elem.text if title_elem is not None else "",
                "link": link_elem.text if link_elem is not None else "",
                "description": description_elem.text if description_elem is not None else "",
                "pub_date": pub_date_elem.text if pub_date_elem is not None else "",
                "guid": guid_elem.text if guid_elem is not None else ""
            }

            json_data["videos"].append(video_data)

        # Set updated time to most recent video or now
        if json_data["videos"]:
            json_data["updated"] = datetime.now(timezone.utc).isoformat()

        return json_data

    except Exception as e:
        print(f"Error converting {rss_file_path}: {e}")
        return None


def convert_all_rss_to_json():
    """Convert all RSS files in rss/ directory to JSON files in json/ directory"""
    rss_dir = Path('rss')
    json_dir = Path('json')

    if not rss_dir.exists():
        print("❌ RSS directory not found")
        return

    json_dir.mkdir(exist_ok=True)

    converted_count = 0
    for rss_file in rss_dir.glob('*.xml'):
        json_data = rss_to_json(rss_file)
        if json_data:
            json_file = json_dir / f"{rss_file.stem}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Converted {rss_file.name} → {json_file.name}")
            converted_count += 1

    print(f"🎉 Converted {converted_count} RSS files to JSON")


def create_consolidated_json():
    """Create a single JSON file with all users' data"""
    json_dir = Path('json')

    if not json_dir.exists():
        print("❌ JSON directory not found")
        return

    consolidated_data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_users": 0,
        "total_videos": 0,
        "users": []
    }

    for json_file in json_dir.glob('*.json'):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                user_data = json.load(f)

            consolidated_data["users"].append(user_data)
            consolidated_data["total_users"] += 1
            consolidated_data["total_videos"] += len(
                user_data.get("videos", []))

        except Exception as e:
            print(f"❌ Error reading {json_file}: {e}")

    # Save consolidated file
    consolidated_file = Path('tiktok_data_consolidated.json')
    with open(consolidated_file, 'w', encoding='utf-8') as f:
        json.dump(consolidated_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Created consolidated JSON: {consolidated_file}")
    print(
        f"   📊 {consolidated_data['total_users']} users, {consolidated_data['total_videos']} videos")


def export_to_csv():
    """Export all video data to CSV format"""
    json_dir = Path('json')

    if not json_dir.exists():
        print("❌ JSON directory not found")
        return

    csv_file = Path('tiktok_videos.csv')

    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['user', 'video_id', 'title', 'description', 'link',
                      'created_time', 'thumbnail_url', 'views', 'likes', 'comments', 'shares']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        video_count = 0
        for json_file in json_dir.glob('*.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    user_data = json.load(f)

                user = user_data.get('user', '')
                for video in user_data.get('videos', []):
                    stats = video.get('stats', {})
                    writer.writerow({
                        'user': user,
                        'video_id': video.get('id', ''),
                        'title': video.get('title', '').replace('\n', ' '),
                        'description': video.get('description', '').replace('\n', ' '),
                        'link': video.get('link', ''),
                        'created_time': video.get('created_time', ''),
                        'thumbnail_url': video.get('thumbnail_url', ''),
                        'views': stats.get('views', 0),
                        'likes': stats.get('likes', 0),
                        'comments': stats.get('comments', 0),
                        'shares': stats.get('shares', 0)
                    })
                    video_count += 1

            except Exception as e:
                print(f"❌ Error processing {json_file}: {e}")

    print(f"✅ Exported {video_count} videos to {csv_file}")


def generate_summary_report():
    """Generate a summary report of all data"""
    json_dir = Path('json')

    if not json_dir.exists():
        print("❌ JSON directory not found")
        return

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "users": {},
        "totals": {
            "users": 0,
            "videos": 0,
            "total_views": 0,
            "total_likes": 0,
            "total_comments": 0,
            "total_shares": 0
        }
    }

    for json_file in json_dir.glob('*.json'):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                user_data = json.load(f)

            user = user_data.get('user', json_file.stem)
            videos = user_data.get('videos', [])

            user_stats = {
                "video_count": len(videos),
                "total_views": 0,
                "total_likes": 0,
                "total_comments": 0,
                "total_shares": 0,
                "latest_video": None
            }

            for video in videos:
                stats = video.get('stats', {})
                user_stats["total_views"] += stats.get('views', 0)
                user_stats["total_likes"] += stats.get('likes', 0)
                user_stats["total_comments"] += stats.get('comments', 0)
                user_stats["total_shares"] += stats.get('shares', 0)

                if not user_stats["latest_video"] or video.get('created_time', '') > user_stats["latest_video"]:
                    user_stats["latest_video"] = video.get('created_time', '')

            report["users"][user] = user_stats
            report["totals"]["users"] += 1
            report["totals"]["videos"] += user_stats["video_count"]
            report["totals"]["total_views"] += user_stats["total_views"]
            report["totals"]["total_likes"] += user_stats["total_likes"]
            report["totals"]["total_comments"] += user_stats["total_comments"]
            report["totals"]["total_shares"] += user_stats["total_shares"]

        except Exception as e:
            print(f"❌ Error processing {json_file}: {e}")

    # Save report
    report_file = Path('tiktok_summary_report.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Print summary
    print(f"✅ Generated summary report: {report_file}")
    print(f"📊 Summary:")
    print(f"   👥 Users: {report['totals']['users']}")
    print(f"   🎥 Videos: {report['totals']['videos']}")
    print(f"   👁️  Total Views: {report['totals']['total_views']:,}")
    print(f"   ❤️  Total Likes: {report['totals']['total_likes']:,}")
    print(f"   💬 Total Comments: {report['totals']['total_comments']:,}")
    print(f"   🔄 Total Shares: {report['totals']['total_shares']:,}")


def main():
    """Main function with command line interface"""
    import sys

    if len(sys.argv) < 2:
        print("TikTok JSON Data Manager")
        print("Commands:")
        print("  convert     - Convert RSS files to JSON")
        print("  consolidate - Create consolidated JSON file")
        print("  csv         - Export to CSV format")
        print("  report      - Generate summary report")
        print("  all         - Run all operations")
        return

    command = sys.argv[1]

    if command == "convert":
        convert_all_rss_to_json()
    elif command == "consolidate":
        create_consolidated_json()
    elif command == "csv":
        export_to_csv()
    elif command == "report":
        generate_summary_report()
    elif command == "all":
        print("🚀 Running all JSON operations...")
        convert_all_rss_to_json()
        create_consolidated_json()
        export_to_csv()
        generate_summary_report()
        print("🎉 All operations completed!")
    else:
        print("Unknown command. Use: convert, consolidate, csv, report, or all")


if __name__ == "__main__":
    main()
