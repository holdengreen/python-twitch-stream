#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This is a small example which creates a twitch stream to connect with
and changes the color of the video according to the colors provided in
the chat.
"""
from __future__ import print_function
from twitchstream.outputvideo import TwitchBufferedOutputStream
from twitchstream.chat import TwitchChatStream
import argparse
import time
import numpy as np

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    required = parser.add_argument_group('required arguments')
    required.add_argument('-u', '--username',
                          help='twitch username',
                          required=True)
    required.add_argument('-o', '--oauth',
                          help='twitch oauth '
                               '(visit https://twitchapps.com/tmi/ '
                               'to create one for your account)',
                          required=True)
    required.add_argument('-s', '--streamkey',
                          help='twitch streamkey',
                          required=True)
    args = parser.parse_args()

    with TwitchBufferedOutputStream(
            twitch_stream_key=args.streamkey,
            width=640,
            height=480,
            fps=30.,
            verbose=True) as videostream, \
        TwitchChatStream(
            username=args.username,
            oauth=args.oauth,
            verbose=False) as chatstream:

        chatstream.send_chat_message("Taking requests!")

        frame = np.zeros((480, 640, 3))
        frequency = 100
        last_phase = 0

        while True:
            received = chatstream.twitch_receive_messages()
            if received:
                if received[0]['message'] == "red":
                    frame[:, :, :] = np.array(
                        [1, 0, 0])[None, None, :]
                elif received[0]['message'] == "green":
                    frame[:, :, :] = np.array(
                        [0, 1, 0])[None, None, :]
                elif received[0]['message'] == "blue":
                    frame[:, :, :] = np.array(
                        [0, 0, 1])[None, None, :]
                elif received[0]['message'].isdigit():
                    frequency = int(received[0]['message'])

            if videostream.get_video_frame_buffer_state() < 30:
                videostream.send_video_frame(frame)

            if videostream.get_audio_buffer_state() < 30:
                x = np.linspace(last_phase,
                                last_phase+frequency*2*np.pi,
                                44100 + 1)
                last_phase = x.pop()
                audio = np.sin(x)
                videostream.send_audio(audio, audio)

            time.sleep(1.0 / videostream.fps)
