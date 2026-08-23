import React, { useRef, useState, useEffect, useCallback } from "react";
import RecordRTC, { StereoAudioRecorder } from "recordrtc";

export default function WaveformRecorder({ onRecordingComplete }) {
  const [isRecording, setIsRecording] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const canvasRef = useRef(null);
  const recorderRef = useRef(null);
  const audioCtxRef = useRef(null);
  const analyserRef = useRef(null);
  const animationRef = useRef(null);
  const timerRef = useRef(null);
  const streamRef = useRef(null);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    const analyser = analyserRef.current;
    if (!canvas || !analyser) return;

    const ctx = canvas.getContext("2d");
    const bufferLength = analyser.fftSize;
    const dataArray = new Uint8Array(bufferLength);

    const render = () => {
      analyser.getByteTimeDomainData(dataArray);
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "#121821";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const barWidth = canvas.width / 64;
      const step = Math.floor(bufferLength / 64);

      for (let i = 0; i < 64; i++) {
        const val = dataArray[i * step] / 128.0 - 1.0;
        const barHeight = Math.abs(val) * canvas.height * 1.8 + 3;
        const x = i * barWidth;
        ctx.fillStyle = "#4FD8E8";
        ctx.fillRect(x, (canvas.height - barHeight) / 2, barWidth - 2, barHeight);
      }
      animationRef.current = requestAnimationFrame(render);
    };
    render();
  }, []);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    streamRef.current = stream;

    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const source = audioCtx.createMediaStreamSource(stream);
    const analyser = audioCtx.createAnalyser();
    analyser.fftSize = 512;
    source.connect(analyser);

    audioCtxRef.current = audioCtx;
    analyserRef.current = analyser;
    draw();

    // Use RecordRTC to generate a .wav file directly
    const recorder = new RecordRTC(stream, {
      type: "audio",
      mimeType: "audio/wav",
      recorderType: StereoAudioRecorder,
      desiredSampRate: 16000 // 16kHz is ideal for backend ML processing
    });

    recorder.startRecording();
    recorderRef.current = recorder;

    setSeconds(0);
    timerRef.current = setInterval(() => setSeconds((s) => s + 1), 1000);
    setIsRecording(true);
  };

  const stopRecording = () => {
    recorderRef.current?.stopRecording(() => {
      const blob = recorderRef.current.getBlob();
      // Pass the WAV blob back to the parent component
      onRecordingComplete(blob);

      streamRef.current?.getTracks().forEach((t) => t.stop());
      audioCtxRef.current?.close();
    });

    cancelAnimationFrame(animationRef.current);
    clearInterval(timerRef.current);
    setIsRecording(false);
  };

  useEffect(() => {
    return () => {
      cancelAnimationFrame(animationRef.current);
      clearInterval(timerRef.current);
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  const mm = String(Math.floor(seconds / 60)).padStart(2, "0");
  const ss = String(seconds % 60).padStart(2, "0");

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm text-inkdim">
          Near-real-time prototype recording
        </span>
        {isRecording && (
          <span className="flex items-center gap-2 text-danger text-sm">
            <span className="w-2 h-2 rounded-full bg-danger rec-dot" />
            REC {mm}:{ss}
          </span>
        )}
      </div>
      <canvas
        ref={canvasRef}
        width={640}
        height={120}
        className="w-full rounded-lg border border-line"
      />
      <div className="mt-4 flex gap-3">
        {!isRecording ? (
          <button
            onClick={startRecording}
            className="px-4 py-2 rounded-lg bg-signal text-void font-semibold text-sm hover:opacity-90 transition"
          >
            Start Recording
          </button>
        ) : (
          <button
            onClick={stopRecording}
            className="px-4 py-2 rounded-lg bg-danger text-void font-semibold text-sm hover:opacity-90 transition"
          >
            Stop &amp; Analyze
          </button>
        )}
      </div>
    </div>
  );
}