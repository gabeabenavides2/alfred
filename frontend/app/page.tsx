"use client";

import { FormEvent, useState } from "react";

export default function Home() {
  const [draft, setDraft] = useState("");
  const [response, setResponse] = useState("");

  async function submitMessage(nextMessage: string) {
    const trimmed = nextMessage.trim();
    if (!trimmed) return;

    const res = await fetch("http://localhost:8080/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: trimmed,
      }),
    });
    const data = await res.json();
    setResponse(data.response);
    setDraft("");
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    submitMessage(draft);
  }

  return (
    <main className="h-screen w-full max-w-4xl mx-auto p-4 flex flex-col">
      <h1 className="text-center text-3xl font-bold mb-4">Alfred</h1>

      <div className="flex-1 border rounded-md p-4 mb-4 overflow-auto">
        <h2 className="text-xl font-semibold mb-2">Response</h2>
        <p>{response}</p>
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
      <textarea
        id="alfred-message"
        value={draft}
        onChange={(event) => setDraft(event.target.value)}
        className="flex-1 border rounded-md p-3 min-h-24"
      />
      <button
        type="submit"
        disabled={!draft.trim()}
        className="border rounded-md px-4 py-2"
      >
        Submit
      </button>
      </form>
    </main>
  );
}
