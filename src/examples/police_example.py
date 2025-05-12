# Example police-civilian interaction data
conversation_transcript = {
    "metadata": {
        "title": "Traffic Stop Interaction",
        "date": "2023-08-22",
        "duration": "00:12:45"
    },
    "segments": [
        {
            "id": 0,
            "speaker": "S1",
            "start": 0.0,
            "end": 8.2,
            "text": "Good afternoon. I'm Officer Johnson with the Metro Police Department. Do you know why I pulled you over today?"
        },
        {
            "id": 1,
            "speaker": "S2",
            "start": 8.5,
            "end": 15.7,
            "text": "No officer, I don't think I was speeding or anything. Was there a problem?"
        },
        {
            "id": 2,
            "speaker": "S1",
            "start": 16.0,
            "end": 25.3,
            "text": "You were going 45 in a 30 zone. May I see your license and registration please?"
        },
        {
            "id": 3,
            "speaker": "S2",
            "start": 25.8,
            "end": 38.1,
            "text": "I'm sorry, I didn't realize the speed limit changed. Here's my license. My name is Robert Chen. The registration is in the glove compartment."
        },
        {
            "id": 4,
            "speaker": "S3",
            "start": 38.5,
            "end": 48.2,
            "text": "Excuse me, Officer. I witnessed what happened. This road just changed to 30 mph last week. The sign is partially hidden by that tree branch."
        },
        {
            "id": 5,
            "speaker": "S1",
            "start": 48.8,
            "end": 59.6,
            "text": "Thank you for that information. I'll make a note of it. Mr. Chen, please wait here while I run your information."
        },
        {
            "id": 6,
            "speaker": "S4",
            "start": 65.1,
            "end": 80.3,
            "text": "Johnson, this is Sergeant Martinez. What's your status on that traffic stop? We've got reports of a similar vehicle involved in an incident downtown."
        },
        {
            "id": 7,
            "speaker": "S1",
            "start": 80.8,
            "end": 92.2,
            "text": "I'm just running the driver's information now, Sergeant. The driver is cooperative. There's also a witness mentioning the speed limit sign is obscured."
        },
        {
            "id": 8,
            "speaker": "S4",
            "start": 92.7,
            "end": 100.3,
            "text": "Understood. I'll send a unit to check that sign. Let me know if you need backup."
        },
        {
            "id": 9,
            "speaker": "S2",
            "start": 105.8,
            "end": 112.5,
            "text": "Is everything okay, officer? I'm already late for my appointment."
        },
        {
            "id": 10,
            "speaker": "S1",
            "start": 113.0,
            "end": 125.4,
            "text": "Everything is fine, Mr. Chen. Given the circumstances with the signage, I'm going to issue just a warning today. Please be mindful of posted speed limits in the future."
        }
    ],
    "language": "en"
}

# Example usage:
if __name__ == "__main__":
    import json
    print(json.dumps(conversation_transcript, indent=2))