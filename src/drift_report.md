# Drift Report

Total interactions logged: 15
Negative feedback: 6 (40.0%)

## Failure Categories

- **Pipeline Failure**: 4 cases (66.7% of failures)
- **Incomplete Response**: 1 cases (16.7% of failures)
- **Tool Error**: 1 cases (16.7% of failures)

## Detailed Failures

### [Incomplete Response] 2026-05-13T11:58:24.077486
- Input: https://youtube.com/shorts/l_nf9Lco1NM?si=33y8Mr1D1ZoLowdR
- Reason: The agent provided only metadata about the video, such as the video ID, transcript, and dataset, without addressing the user's potential question or need related to the YouTube video.

### [Tool Error] 2026-05-01T14:48:35.114269
- Input: https://youtube.com/shorts/hij456
- Reason: The agent used the wrong tool argument, as indicated by the user comment and the agent's response mentioning a wrong path placeholder.
- User comment: Wrong tool argument used

### [Pipeline Failure] 2026-05-01T14:48:35.106689
- Input: https://youtube.com/shorts/yza567
- Reason: The agent encountered a technical error with the Deepgram API key, resulting in an invalid error message being displayed to the user.
- User comment: API key error, should show better message

### [Pipeline Failure] 2026-05-01T14:48:35.102310
- Input: https://youtube.com/shorts/stu901
- Reason: The agent reported that the video was processed but a dataset file was not created, indicating a technical error during processing.
- User comment: Dataset file missing after run

### [Pipeline Failure] 2026-05-01T14:48:35.093053
- Input: https://youtube.com/shorts/jkl012
- Reason: The agent reported a technical error, specifically that the transcription returned empty segments, resulting in no transcript being provided.
- User comment: Got no transcript at all

### [Pipeline Failure] 2026-05-01T14:48:35.088777
- Input: https://youtube.com/shorts/def456
- Reason: The agent encountered a technical error during processing, as indicated by the 'No such file or directory' error message.
- User comment: It failed to find the audio file
