from feedback_db import init_db, log_feedback
init_db()

samples = [
    ('thread_001', 'msg_001', 'https://youtube.com/shorts/abc123', 'Dataset created: dataset/abc123_dataset.json with 8 segments', 1, ''),
    ('thread_002', 'msg_002', 'https://youtube.com/shorts/def456', 'Error: No such file or directory: path_to_audio', -1, 'It failed to find the audio file'),
    ('thread_003', 'msg_003', 'https://youtube.com/shorts/ghi789', 'Dataset created: dataset/ghi789_dataset.json with 12 segments', 1, ''),
    ('thread_004', 'msg_004', 'https://youtube.com/shorts/jkl012', 'Pipeline error: transcription returned empty segments', -1, 'Got no transcript at all'),
    ('thread_005', 'msg_005', 'https://youtube.com/shorts/mno345', 'Dataset created: dataset/mno345_dataset.json with 5 segments', 1, ''),
    ('thread_006', 'msg_006', 'https://youtube.com/shorts/pqr678', 'Dataset created: dataset/pqr678_dataset.json with 9 segments', 1, ''),
    ('thread_007', 'msg_007', 'https://youtube.com/shorts/stu901', 'The agent said the video was processed but no dataset file was created', -1, 'Dataset file missing after run'),
    ('thread_008', 'msg_008', 'https://youtube.com/shorts/vwx234', 'Dataset created: dataset/vwx234_dataset.json with 7 segments', 1, ''),
    ('thread_009', 'msg_009', 'https://youtube.com/shorts/yza567', 'Error: Deepgram API key invalid', -1, 'API key error, should show better message'),
    ('thread_010', 'msg_010', 'https://youtube.com/shorts/bcd890', 'Dataset created: dataset/bcd890_dataset.json with 11 segments', 1, ''),
    ('thread_011', 'msg_011', 'https://youtube.com/shorts/efg123', 'Dataset created: dataset/efg123_dataset.json with 6 segments', 1, ''),
    ('thread_012', 'msg_012', 'https://youtube.com/shorts/hij456', 'Agent called transcribe_audio with wrong path placeholder', -1, 'Wrong tool argument used'),
]

for t, m, ui, ar, fs, oc in samples:
    log_feedback(t, m, ui, ar, fs, oc)

print(f'Seeded {len(samples)} feedback entries')
