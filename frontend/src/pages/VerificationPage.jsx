import React, { useState } from "react";
import { fetchVerification } from "../api/apiService";
import QRCodeScanner from "../components/QRCodeScanner";
import VerificationResultCard from "../components/VerificationResultCard";

export default function VerificationPage() {
  const [identifier, setIdentifier] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const doVerify = async id => {
    if (!id) return;
    // if the scanned value is a full URL, pull the identifier
    let identifier = id;
    try {
      const url = new URL(id);
      if (url.pathname.startsWith("/verify/")) {
        identifier = url.pathname.split("/").pop();
      }
    } catch (_) {
      // not a URL
    }

    setError("");
    try {
      const res = await fetchVerification(identifier);
      setResult(res);
    } catch (e) {
      setError(e.message || "Verification failed");
      setResult(null);
    }
  };

  return (
    <div style={{ padding:20, maxWidth:600, margin:"0 auto" }}>
      <h1>Diploma Verification</h1>

      <div style={{ display:"flex", gap:8, marginBottom:12 }}>
        <input
          value={identifier}
          onChange={e=>setIdentifier(e.target.value)}
          placeholder="Enter diploma ID or scan QR code"
          style={{ flex:1, padding:6, borderRadius:4, border:`1px solid #444` }}
        />
        <button onClick={()=>doVerify(identifier)} style={{ padding:6 }}>Verify</button>
      </div>

      <QRCodeScanner onScan={doVerify} />

      {error && <div style={{ color:"red", marginTop:12 }}>{error}</div>}

      {result && <VerificationResultCard data={result} />}
    </div>
  );
}