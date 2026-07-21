import { useRef, useState } from "react";
import { MdPlayArrow, MdPause, MdVideocam } from "react-icons/md";

interface Props {
  src: string | null;
  height?: number;
}

export default function VideoThumbnail({ src, height = 80 }: Props) {
  const ref = useRef<HTMLVideoElement | null>(null);
  const [playing, setPlaying] = useState(false);

  const toggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!ref.current || !src) return;
    if (playing) { ref.current.pause(); } else { ref.current.play(); }
    setPlaying(!playing);
  };

  if (!src) {
    return (
      <div
        className="d-flex align-items-center justify-content-center"
        style={{ height, background: "var(--surface-2)", borderRadius: 8, color: "var(--muted)" }}
      >
        <MdVideocam size={24} style={{ opacity: 0.4 }} />
      </div>
    );
  }

  return (
    <div style={{ position: "relative", height, overflow: "hidden", borderRadius: 8 }}>
      <video
        ref={ref}
        src={src}
        onEnded={() => setPlaying(false)}
        onPause={() => setPlaying(false)}
        preload="metadata"
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
        onClick={toggle}
      />
      {!playing && (
        <button
          onClick={toggle}
          className="card-play-btn"
          style={{
            position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)",
            width: 32, height: 32,
          }}
        >
          <MdPlayArrow size={18} />
        </button>
      )}
      {playing && (
        <button
          onClick={toggle}
          style={{
            position: "absolute", top: 4, right: 4,
            background: "rgba(0,0,0,0.5)", border: "none", borderRadius: 4,
            color: "#fff", padding: "2px 4px", cursor: "pointer",
          }}
        >
          <MdPause size={14} />
        </button>
      )}
    </div>
  );
}
