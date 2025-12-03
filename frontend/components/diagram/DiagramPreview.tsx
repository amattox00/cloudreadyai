import React, { useEffect, useRef } from "react";

interface DiagramPreviewProps {
  xml: string;
  height?: number;
}

/**
 * Draw.io (diagrams.net) iframe preview.
 * Uses the JSON postMessage protocol to push XML into the embedded editor.
 */
export const DiagramPreview: React.FC<DiagramPreviewProps> = ({
  xml,
  height = 600,
}) => {
  const iframeRef = useRef<HTMLIFrameElement | null>(null);

  useEffect(() => {
    const iframe = iframeRef.current;
    if (!iframe) return;

    const handleMessage = (event: MessageEvent) => {
      if (event.source !== iframe.contentWindow) return;

      try {
        // Helpful for debugging in the browser console
        // eslint-disable-next-line no-console
        console.log("draw.io message:", event.data);
      } catch {
        /* ignore */
      }

      // draw.io sometimes sends "ready" as a simple string,
      // or an object like { event: "init" } when using proto=json.
      let isReady = false;

      if (typeof event.data === "string") {
        if (event.data === "ready") {
          isReady = true;
        } else {
          try {
            const parsed = JSON.parse(event.data);
            if (parsed?.event === "init") {
              isReady = true;
            }
          } catch {
            /* not JSON, ignore */
          }
        }
      } else if (typeof event.data === "object" && event.data !== null) {
        if ((event.data as any).event === "init") {
          isReady = true;
        }
      }

      if (isReady) {
        const msg = {
          action: "load",
          autosize: 1,
          xml,
        };
        iframe.contentWindow?.postMessage(JSON.stringify(msg), "*");
      }
    };

    window.addEventListener("message", handleMessage);

    // Fallback: if we somehow never see the ready/init event,
    // still try posting after a short delay.
    const timer = window.setTimeout(() => {
      const msg = {
        action: "load",
        autosize: 1,
        xml,
      };
      iframe.contentWindow?.postMessage(JSON.stringify(msg), "*");
    }, 1500);

    return () => {
      window.removeEventListener("message", handleMessage);
      window.clearTimeout(timer);
    };
  }, [xml]);

  const drawIoUrl =
    "https://embed.diagrams.net/?embed=1&ui=min&spin=1&proto=json&noSaveBtn=1&noExitBtn=1";

  return (
    <iframe
      ref={iframeRef}
      src={drawIoUrl}
      style={{ width: "100%", border: "1px solid #ccc", height }}
      aria-label="Diagram preview"
    />
  );
};
