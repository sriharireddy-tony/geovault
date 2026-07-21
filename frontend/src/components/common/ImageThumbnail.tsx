import { useState } from "react";
import { Modal } from "react-bootstrap";
import { MdImage } from "react-icons/md";

interface Props {
  src: string | null;
  alt?: string;
  height?: number;
}

export default function ImageThumbnail({ src, alt = "Image", height = 80 }: Props) {
  const [showZoom, setShowZoom] = useState(false);

  if (!src) {
    return (
      <div
        className="d-flex align-items-center justify-content-center"
        style={{ height, background: "var(--surface-2)", borderRadius: 8, color: "var(--muted)" }}
      >
        <MdImage size={24} style={{ opacity: 0.4 }} />
      </div>
    );
  }

  return (
    <>
      <img
        src={src}
        alt={alt}
        onClick={(e) => { e.stopPropagation(); setShowZoom(true); }}
        style={{
          height, width: "100%", objectFit: "cover", borderRadius: 8, cursor: "zoom-in",
        }}
      />
      <Modal show={showZoom} onHide={() => setShowZoom(false)} centered size="lg">
        <Modal.Body className="p-0" style={{ background: "#000" }}>
          <img src={src} alt={alt} className="w-100" style={{ maxHeight: "80vh", objectFit: "contain" }} />
        </Modal.Body>
      </Modal>
    </>
  );
}
