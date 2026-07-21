import { MdClose, MdAudiotrack } from "react-icons/md";
import AudioPlayerMini from "./AudioPlayerMini";
import ImageThumbnail from "./ImageThumbnail";
import VideoThumbnail from "./VideoThumbnail";

interface Props {
  type: "audio" | "image" | "video";
  title: string;
  fileUrl: string | null;
  onRemove?: () => void;
}

export default function MediaPreviewCard({ type, title, fileUrl, onRemove }: Props) {
  return (
    <div className="media-preview-card">
      <div className="media-preview-thumb">
        {type === "audio" && (
          <div className="d-flex align-items-center justify-content-center h-100" style={{ background: "var(--surface-2)", borderRadius: "8px 8px 0 0" }}>
            <AudioPlayerMini src={fileUrl} size={36} />
            {!fileUrl && <MdAudiotrack size={24} style={{ color: "var(--muted)", opacity: 0.4 }} />}
          </div>
        )}
        {type === "image" && <ImageThumbnail src={fileUrl} alt={title} height={100} />}
        {type === "video" && <VideoThumbnail src={fileUrl} height={100} />}
      </div>
      <div className="media-preview-info">
        <span className="media-preview-title" title={title}>{title}</span>
      </div>
      {onRemove && (
        <button
          className="media-preview-remove"
          onClick={(e) => { e.stopPropagation(); onRemove(); }}
          title="Remove"
        >
          <MdClose size={14} />
        </button>
      )}
    </div>
  );
}
