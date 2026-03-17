import React from "react";
import { QrReader } from "react-qr-reader";

// simple wrapper around react-qr-reader
// calls onScan(text) when a code is successfully read
export default function QRCodeScanner({ onScan }) {
  return (
    <div style={{ marginTop:20 }}>
      <h3>Scan QR code</h3>
      <div style={{ maxWidth:400, margin:"0 auto" }}>
        <QrReader
          constraints={{ facingMode: "environment" }}
          onResult={(result, error) => {
            if (result) {
              const text = result?.text || result;
              if (text) onScan(text);
            }
            // ignore errors for now
          }}
          style={{ width: "100%" }}
        />
      </div>
    </div>
  );
}