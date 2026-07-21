import { useRef, useState } from "react";
import { MdPlayArrow, MdPause } from "react-icons/md";

interface Props {
  src: string | null;
  size?: number;
}

export default function AudioPlayerMini({ src, size = 28 }: Props) {
  const ref = useRef<HTMLAudioElement | null>(null);
  const [playing, setPlaying] = useState(false);

  const toggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!ref.current || !src) return;
    if (playing) { ref.current.pause(); } else { ref.current.play(); }
    setPlaying(!playing);
  };

  if (!src) return null;

  return (
    <>
      <audio
        ref={ref}
        src={src}
        onEnded={() => setPlaying(false)}
        onPause={() => setPlaying(false)}
        preload="none"
      />
      <button
        className={`card-play-btn${playing ? " playing" : ""}`}
        style={{ width: size, height: size, minWidth: size }}
        onClick={toggle}
        title={playing ? "Pause" : "Play"}
      >
        {playing ? <MdPause size={size * 0.55} /> : <MdPlayArrow size={size * 0.55} />}
      </button>
    </>
  );
}
