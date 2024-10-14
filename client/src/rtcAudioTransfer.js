"use client";
import React, { useState, useRef } from "react";
import RecordRTC from "recordrtc";
import { v4 as uuidv4 } from "uuid";

const Mic = () => {
  const [isRecording, setIsRecording] = useState(false);
  const recorderRef = useRef<RecordRTC | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const startRecording = () => {
    const sessionId = uuidv4();
    const messageId = uuidv4();
    const userId = uuidv4();

    navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
      const ws = new WebSocket(`wss://425e-185-186-235-99.ngrok-free.app/media-stream`); // fixme: url to server from config file
      ws.onopen = () => {
        ws.send(
          JSON.stringify({
            type: "start_audio",
            session_id: sessionId,
            message_id: messageId,
            user_id: userId,
          })
        );

        const recorder = new RecordRTC(stream, {
          type: "audio",
          recorderType: RecordRTC.StereoAudioRecorder,
          mimeType: "audio/wav",
          timeSlice: 100,
          sampleRate: 48000,
          numberOfAudioChannels: 2,
          ondataavailable: (blob) => {
            console.log("ondataavailable", blob);
            const reader = new FileReader();
            reader.onloadend = () => {
              const base64data = reader.result;
              ws.send(
                JSON.stringify({
                  type: "stream_audio",
                  audio_data: base64data,
                })
              );
            };
            reader.readAsDataURL(blob);
          },
        });

        recorder.startRecording();
        recorderRef.current = recorder;
        wsRef.current = ws;
        setIsRecording(true);
      };
    });
  };

  const stopRecording = () => {
    if (recorderRef.current && wsRef.current) {
      recorderRef.current.stopRecording(() => {
        wsRef.current?.send(
          JSON.stringify({
            type: "stop_audio",
          })
        );
        wsRef.current?.close();
        setIsRecording(false);
      });
    }
  };

  return (
    <div>
      <button onClick={isRecording ? stopRecording : startRecording}>
        {isRecording ? "Stop Recording" : "Start Recording"}
      </button>
    </div>
  );
};

export default Mic;