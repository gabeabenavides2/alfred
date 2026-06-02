"use client";

import { FormEvent, useMemo, useState } from "react";

type Message = {
  role: "assistant" | "user";
  content: string;
};

const starterPrompts = [
  "Build tonight's mission plan and priorities.",
  "Turn a rough idea into a clean operation checklist.",
  "Draft a polished message in Alfred's voice.",
];

const initialMessages: Message[] = [
  {
    role: "assistant",
    content:
      "Good evening. I am Alfred. Bring me the clutter, the unfinished plan, or the urgent task, and I will help you turn it into order.",
  },
  {
    role: "assistant",
    content:
      "This interface is presently in preview mode, so I am not calling the backend just yet. The command desk is ready for that next step.",
  },
];

function buildPreviewResponse(message: string) {
  const trimmed = message.trim();

  if (!trimmed) {
    return "Give me a little direction and I’ll help you organize the next step.";
  }

  return `Preview mode note: if you send "${trimmed.length > 72 ? `${trimmed.slice(0, 72)}...` : trimmed}" to Alfred, the backend can turn this screen into a real chat workflow. The UI is ready for message history, quick prompts, and a focused workspace.`;
}

export default function Home() {
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState<Message[]>(initialMessages);

  const totalMessages = useMemo(() => messages.length, [messages]);

  function submitMessage(nextMessage: string) {
    const trimmed = nextMessage.trim();
    if (!trimmed) return;

    setMessages((current) => [
      ...current,
      { role: "user", content: trimmed },
      { role: "assistant", content: buildPreviewResponse(trimmed) },
    ]);
    setDraft("");
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    submitMessage(draft);
  }

  return (
    <main className="min-h-screen px-4 py-6 text-foreground sm:px-6 lg:px-8">
      <div className="alfred-shell mx-auto grid min-h-[calc(100vh-3rem)] w-full max-w-7xl overflow-hidden rounded-[2rem] border border-line lg:grid-cols-[320px_minmax(0,1fr)]">
        <aside className="border-b border-line p-6 lg:border-r lg:border-b-0 lg:p-8">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-medium uppercase tracking-[0.32em] text-accent">
                Alfred
              </p>
              <h1 className="mt-3 font-serif text-4xl leading-none sm:text-5xl">
                The butler for your midnight shift.
              </h1>
            </div>
            <div className="rounded-full border border-accent/30 bg-accent-soft px-3 py-1 text-xs text-accent">
              Gotham Mode
            </div>
          </div>

          <p className="mt-6 max-w-sm text-sm leading-7 text-muted">
            A darker command room for planning the evening, drafting with polish,
            and turning loose thoughts into decisive action.
          </p>

          <div className="mt-8 grid gap-3">
            <div className="alfred-panel rounded-3xl p-4">
              <p className="text-xs uppercase tracking-[0.22em] text-muted">
                Session
              </p>
              <p className="mt-2 text-2xl font-semibold text-accent">{totalMessages}</p>
              <p className="mt-1 text-sm text-muted">Signals in the current briefing</p>
            </div>
            <div className="alfred-panel rounded-3xl p-4">
              <p className="text-xs uppercase tracking-[0.22em] text-muted">
                Best for
              </p>
              <ul className="mt-3 space-y-2 text-sm text-foreground/88">
                <li>Nightly planning and prioritization</li>
                <li>Polished drafts, replies, and briefings</li>
                <li>Turning ideas into tactical next steps</li>
              </ul>
            </div>
          </div>

          <div className="mt-8">
            <p className="text-xs uppercase tracking-[0.22em] text-muted">
              Try asking
            </p>
            <div className="mt-4 flex flex-col gap-3">
              {starterPrompts.map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  onClick={() => submitMessage(prompt)}
                  className="alfred-panel rounded-2xl px-4 py-3 text-left text-sm leading-6 transition-transform duration-150 hover:-translate-y-0.5 hover:border-accent"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        </aside>

        <section className="alfred-grid flex min-h-[70vh] flex-col p-4 sm:p-6 lg:p-8">
          <div className="alfred-panel flex items-center justify-between rounded-[1.75rem] px-5 py-4">
            <div>
              <p className="text-sm font-medium">Command Desk</p>
              <p className="text-sm text-muted">
                Personal butler interface with a conversation-first layout
              </p>
            </div>
            <div className="rounded-full border border-accent/30 bg-accent-soft px-3 py-1 text-xs font-medium text-accent">
              Systems Standby
            </div>
          </div>

          <div className="mt-4 flex-1 space-y-4 overflow-hidden rounded-[1.75rem] border border-line bg-black/20 p-4 sm:p-5">
            <div className="flex h-full flex-col gap-4 overflow-y-auto pr-1">
              {messages.map((message, index) => (
                <article
                  key={`${message.role}-${index}`}
                  className={`max-w-2xl rounded-[1.5rem] px-5 py-4 shadow-sm ${
                    message.role === "assistant"
                      ? "border border-line bg-card-strong text-foreground"
                      : "ml-auto border border-accent/50 bg-accent text-black"
                  }`}
                >
                  <p className="mb-2 text-xs font-medium uppercase tracking-[0.2em] opacity-70">
                    {message.role === "assistant" ? "Alfred" : "You"}
                  </p>
                  <p className="text-sm leading-7">{message.content}</p>
                </article>
              ))}
            </div>
          </div>

          <form onSubmit={handleSubmit} className="mt-4">
            <div className="alfred-panel rounded-[1.75rem] p-3">
              <label htmlFor="alfred-message" className="sr-only">
                Message Alfred
              </label>
              <textarea
                id="alfred-message"
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                placeholder="What needs attention tonight, sir?"
                className="min-h-28 w-full resize-none rounded-[1.25rem] border border-transparent bg-transparent px-3 py-3 text-sm leading-7 text-foreground outline-none placeholder:text-muted"
              />
              <div className="flex flex-col gap-3 border-t border-line px-2 pt-3 sm:flex-row sm:items-center sm:justify-between">
                <p className="text-sm text-muted">
                  Begin with one task, one concern, or one unfinished plan.
                </p>
                <button
                  type="submit"
                  className="rounded-full bg-accent px-5 py-3 text-sm font-medium text-black transition-transform duration-150 hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-50"
                  disabled={!draft.trim()}
                >
                  Send to Alfred
                </button>
              </div>
            </div>
          </form>
        </section>
      </div>
    </main>
  );
}
