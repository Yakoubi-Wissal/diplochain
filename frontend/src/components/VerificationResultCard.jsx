import React from "react";

export default function VerificationResultCard({ data }) {
  if (!data) return null;
  const { status } = data;
  const color =
    status === "VERIFIED" ? "green" :
    status === "REVOKED" ? "orange" :
    status === "INVALID" ? "red" :
    "gray";

  return (
    <div style={{ border:`2px solid ${color}`, padding:20, marginTop:20, borderRadius:8 }}>
      <h2 style={{ color }}>{status}</h2>
      <div><strong>Diploma ID:</strong> {data.diploma_id}</div>
      <div><strong>Student:</strong> {data.student}</div>
      <div><strong>University:</strong> {data.university}</div>
      <div><strong>Degree:</strong> {data.degree}</div>
      <div><strong>Field of study:</strong> {data.field_of_study}</div>
      <div><strong>Issue date:</strong> {data.issue_date}</div>
      <div>
        <strong>Blockchain hash:</strong>{" "}
        <span style={{ fontFamily: "monospace", wordBreak: "break-all" }}>
          {data.blockchain_hash}
        </span>
      </div>
    </div>
  );
}